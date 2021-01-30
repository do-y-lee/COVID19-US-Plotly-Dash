import pymongo
from typing import Dict


class Database:
    URI = "mongodb://127.0.0.1:27017/covid"
    DATABASE = pymongo.MongoClient(URI).get_database()

    @classmethod
    def delete(cls, collection: str):
        cls.DATABASE[collection].remove()

    @classmethod
    def insert(cls, collection: str, data: Dict):
        cls.DATABASE[collection].insert(data)

    @classmethod
    def read_all(cls, collection: str) -> pymongo.cursor:
        return cls.DATABASE[collection].find()

