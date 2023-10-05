import requests
import time
from config import qiwi_token, qiwi_phone, bot

from models import Users, Transactions


def to_float(s):
    try:
        s = float(s)
    except ValueError:
        s = -1
    finally:
        return s


def check_qiwi_payments():
    headers = {
        'Authorization': f'Bearer {qiwi_token}',
    }

    params = {
        'rows': 20,  # Максимальное количество последних платежей для получения
        'operation': 'IN'  # Только входящие платежи
    }

    transactions = [x.ID for x in list(Transactions.select().execute())]

    try:
        response = requests.get(f'https://edge.qiwi.com/payment-history/v2/persons/{qiwi_phone}/payments', headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        for payment in data['data']:
            if payment["txnId"] in transactions:
                continue

            amount = payment['sum']['amount']
            comment = payment.get('comment', "Нет комментариев")
            user_id = to_float(comment)
            Transactions.create(ID=payment["txnId"], UserID=user_id, Method="qiwi", Comment=comment, Summ=amount)

            user = Users.get_or_none(UserID=user_id)
            if user:
                user.UserBalance += amount
                user.save()
                bot.send_message(user_id, f"Ваш баланс пополнен на сумму {amount} руб")

            print(f"Пополнение на сумму {amount} руб., uid: {user_id}")

    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")


def start_qiwi():
    while True:
        check_qiwi_payments()
        time.sleep(300)

