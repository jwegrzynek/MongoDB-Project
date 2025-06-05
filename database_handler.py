from pymongo import MongoClient
from pymongo.server_api import ServerApi
from typing import Optional
import pprint
from typing import List


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




    # CRUD - Update
    def update_pet(self, query: dict, new_values: dict) -> Optional[dict]:
        """
        Aktualizuje jeden dokument spełniający warunek 'query' nowymi wartościami 'new_values'.
        Zwraca zaktualizowany dokument lub None, jeśli nie znaleziono.
        """
        if self.collection is None:
            print("⚠️ No connection to the collection.")
            return None

        result = self.collection.update_one(query, {"$set": new_values})
        if result.modified_count == 1:
            updated_doc = self.collection.find_one(query)
            print("✅ Document updated:")
            pprint.pprint(updated_doc)
            return updated_doc
        else:
            print("⚠️ No document updated.")
            return None

    # CRUD - Delete
    def delete_pet(self, query: dict) -> Optional[dict]:
        """
        Usuwa jeden dokument spełniający warunek 'query'.
        Zwraca usunięty dokument lub None, jeśli nie znaleziono.
        """
        if self.collection is None:
            print("⚠️ No connection to the collection.")
            return None

        deleted_doc = self.collection.find_one_and_delete(query)
        if deleted_doc:
            print("🗑️ Document deleted:")
            pprint.pprint(deleted_doc)
            return deleted_doc
        else:
            print("⚠️ No matching document found to delete.")
            return None

    # Szukamy wolnych zwierząt do adopcji
    def find_available_pets(self) -> list:
        """
        Zwraca listę wszystkich wolnych zwierząt do adopcji (np. adopted=False).
        """
        if self.collection is None:
            print("⚠️ No connection to the collection.")
            return []

        # Zakładamy, że pole 'adopted' oznacza, czy zwierzę zostało adoptowane
        available_pets = list(self.collection.find({"adoption.adopted": False}))
        if available_pets:
            print(f"✅ Found {len(available_pets)} available pets:")
            for pet in available_pets:
                pprint.pprint(pet)
        else:
            print("⚠️ No available pets found.")
        return available_pets

    # Wyszukiwanie zwierząt do wybranej kwoty
    def find_pets_by_fee(self, max_fee: int) -> list:
        """
        Zwraca listę zwierząt, których opłata adopcyjna nie przekracza podanej kwoty.
        """
        if self.collection is None:
            print("⚠️ No connection to the collection.")
            return []
        pets = list(self.collection.find({"fee": {"$lte": max_fee}}))
        return pets


    # Do ulepszenia - użyć powyższych funkcji
    def find_pets_to_adoption(self, pet_type: str, max_age: int, available: bool, max_fee: int) -> list:
        """
        Zwraca listę zwierząt danego typu, młodszych niż max_age i dostępnych do adopcji.
        """
        if self.collection is None:
            print("⚠️ No connection to the collection.")
            return []
        query = {
            "type": pet_type,
            "age": {"$lt": max_age},
            "adoption.adopted": False, # lub "available": available, zależnie od schematu
            "fee": {"$lte": max_fee}
        }
        pets = list(self.collection.find(query))
        return pets