from pymongo import MongoClient
from pymongo.server_api import ServerApi
from typing import Optional
import pprint


class PetAdoptionDatabase:
    def __init__(self, uri: str, db_name: str = "petsDB", collection_name: str = "petsInformation"):
        self.uri = uri
        self.db_name = db_name
        self.collection_name = collection_name

        try:
            self.client = MongoClient(self.uri, server_api=ServerApi('1'))
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            # test connection
            self.client.admin.command('ping')
            print("✅ Connected to MongoDB")
        except Exception as e:
            print("❌ Failed to connect to MongoDB:", e)
            self.client = None
            self.db = None
            self.collection = None

    def find_one_pet(self, query: Optional[dict] = None) -> Optional[dict]:
        """
        Zwraca jeden dokument z kolekcji, spełniający opcjonalny warunek.
        Jeśli query nie zostanie podany, zwraca pierwszy dostępny dokument.
        """
        if self.collection is None:
            print("⚠️ No connection to the collection.")
            return None

        result = self.collection.find_one(query or {})
        if result:
            pprint.pprint(result)
        else:
            print("⚠️ No matching document found.")
        return result
