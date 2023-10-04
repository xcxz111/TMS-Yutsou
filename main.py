import time
import uuid


from datetime import datetime

import pyperclip
from telebot import custom_filters
from telebot.handler_backends import StatesGroup, State
from threading import Thread

from config import bot
from keyboards import home_markup, cabinet_markup, billing_markup, admin_markup, category_markup, categories_markup, \
    buy_categories_markup, to_pay_account_markup, my_cart, cart_data_markup, qiwi_markup, main_markup
from models import Users, Categories, Products, init_database


db = init_database()
admins = [288657881]
temp = {}


class States(StatesGroup):
    format_ = State()
    country = State()
    price = State()
    category = State()
    file = State()
    count = State()


@bot.message_handler(commands=["start"])
def start_message(message):
    global admins
    user = Users.get_or_none(UserID=message.from_user.id)
    if not user:
        print(f"Новый пользователь: {message.from_user.id}")
        Users.create(UserID=message.from_user.id, UserName=message.from_user.username, UserBalance=9999)
        user = Users.get(UserID=message.from_user.id)

    bot.send_message(message.chat.id, f"Здравствуйте {message.from_user.first_name}. \nВаш ID: {message.from_user.id} \nВаш баланс: {user.UserBalance}", reply_markup=home_markup(is_admin=message.from_user.id in admins))


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('home'))
def home_callback(callback):
    global admins
    bot.edit_message_text("Вы попали на главную страницу. Выберите действия:", callback.message.chat.id, callback.message.message_id, reply_markup=home_markup(is_admin=callback.from_user.id in admins))


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('cabinet'))
def cabinet_callback(callback):
    user = Users.get(Users.UserID == callback.from_user.id)
    bot.edit_message_text(f"Ваш баланс: {user.UserBalance} \nПокупок: {user.Purchases}", callback.message.chat.id, callback.message.message_id, reply_markup=cabinet_markup())


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('billing'))
def billing_callback(callback):
    user = Users.get(Users.UserID == callback.from_user.id)
    bot.edit_message_text("выберите метод пополнения счета.", callback.message.chat.id, callback.message.message_id, reply_markup=billing_markup())


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('qiwi'))
def qiwi_callback(callback):
    user_id = callback.from_user.id
    bot.edit_message_text(f"Сделайте перевод на номер QIWI +79033749003 \nПри оплате обязательно укажите в комментарии ваш ID \nВаш ID: <code>{user_id}</code> \nБаланс будет пополнен автоматически в течение нескольких минут.\nНажмите скопировать а после перейдите по ссылке для оплаты", callback.message.chat.id, callback.message.message_id, parse_mode='html', reply_markup=qiwi_markup())


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('copy_id'))
def copy_id_callback(callback):
    user_id = callback.from_user.id
    pyperclip.copy(user_id)
    bot.edit_message_text(f"Ваш ID: <code>{user_id}</code> скопирован в буфер обмена. \nУкажите его в комментарии при оплате!", callback.message.chat.id, callback.message.message_id, parse_mode='html', reply_markup=main_markup())


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('admin'))
def admin_callback(callback):
    if callback.from_user.id not in admins:
        return
    bot.edit_message_text("панель Администратора", callback.message.chat.id, callback.message.message_id, reply_markup=admin_markup())


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('category'))
def category_callback(callback):
    user = Users.get(Users.UserID == callback.from_user.id)
    bot.edit_message_text("Добавьте или удалите категорию", callback.message.chat.id, callback.message.message_id, reply_markup=category_markup())


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('add_categories'))
def add_category_callback(callback):
    bot.set_state(callback.from_user.id, States.format_, callback.message.chat.id)
    bot.edit_message_text("Введите название формата: \nВведите /cancel для выхода", callback.message.chat.id, callback.message.message_id)


@bot.callback_query_handler(func=lambda callback: callback.data.startswith("del_categories"))
def del_categories_callback(callback):
    global admins
    if callback.from_user.id not in admins:
        return

    categories = Categories.select().dicts()
    bot.edit_message_text("Выберите категорию:", callback.message.chat.id, callback.message.message_id, reply_markup=categories_markup(categories, "del_category"))


