from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from decouple import config


class AsyncDatabase:
    _instances = {}

    def __new__(cls, db_name="meco"):
        if db_name not in cls._instances:
            print(f"Connecting to Mongo: {db_name}")
            instance = super().__new__(cls)
            instance.client = AsyncIOMotorClient(config("MONGO_URL"))
            instance._db = instance.client[db_name]
            cls._instances[db_name] = instance
        return cls._instances[db_name]

    @property
    def db(self):
        return self._db

    @db.setter
    def db(self, new_db):
        self._db = new_db


class SyncDatabase:
    _instances = {}

    def __new__(cls, db_name="meco"):
        if db_name not in cls._instances:
            print(f"Connecting to Mongo: {db_name}")
            instance = super().__new__(cls)
            instance.client = MongoClient(config("MONGO_URL"))
            instance._db = instance.client[db_name]
            cls._instances[db_name] = instance
        return cls._instances[db_name]

    @property
    def db(self):
        return self._db

    @db.setter
    def db(self, new_db):
        self._db = new_db


def get_async_session(db_name="meco"):
    database_instance = AsyncDatabase(db_name)
    return database_instance.db


def get_sync_session(db_name="meco"):
    database_instance = SyncDatabase(db_name)
    return database_instance.db
