from pymongo import ASCENDING, MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

def connect_with_database():
    connection = MongoClient(os.getenv("DATABASE_URL"))
    db = connection[os.getenv("DATABASE")]
    collection = db[os.getenv("COLLECTION")]
    return collection

def connect_with_master_database():
    connection = MongoClient(os.getenv("DATABASE_URL"))
    db = connection[os.getenv("DATABASE")]
    collection = db[os.getenv("MASTER_COLLECTION")]
    collection.create_index(
        [
            ("Description", ASCENDING),
            ("DisplayName", ASCENDING)
        ]
    )
    return collection
