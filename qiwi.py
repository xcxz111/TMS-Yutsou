
from config import token, phone

import requests
import time


def check_qiwi_payments():
    headers = {
        'Authorization': f'Bearer {token}'
    }

    params = {
        'rows': 10,  # Максимальное количество последних платежей для получения
        'operation': 'IN'  # Только входящие платежи
    }

    try:
        response = requests.get(f'https://edge.qiwi.com/payment-history/v2/persons/{phone}/payments',
                                headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        for payment in data['data']:
            amount = payment['sum']['amount']
            comment = payment.get('comment', 'Нет комментария')
            print(f"Пополнение на сумму {amount} руб., комментарий платежа: {comment}")

    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")


if __name__ == "__main__":
    while True:
        check_qiwi_payments()
        time.sleep(60)