@bot.callback_query_handler(func=lambda callback: callback.data.startswith("del_category"))
def del_categories_callback(callback):
    global admins
    if callback.from_user.id not in admins:
        return

    data = callback.data.split("|")[1]
    Categories.delete().where(Categories.id == data).execute()
    bot.edit_message_text("Успешно удалено", callback.message.chat.id, callback.message.message_id, reply_markup=admin_markup())


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('add_account'))
def add_account_callback(callback):
    categories = Categories.select().dicts()
    bot.edit_message_text("Выберите категорию:", callback.message.chat.id, callback.message.message_id, reply_markup=categories_markup(categories, "add_file"))


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('add_file'))
def add_file_callback(callback):
    bot.set_state(callback.from_user.id, States.file, callback.message.chat.id)
    with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data:
        data["id"] = callback.data.split("|")[1]
    bot.edit_message_text("Отправьте файл. для выхода введите /cancel", callback.message.chat.id, callback.message.message_id)


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('buy_tg'))
def buy_tg_callback(callback):
    bot.edit_message_text("Выберите категорию товара:", callback.message.chat.id, callback.message.message_id, reply_markup=buy_categories_markup(Products.select()))


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('buy_categories'))
def buy_categories_callback(callback):
    global admins
    category_id = callback.data.split("|")[1]
    category = Categories.get_or_none(Categories.id == category_id)
    if not category:
        bot.edit_message_text("Категория не найдена", callback.message.chat.id, callback.message.message_id, reply_markup=home_markup(is_admin=callback.from_user.id in admins))
        return
    products = list(Products.select().where(Products.ProductStatus == "sale", Products.Category == category).execute())
    bot.set_state(callback.from_user.id, States.count, callback.message.chat.id)
    with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data:
        data["products"] = [i.ProductID for i in products]
    bot.edit_message_text(f"Введите количество товара. В наличии {len(products)}.\nОни бронируются на 1 минуту, никто не сможет их купить до истечения времени. \nдля выхода введите /cancel", callback.message.chat.id, callback.message.message_id)


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('buy_account'))
def buy_tg_callback(callback):
    global admins
    data_id = callback.data.split("|")[1]
    data = temp.pop(data_id, None)
    if not data:
        bot.send_message(callback.message.chat.id, f"Возникла ошибка. Попробуйте еще раз.")
        return
    products = data["products"]
    user = Users.select().where(Users.UserID == callback.from_user.id).get()
    price = data["price"]
    if price > user.UserBalance:
        bot.send_message(callback.message.chat.id, f"Не хватает {abs(user.UserBalance - price)}$", reply_markup=home_markup(is_admin=callback.from_user.id in admins))
        return
    user.UserBalance -= price
    user.Purchases += len(products)
    user.save()
    file_ids = []
    for product in products:
        file_ids.append(product.ProductID)
        product.ProductStatus = "sold"
        product.UserID = user.UserID
        product.SellProductTime = datetime.now()
        product.save()
    for file_id in file_ids:
        bot.send_document(callback.message.chat.id, file_id, visible_file_name=True)
        time.sleep(1)
    bot.send_message(callback.message.chat.id, "Спасибо за покупку!", reply_markup=home_markup(is_admin=callback.from_user.id in admins))


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('cart'))
def cart_callback(callback):
    global admins
    products = list(Products.select().where(Products.ProductStatus == "in_cart", Products.UserID == callback.from_user.id).execute())
    if len(products) == 0:
        bot.edit_message_text("Нет товаров в корзине", callback.message.chat.id, callback.message.message_id, reply_markup=home_markup(is_admin=callback.from_user.id is admins))
        return
    quantity = len(products)
    price = products[0].ProductPrice * quantity
    uid = str(uuid.uuid4())
    temp[uid] = {
        "quantity": quantity,
        "products": products
    }
    bot.edit_message_text(f"Аккаунтов: {quantity}\nЦена: {price}", callback.message.chat.id, callback.message.message_id, reply_markup=my_cart(uid))


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('buy_in_cart'))
def buy_in_cart_callback(callback):
    global admins
    data_id = callback.data.split("|")[1]
    data = temp.pop(data_id, None)
    if not data:
        bot.send_message(callback.message.chat.id, f"Возникла ошибка. Попробуйте еще раз.")
        return
    quantity = data["quantity"]
    products = data["products"][:quantity]
    user = Users.select().where(Users.UserID == callback.from_user.id).get()
    price = products[0].ProductPrice * len(products)
    if price > user.UserBalance:
        bot.send_message(callback.message.chat.id, f"Не хватает {abs(user.UserBalance - price)}$", reply_markup=home_markup(is_admin=callback.from_user.id in admins))
        return
    user.UserBalance -= price
    user.Purchases += len(products)
    user.save()
    file_ids = []
    for product in products:
        file_ids.append(product.ProductID)
        product.ProductStatus = "sold"
        product.UserID = user.UserID
        product.SellProductTime = datetime.now()
        product.save()
    for file_id in file_ids:
        bot.send_document(callback.message.chat.id, file_id, visible_file_name=True)
        time.sleep(1)
    bot.send_message(callback.message.chat.id, "Спасибо за покупку!", reply_markup=home_markup(is_admin=callback.from_user.id in admins))


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('del_in_cart'))
def del_in_cart_callback(callback):
    global admins
    data_id = callback.data.split("|")[1]
    data = temp.pop(data_id, None)
    if not data:
        bot.send_message(callback.message.chat.id, f"Возникла ошибка. Попробуйте еще раз.")
        return
    quantity = data["quantity"]
    products = data["products"][:quantity]
    for product in products:
        product.ProductStatus = "sale"
        product.UserID = -1
        product.save()
    bot.send_message(callback.message.chat.id, "Корзина очищена", reply_markup=home_markup(is_admin=callback.from_user.id is admins))


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('my_orders'))
def my_orders_callback(callback):
    user = Users.select().where(Users.UserID == callback.from_user.id).get()
    if time.time() - user.LastGetProduct < 5 * 60:
        bot.edit_message_text(f"Получить покупки можно раз в 5 минут", callback.message.chat.id, callback.message.message_id)
        return

    user.LastGetProduct = time.time()
    user.save()

    products = list(Products.select().where(Products.ProductStatus == "sold", Products.UserID == callback.from_user.id, (Products.SellProductTime.day - datetime.now().date().day) < 60).execute())

    bot.edit_message_text("Выберите день покупки:", callback.message.chat.id, callback.message.message_id, reply_markup=cart_data_markup(products))


