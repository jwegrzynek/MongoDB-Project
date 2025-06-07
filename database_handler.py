from pymongo import MongoClient
from pymongo.server_api import ServerApi
from typing import Union,Optional
from bson import ObjectId
import pprint
from typing import List
from datetime import datetime, timedelta


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
            print("Connected to MongoDB")
        except Exception as e:
            print("Failed to connect to MongoDB:", e)
            self.client = None
            self.db = None
            self.collection = None


   # CRUD - Create
    def create_pet(self, pet_data: dict) -> Optional[dict]:
        """
        Tworzy nowy dokument w kolekcji z danymi 'pet_data'.
        Zwraca wstawiony dokument z nadanym id lub None w przypadku błędu.
        """
        if self.collection is None:
            print("No connection to the collection.")
            return None

        result = self.collection.insert_one(pet_data)
        if result.inserted_id:
            new_doc = self.collection.find_one({"_id": result.inserted_id})
            print("Document created:")
            pprint.pprint(new_doc)
            return new_doc
        else:
            print("Failed to insert document.")
            return None

    # CRUD - Read
    def read_pets(self, query: dict = {}) -> List[dict]:
        """
        Zwraca listę dokumentów spełniających warunek 'query'.
        Jeśli query jest puste, zwraca wszystkie dokumenty.
        """
        if self.collection is None:
            print("No connection to the collection.")
            return []

        results = list(self.collection.find(query))
        if results:
            print(f"Found {len(results)} document(s):")
            for doc in results:
                pprint.pprint(doc)
        else:
            print("No documents found.")
        return results


    #


    # CRUD - Update
    def update_pet(self, query: dict, new_values: dict) -> Optional[dict]:
        """
        Aktualizuje jeden dokument spełniający warunek 'query' nowymi wartościami 'new_values'.
        Zwraca zaktualizowany dokument lub None, jeśli nie znaleziono.
        """
        if self.collection is None:
            print("No connection to the collection.")
            return None

        result = self.collection.update_one(query, {"$set": new_values})
        if result.modified_count == 1:
            updated_doc = self.collection.find_one(query)
            print("Document updated:")
            pprint.pprint(updated_doc)
            return updated_doc
        else:
            print("No document updated.")
            return None

    # CRUD - Delete
    def delete_pet(self, query: dict) -> Optional[dict]:
        """
        Usuwa jeden dokument spełniający warunek 'query'.
        Zwraca usunięty dokument lub None, jeśli nie znaleziono.
        """
        if self.collection is None:
            print("No connection to the collection.")
            return None

        deleted_doc = self.collection.find_one_and_delete(query)
        if deleted_doc:
            print("Document deleted:")
            pprint.pprint(deleted_doc)
            return deleted_doc
        else:
            print("No matching document found to delete.")
            return None

    # Szukamy wolnych zwierząt do adopcji
    def find_available_pets(self) -> list:
        """
        Zwraca listę wszystkich wolnych zwierząt do adopcji (np. adopted=False).
        """
        if self.collection is None:
            print("No connection to the collection.")
            return []

        # Zakładamy, że pole 'adopted' oznacza czy zwierzę zostało adoptowane
        available_pets = list(self.collection.find({"adoption.adopted": False}))
        if available_pets:
            print(f"Found {len(available_pets)} available pets:")
            for pet in available_pets:
                pprint.pprint(pet)
        else:
            print("No available pets found.")
        return available_pets

    # Wyszukiwanie zwierząt do wybranej kwoty
    def find_pets_by_fee(self, max_fee: int) -> list:
        """
        Zwraca listę zwierząt, których opłata adopcyjna nie przekracza podanej kwoty.
        """
        if self.collection is None:
            print("No connection to the collection.")
            return []
        pets = list(self.collection.find({"fee": {"$lte": max_fee}}))
        return pets


    # Do ulepszenia - użyć powyższych funkcji
    def find_pets_to_adoption(self, pet_type: str, max_age: int, available: bool, max_fee: int) -> list:
        """
        Zwraca listę zwierząt danego typu, młodszych niż max_age i dostępnych do adopcji.
        """
        if self.collection is None:
            print("No connection to the collection.")
            return []
        query = {
            "type": pet_type,
            "age": {"$lt": max_age},
            "adoption.adopted": False, # lub "available": available, zależnie od schematu
            "fee": {"$lte": max_fee}
        }
        pets = list(self.collection.find(query))
        return pets


    # metoda Weroniki
    def find_pets_by_description(self, keywords: list[str]) -> list:

        """
        Zwraca listę dostępnych zwierząt do adopcji, których opis zawiera dowolne z podanych słów kluczowych.
        """

        if self.collection is None:
            print("No connection to the collection.")
            return []

        # Tworzymy zapytanie z wyrażeniem regularnym na słowa kluczowe (case-insensitive)
        conditions = [{"description": {"$regex": word, "$options": "i"}} for word in keywords]

        query = {
            "adoption.adopted": False,
            "$or": conditions
        }

        pets = list(self.collection.find(query))

        if pets:
            print(f"Found {len(pets)} matching pets:")
            for pet in pets:
                pprint.pprint(pet)
        else:
            print("No available pets found.")

        return pets

    #


    def get_pets_by_age(
        self,
        order: str,
        n: int = 1,
        adopted: Optional[bool] = None
    ) -> List[dict]:

        """
        Zwraca listę n zwierząt o najmniejszym lub największym wieku.

        Args:
        order (str): Wymagany. "youngest" - najmłodsze, "oldest" - najstarsze.
        n (int): liczba zwierząt do zwrócenia (domyślnie 1).
        """

        allowed_orders = ["youngest", "oldest"]
        if order not in allowed_orders:
            raise ValueError(f"The 'order' argument must be one of: {allowed_orders}")

        if self.collection is None:
            print("No connection to the collection.")
            return []

        sort_order = 1 if order == "youngest" else -1

        query = {}
        if adopted is True:
            query["adoption.adopted"] = True
        elif adopted is False:
            query["adoption.adopted"] = False

        pets = list(self.collection.find(query).sort("age", sort_order).limit(n))

        if pets:
            print(f"Found {len(pets)} pets ({order})", end='')
        if adopted is True:
            print(" that are adopted:")
        elif adopted is False:
            print(" that are not adopted:")
        else:
            print(":")
        for pet in pets:
            pprint.pprint(pet)
        else:
            print("No pets found in the collection matching the criteria.")

        return pets

    def get_pets_by_shelter_stay(
        self,
        stay_type: str,
        n: int = 1,
        threshold_months: Optional[int] = None,
        comparison: Optional[str] = None
    ) -> List[dict]:
        """
        Returns a list of pets filtered and sorted by shelter stay duration.

        Args:
            stay_type (str): "longest" or "shortest" — sort order.
            n (int): number of records to return.
            threshold_months (int, optional): threshold in months for filtering.
            comparison (str, optional): "longer" or "shorter" — filter pets
                                        with daysInShelter longer/shorter than threshold_months.

        """
        allowed_stay_types = ["longest", "shortest"]
        allowed_comparisons = ["longer", "shorter", None]

        if stay_type not in allowed_stay_types:
            raise ValueError(f"'stay_type' must be one of {allowed_stay_types}")
        if comparison not in allowed_comparisons:
            raise ValueError(f"'comparison' must be one of {allowed_comparisons}")

        if self.collection is None:
            print("No connection to the collection.")
            return []

        sort_order = -1 if stay_type == "longest" else 1

        # Budujemy zapytanie
        query = {"adoption.daysInShelter": {"$exists": True, "$ne": None}}

        if comparison in ["longer", "shorter"] and threshold_months is not None:
            threshold_days = threshold_months * 30  # approx. days
            if comparison == "longer":
                query["adoption.daysInShelter"]["$gt"] = threshold_days
            else:  # comparison == "shorter"
                query["adoption.daysInShelter"]["$lt"] = threshold_days

        # Pobieramy dokumenty
        pets = list(self.collection.find(query).sort("adoption.daysInShelter", sort_order).limit(n))

        if pets:
            print(f"Found {len(pets)} pet(s) sorted by {stay_type} stay in shelter.")
            if comparison and threshold_months is not None:
                comp_str = "longer than" if comparison == "longer" else "shorter than"
                print(f"Filtered pets with stay {comp_str} {threshold_months} month(s).")

            for pet in pets:
                days = pet.get("adoption", {}).get("daysInShelter", "unknown")
                print(f"Stay duration: {days} days")
                pprint.pprint(pet)
        else:
            print("No pets found matching the criteria.")

        return pets


    def ready_for_adoption(self) -> List[dict]:
        """
        Prints pets ready for adoption:
        - not adopted,
        - vaccinated,
        - healthy (no injuries),
        - sterilized,
        - dewormed.
        """

        if self.collection is None:
            print("No connection to the collection.")
            return []

        query = {
            "adoption.adopted": False,
            "medical.vaccinated": "Yes",
            "medical.health": "Healthy",
            "medical.sterilized": "Yes",
            "medical.dewormed": "Yes"
        }

        pets = list(self.collection.find(query))

        if pets:
            print(f"Found {len(pets)} pet(s) ready for adoption:")
            for pet in pets:
                pprint.pprint(pet)
        else:
            print("No pets ready for adoption found.")

        return pets

    def is_ready_for_adoption(self, pet_id: Union[str, ObjectId]) -> Optional[bool]:
        """
        Checks if the pet with the given id is ready for adoption.

        Ready means:
        - not adopted
        - vaccinated == "Yes"
        - dewormed == "Yes"
        - sterilized == "Yes"
        - health == "Healthy"

        Args:
            pet_id (str or ObjectId): the _id of the pet.

        Returns:
            bool: True if ready, False if not ready, None if pet not found or error.
        """
        if self.collection is None:
            print("No connection to the collection.")
            return None

        try:
            oid = pet_id if isinstance(pet_id, ObjectId) else ObjectId(pet_id)
            pet = self.collection.find_one({"_id": oid})

            if pet is None:
                print(f"No pet found with id {pet_id}")
                return None

            name = pet.get("name") or "Unnamed"
            adoption = pet.get("adoption", {})
            medical = pet.get("medical", {})

            is_ready = (
                adoption.get("adopted") is False and
                medical.get("vaccinated") == "Yes" and
                medical.get("dewormed") == "Yes" and
                medical.get("sterilized") == "Yes" and
                medical.get("health") == "Healthy"
            )

            if is_ready:
                print(f"Pet '{name}' (id: {pet_id}) is READY for adoption.")
            else:
                print(f"Pet '{name}' (id: {pet_id}) is NOT ready for adoption.")

            return is_ready

        except Exception as e:
            print(f"Error checking adoption readiness: {e}")
            return None

