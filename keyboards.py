from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def home_markup(is_admin=False):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Личный кабинет", callback_data="cabinet"))
    markup.add(InlineKeyboardButton("Пополнить счет", callback_data="billing")),
    markup.add(InlineKeyboardButton("купить Telegram аккаунт", callback_data="buy_tg")),
    markup.add(InlineKeyboardButton("Инструкция", url="https://telegra.ph/Pravila-pokupok-v-magazine-LINCOLN-MARKET-11-25")),
    markup.add(InlineKeyboardButton("Канал", url="https://t.me/tg_selling_market"))

    if is_admin:
        markup.add(InlineKeyboardButton("Админка", callback_data="admin"))
    return markup


def cabinet_markup():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Получить купленные аккаунты", callback_data="my_orders"))
    markup.add(InlineKeyboardButton("Корзина", callback_data="cart"))
    markup.add(InlineKeyboardButton("Пополнить счет", callback_data="billing"))
    markup.add(
        InlineKeyboardButton("🔸 Назад", callback_data="home"),
        InlineKeyboardButton("🔹 Главная", callback_data="home"))
    return markup


def billing_markup():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("пополнить через QIWI", callback_data="qiwi"))
    markup.add(
        InlineKeyboardButton("🔸 Назад", callback_data="home"),
        InlineKeyboardButton("🔹 Главная", callback_data="home"))
    return markup


def qiwi_markup():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("скопировать ID", callback_data="copy_id"))
    markup.add(InlineKeyboardButton("🔹 Главная", callback_data="home"))
    return markup


def main_markup():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("перейти для оплаты", url="qiwi.com/p/79033749003"))
    markup.add(InlineKeyboardButton("🔹 Главная", callback_data="home"))
    return markup

def admin_markup():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("аккаунты", callback_data="add_account")),
    markup.add(InlineKeyboardButton("категории", callback_data="category")),
    markup.add(
        InlineKeyboardButton("🔸 Назад", callback_data="home"),
        InlineKeyboardButton("🔹 Главная", callback_data="home"))
    return markup


def category_markup():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("добавить категории", callback_data="add_categories")),
    markup.add(InlineKeyboardButton("изменить категории", callback_data="edit_categories")),
    markup.add(InlineKeyboardButton("удалить категории", callback_data="del_categories")),

    markup.add(
        InlineKeyboardButton("🔸 Назад", callback_data="admin"),
        InlineKeyboardButton("🔹 Главная", callback_data="home"))
    return markup


def categories_markup(categories, n):
    markup = InlineKeyboardMarkup()
    for category in categories:
        name = " - ".join([category["FormatName"], category["CountryName"], str(category["Price"]) + " RUB"])
        callback_data = f"{n}|{category['id']}"
        markup.add(InlineKeyboardButton(name, callback_data=callback_data))
    markup.add(
        InlineKeyboardButton("🔸 Назад", callback_data="admin"),
        InlineKeyboardButton("🔹 Главная", callback_data="home"))
    return markup


def buy_categories_markup(products):
    markup = InlineKeyboardMarkup()
    categories = []
    for product in products:
        if product.ProductStatus != "sale":
            continue

        if product.Category not in categories:
            name = f"{product.ProductFormat} - {product.ProductCountry} - {product.ProductPrice} RUB"
            markup.add(InlineKeyboardButton(name, callback_data=f"buy_categories|{product.Category.id}"))
            categories.append(product.Category)
    markup.add(
        InlineKeyboardButton("🔸 Назад", callback_data="home"),
        InlineKeyboardButton("🔹 Главная", callback_data="home"))
    return markup


def to_pay_account_markup(cdata):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("купить", callback_data="buy_account"+"|"+cdata))
    markup.add(InlineKeyboardButton("в корзину", callback_data="cart"+"|"+cdata))
    markup.add(
        InlineKeyboardButton("🔸 Назад", callback_data="buy_tg"),
        InlineKeyboardButton("🔹 Главная", callback_data="home"))
    return markup


def my_cart(cdata):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("купить всё", callback_data="buy_in_cart|"+cdata))
    markup.add(InlineKeyboardButton("удалить всё", callback_data="del_in_cart|"+cdata))
    markup.add(
        InlineKeyboardButton("🔸 Назад", callback_data="buy_tg"),
        InlineKeyboardButton("🔹 Главная", callback_data="home")
    )
    return markup


def cart_data_markup(products):
    markup = InlineKeyboardMarkup()
    dates = []
    for product in products:
        date = str(product.SellProductTime.date())
        if date not in dates:
            markup.add(InlineKeyboardButton(date, callback_data="get_accounts|"+date))
            dates.append(date)
    markup.add(
        InlineKeyboardButton("🔸 Назад", callback_data="cabinet"),
        InlineKeyboardButton("🔹 Главная", callback_data="home")
    )
    return markup

