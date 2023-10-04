from SimpleQIWI import *

from config import token, phone

api = QApi(token=token, phone=phone)
print(api.balance)