@bot.callback_query_handler(func=lambda callback: callback.data.startswith("get_accounts"))
def get_accounts_callback(callback):
    global admins
    date = callback.data.split("|")[1]
    p = list(Products.select().where(Products.ProductStatus == "sold", Products.UserID == callback.from_user.id).execute())
    products = []
    for i in p:
        if str(i.SellProductTime.date()) == date:
            products.append(i)
    for product in products:
        bot.send_document(callback.message.chat.id, product.ProductID, visible_file_name=True)
        time.sleep(1)
    bot.send_message(callback.message.chat.id, "Готово!", reply_markup=home_markup(is_admin=callback.from_user.id in admins))



""" Обработка состояний """


@bot.message_handler(state="*", commands=["cancel"])
def on_cancel_state(message):
    global admins
    bot.delete_state(message.from_user.id, message.chat.id)
    bot.send_message(message.chat.id, "Состояние удалено", reply_markup=home_markup(is_admin=message.from_user.id in admins))


@bot.message_handler(state=States.format_)
def format_state(message):
    bot.set_state(message.from_user.id, States.country, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["format"] = message.text
    bot.send_message(message.chat.id, "Введите название страны")


@bot.message_handler(state=States.country)
def country_state(message):
    bot.set_state(message.from_user.id, States.price, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["country"] = message.text
    bot.send_message(message.chat.id, "Введите стоимость")


@bot.message_handler(state=States.price)
def create_category(message):
    bot.set_state(message.from_user.id, States.category, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        format_ = data["format"]
        country = data["country"]
        try:
            price = float(message.text)
        except ValueError:
            bot.send_message(message.chat.id, "Это не число. Введите стоимость еще раз:")
            return
    bot.delete_state(message.from_user.id, message.chat.id)
    Categories.create(Id=uuid.uuid4(), FormatName=format_, CountryName=country, Price=price)
    bot.send_message(message.chat.id, "Категория успешно создана", reply_markup=admin_markup())


@bot.message_handler(state=States.file, content_types=["document"])
def file_state(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        category_id = data["id"]
    category = Categories.get(Categories.id == category_id)

    product = Products.create(
            ProductID=message.document.file_id,
            Category=category_id,
            ProductFormat=category.FormatName,
            ProductCountry=category.CountryName,
            ProductPrice=category.Price,
            ProductStatus="sale",
            SellProductTime="None"
    )

    bot.send_message(message.chat.id, "Товар успешно добавлен", reply_markup=admin_markup())


@bot.message_handler(state=States.count)
def count_state(message):
    global admins
    try:
        quantity = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Это не число. Повторите попытку.", reply_markup=buy_categories_markup(Products.select()))
        return

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        products1 = data["products"][:quantity]
    bot.delete_state(message.from_user.id, message.chat.id)
    if quantity < 1 or quantity > len(products1):
        bot.send_message(message.chat.id, "Число указано не верно. Повторите попытку.", reply_markup=buy_categories_markup(Products.select()))
        return

    products2 = list(Products.select().where(Products.ProductStatus == "sale").execute())
    products = list()

    total_price = 0
    for product in products2:
        if product.ProductID in products1:
            products.append(product)
            total_price += product.ProductPrice

    if len(products) == 0:
        bot.send_message(message.chat.id, "Аккаунты не найдены. Возможно их кто-то купил.", reply_markup=buy_categories_markup())
        return

    for product in products:
        product.ProductStatus = "in_cart"
        product.UserID = message.from_user.id
        product.save()

    message_text = (
        f"Ваш выбор:\n"
        f"формат: {products[0].ProductFormat}\n"
        f"страна: {products[0].ProductCountry}\n"
        f"Количество: {quantity}\n"
        f"к оплате: {total_price}$\n"
    )

    uid = str(uuid.uuid4())
    temp[uid] = {
        "products": products,
        "price": total_price
    }

    m = bot.send_message(message.chat.id, message_text, reply_markup=to_pay_account_markup(uid))
    Thread(target=wait_and_delete, args=(products, message, m.message_id, 60)).start()


def wait_and_delete(products, message, mid, t):
    global admins
    time.sleep(t)
    for product in products:
        product_in_db = Products.get(Products.ProductID == product.ProductID)
        if product_in_db.ProductStatus == "in_cart" and product_in_db.UserID == message.from_user.id:
            product.ProductStatus = "sale"
            product.UserID = -1
            product.save()
    bot.edit_message_text("Истекло время", message.chat.id, mid, reply_markup=home_markup(is_admin=message.from_user.id in admins))
    bot.delete_state(message.from_user.id, message.chat.id)




if __name__ == "__main__":
    print("Запуск...")
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.infinity_polling()
