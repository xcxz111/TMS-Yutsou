from peewee import *
from datetime import datetime


db = SqliteDatabase('database_market.db')


class BaseModel(Model):
    class Meta:
        database = db


class Users(BaseModel):
    UserID = IntegerField(primary_key=True)
    UserName = CharField(null=True)
    UserBalance = FloatField(default=0.0)
    Purchases = IntegerField(default=0)
    LastGetProduct = IntegerField(default=0)


class Categories(BaseModel):
    FormatName = CharField()
    CountryName = CharField()
    Price = FloatField()


class Products(BaseModel):
    ProductID = CharField(primary_key=True)
    FileName = CharField()
    UserID = IntegerField(default=-1)
    Category = ForeignKeyField(Categories, backref='products')
    ProductFormat = CharField()
    ProductCountry = CharField()
    ProductPrice = FloatField()
    ProductStatus = CharField()
    AddProductTime = DateTimeField(default=datetime.now())
    SellProductTime = DateTimeField()


class Transactions(BaseModel):
    ID = IntegerField(primary_key=True)
    UserID = IntegerField()
    Method = CharField()
    Comment = CharField()
    Summ = FloatField()
    Time = DateTimeField(default=datetime.now())


def init_database():
    global db
    db.create_tables([Users, Categories, Products, Transactions])
    return db
