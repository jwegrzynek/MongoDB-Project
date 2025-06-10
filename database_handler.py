import hashlib
import random
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from typing import Optional
import pymongo
from bson import ObjectId
import pprint
from typing import List
from datetime import datetime


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
            print("Connected to MongoDB!\n")
        except Exception as e:
            print("Failed to connect to MongoDB:", e)
            self.client = None
            self.db = None
            self.collection = None

    @staticmethod
    def return_period(days_passed: int):
        if days_passed == 0:
            return "Same Day"
        elif 1 <= days_passed <= 7:
            return "1-7 Days"
        elif 8 <= days_passed <= 30:
            return "8-30 Days"
        elif 31 <= days_passed <= 90:
            return "31-90 Days"
        elif days_passed > 90:
            return "Over 90 Days"
        else:
            return None

    def _get_next_sequence(self):
        counter = self.db.counters.find_one_and_update(
            {"_id": "petID"},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=pymongo.ReturnDocument.AFTER
        )
        return counter["seq"]

    # CRUD - Create
    def create_pet(
            self,
            name: str = None,
            type: str = "Dog",
            age: int = 0,
            breed_primary: str = None,
            breed_secondary: str = None,
            gender: str = "Unknown",
            colors: list = None,
            maturity_size: str = "Unknown",
            fur_length: str = "Unknown",
            vaccinated: str = "Unknown",
            dewormed: str = "Unknown",
            sterilized: str = "Unknown",
            health: str = "Unknown",
            quantity: int = 1,
            fee: int = 0,
            rescuer_id: str = "",
            rescue_date: Optional[datetime] = None,
            description: str = None,
            location: str = "Unknown",
            adopted: bool = False,
            adoption_date: Optional[datetime] = None,
            adoption_period: str = "null",
            days_in_shelter: Optional[int] = None
    ) -> Optional[dict]:
        """
        Creates a new pet document based on the given attributes and inserts it into the database.

        Returns the inserted document or None on failure.
        """
        if self.collection is None:
            print("No connection to the collection.")
            return None

        try:
            pet_data = {
                "_id": self._get_next_sequence(),
                "name": name,
                "type": type,
                "age": age,
                "breed": {
                    "primary": breed_primary,
                    "secondary": breed_secondary
                },
                "gender": gender,
                "colors": colors if colors else [],
                "maturitySize": maturity_size,
                "furLength": fur_length,
                "medical": {
                    "vaccinated": vaccinated,
                    "dewormed": dewormed,
                    "sterilized": sterilized,
                    "health": health
                },
                "quantity": quantity,
                "fee": fee,
                "rescuerId": rescuer_id,
                "rescueDate": rescue_date or datetime.today(),
                "description": description,
                "location": location,
                "adoption": {"adopted": adopted} if adopted is False else {
                    "adopted": adopted,
                    "adoptionDate": adoption_date,
                    "adoptionPeriod": adoption_period,
                    "daysInShelter": days_in_shelter
                }
            }

            result = self.collection.insert_one(pet_data)
            if result.inserted_id:
                new_doc = self.collection.find_one({"_id": result.inserted_id})
                print("Document created:")
                pprint.pprint(new_doc)
                return new_doc
            else:
                print("Failed to insert document.")
                return None

        except Exception as e:
            print(f"Error creating pet: {e}")
            return None

    # CRUD - Read
    def read_pets(self, query: dict = {}) -> List[dict]:
        """
        Returns a list of pet documents matching the given query.
        If no query is provided, returns all documents in the collection.
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

    # CRUD - Update
    def update_pet(self, query: dict, new_values: dict) -> Optional[dict]:
        """
        Updates a single pet document that matches the given query with the provided new values.
        Returns the updated document if the update was successful, or None if no document was updated or found.
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
        Deletes a single pet document that matches the given query.
        Returns the deleted document if found and deleted, or None if no match was found.
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

    def find_pets_for_adoption(self, pet_type: str = "any", max_age: int = -1, max_fee: int = -1,
                               location: str = 'any', maturity_size: str = 'any', fur_length: str = 'any') -> list:
        """
        Returns a list of pets that are available for adoption, filtered by optional criteria.

        Args:
            pet_type (str): Type of pet to search for (e.g., 'Dog', 'Cat'). Use 'any' to ignore this filter.
            max_age (int): Maximum age in months. Use -1 to ignore this filter.
            max_fee (int): Maximum adoption fee. Use -1 to ignore this filter.
            location (str): Location of the pet. Use 'any' to search across all locations.
            maturity_size (str): Maturity size of the pet. Use 'any' to ignore this filter.
            fur_length (str): Length of the pet's fur. Use 'any' to ignore this filter.

        Returns:
            list: A list of matching pet documents, or an empty list if none found.
    """
        if self.collection is None:
            print("No connection to the collection.")
            return []

        query = {"adoption.adopted": False}

        if pet_type.lower() != "any":
            query["type"] = pet_type

        if max_age >= 0:
            query["age"] = {"$lte": max_age}

        if max_fee >= 0:
            query["fee"] = {"$lte": max_fee}

        if location.lower() != "any":
            query["location"] = location

        if maturity_size.lower() != "any":
            query["maturitySize"] = maturity_size

        if fur_length.lower() != "any":
            query["furLength"] = fur_length

        available_pets = list(self.collection.find(query))
        if available_pets:
            print(f"Found {len(available_pets)} available pets.")
            return available_pets
        else:
            print("No available pets found.")
            return []

    def find_pets_by_description(self, keywords: list[str]) -> list:
        """
        Returns a list of pets available for adoption whose descriptions contain any of the provided keywords.

        Args:
            keywords (list[str]): A list of words or phrases to search for in the 'description' field.

        Returns:
            list: A list of matching pet documents, or an empty list if none found.
        """

        if self.collection is None:
            print("No connection to the collection.")
            return []

        # Creating regex for keywords
        conditions = [{"description": {"$regex": word, "$options": "i"}} for word in keywords]

        query = {
            "adoption.adopted": False,
            "$or": conditions
        }

        pets = list(self.collection.find(query))

        if pets:
            print(f"Found {len(pets)} matching pets:")
            return pets
        else:
            print("No available pets found.")
            return []

    def get_pets_by_age(self, order: str, n: int = 1, adopted: Optional[bool] = None) -> List[dict]:
        """
        Returns a list of n pets with the lowest or highest age, depending on the order.

        Args:
            order (str): Required. "youngest" for the youngest pets, "oldest" for the oldest.
            n (int): Number of pets to return (default is 1).
            adopted (bool, optional):
                - True: only return adopted pets,
                - False: only return not adopted pets,
                - None: include all pets regardless of adoption status.

        Returns:
            List[dict]: A list of pet documents sorted by age.
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
        Returns a list of pets filtered and sorted by their duration in the shelter.

        Args:
            stay_type (str): "longest" or "shortest" — determines the sorting order.
            n (int): Number of pets to return.
            threshold_months (int, optional): Threshold value in months for filtering.
            comparison (str, optional):
                "longer" — include pets that stayed longer than the threshold.
                "shorter" — include pets that stayed shorter than the threshold.
                None — no threshold filtering applied.

        Returns:
            List[dict]: List of pet documents sorted by shelter stay duration.
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

        query = {"adoption.daysInShelter": {"$exists": True, "$ne": None}}

        if comparison in ["longer", "shorter"] and threshold_months is not None:
            threshold_days = threshold_months * 30  # approx. days
            if comparison == "longer":
                query["adoption.daysInShelter"]["$gt"] = threshold_days
            else:  # comparison == "shorter"
                query["adoption.daysInShelter"]["$lt"] = threshold_days

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

    def pets_ready_for_adoption(self) -> List[dict]:
        """
        Returns a list of pets that are ready for adoption.

        Criteria:
        - Not adopted
        - Vaccinated
        - Healthy or minor injury (no serious injury or unknown status)
        - Sterilized
        - Dewormed

        Returns:
            List[dict]: List of pets matching the criteria.
        """

        if self.collection is None:
            print("No connection to the collection.")
            return []

        query = {
            "adoption.adopted": False,
            "medical.vaccinated": "Yes",
            "medical.health": {"$in": ["Healthy", "Minor Injury"]},
            "medical.sterilized": "Yes",
            "medical.dewormed": "Yes"
        }

        pets = list(self.collection.find(query))

        if pets:
            print(f"Found {len(pets)} pet(s) ready for adoption:")
        else:
            print("No pets ready for adoption found.")

        return pets

    def is_ready_for_adoption(self, pet_id: int) -> Optional[bool]:
        """
        Checks if the pet with the given ID is ready for adoption.

        A pet is considered ready if:
        - Not adopted
        - Vaccinated == "Yes"
        - Dewormed == "Yes"
        - Sterilized == "Yes"
        - Health is "Healthy" or "Minor Injury"

        Args:
            pet_id (int): The _id of the pet.

        Returns:
            Optional[bool]:
                - True if ready for adoption
                - False if not ready
                - None if pet not found or connection error
        """
        if self.collection is None:
            print("No connection to the collection.")
            return None

        try:
            pet = self.collection.find_one({"_id": pet_id})

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
                    medical.get("health") in ["Healthy", "Minor Injury"]
            )

            if is_ready:
                print(f"Pet '{name}' (id: {pet_id}) is READY for adoption.")
            else:
                print(f"Pet '{name}' (id: {pet_id}) is NOT ready for adoption.")

            return is_ready

        except Exception as e:
            print(f"Error checking adoption readiness: {e}")
            return None

    def prepare_pet_for_adoption(self, pet_id: int) -> Optional[dict]:
        """
        Prepares a pet for adoption by updating its medical status:
        - Sets 'vaccinated', 'dewormed', and 'sterilized' to "Yes"
        - Attempts to improve the pet's health condition probabilistically:
            - "Minor Injury" - 60% chance to become "Healthy"
            - "Unknown" or "Serious Injury" -
                60% chance of becoming "Healthy", 40% chance of changing to "Minor Injury"

        Args:
            pet_id (int): The _id of the pet.

        Returns:
            Optional[dict]: The updated pet document if successful, or None on error.
        """
        if self.collection is None:
            print("No connection to the collection.")
            return None

        try:
            pet = self.collection.find_one({"_id": pet_id})
            if pet is None:
                print(f"No pet found with id {pet_id}")
                return None

            name = pet.get("name") or "Unnamed"
            medical = pet.get("medical", {})
            current_health = medical.get("health")

            if current_health == "Minor Injury":
                new_health = "Healthy" if random.random() < 0.6 else "Minor Injury"
            elif current_health in ["Unknown", "Serious Injury"]:
                roll = random.random()
                if roll < 0.6:
                    new_health = "Healthy"
                else:
                    new_health = "Minor Injury"
            else:
                new_health = current_health

            update_result = self.collection.update_one(
                {"_id": pet_id},
                {
                    "$set": {
                        "medical.vaccinated": "Yes",
                        "medical.dewormed": "Yes",
                        "medical.sterilized": "Yes",
                        "medical.health": new_health
                    }
                }
            )

            if update_result.modified_count > 0:
                updated_pet = self.collection.find_one({"_id": pet_id})
                print(f"Pet '{name}' (id: {pet_id}) has been prepared for adoption.")
                return updated_pet
            else:
                print(f"Pet with id: {pet_id} not modified or found.")
                return pet

        except Exception as e:
            print(f"Error preparing pet for adoption: {e}")
            return None

    def adopt_pet(self, pet_id: int) -> dict:
        """
        Marks the pet as adopted by updating the adoption fields:
        - Sets adopted to True
        - Sets adoptionDate to today
        - Calculates daysInShelter from rescueDate
        - Sets adoptionPeriod based on daysInShelter

        Args:
            pet_id (int): The _id of the pet to adopt.

        Returns:
            dict: Updated pet document if successful, empty dict otherwise.
        """

        if self.collection is None:
            print("No connection to the collection.")
            return {}

        try:
            pet = self.collection.find_one({"_id": pet_id})
            if pet is None:
                print(f"No pet found with id {pet_id}")
                return {}

            if pet.get("adoption", {}).get("adopted", False):
                print(f"Pet with id {pet_id} is already adopted.")
                return {}

            # Update the pet's adoption status
            today = datetime.today().date()
            rescue_date = pet.get("rescueDate").date()
            days_in_shelter = (today - rescue_date).days

            self.collection.update_one(
                {"_id": pet_id},
                {"$set": {
                    "adoption.adopted": True,
                    "adoption.adoptionDate": datetime.today(),
                    "adoption.adoptionPeriod": self.return_period(days_in_shelter),
                    "adoption.daysInShelter": days_in_shelter
                }
                }
            )

            adopted_pet = self.collection.find_one({"_id": pet_id})
            print(f"You adopted pet {adopted_pet.get('name')} (id: {adopted_pet.get('_id')})!!!")
            return adopted_pet

        except Exception as e:
            print(f"Error during adoption process: {e}")
            return {}

    def get_pet_of_the_day(self) -> Optional[dict]:
        """
        Returns the "Pet of the Day" based on the current date.
        Uses a hash of today's date to select a pseudo-random pet consistently for the day.

        Returns:
            dict or None: The selected pet document or None if no pets available or error occurs.
        """
        if self.collection is None:
            print("No connection to the collection.")
            return None

        # Get total count of pets
        count = self.collection.count_documents({})
        if count == 0:
            print("No pets available.")
            return None

        # Index based on date
        today = datetime.now().date().isoformat()  # e.g., '2025-06-10'
        hash_value = int(hashlib.sha256(today.encode()).hexdigest(), 16)
        index = hash_value % count

        pet = self.collection.find().skip(index).limit(1)
        pet_of_the_day = next(pet, None)

        if pet_of_the_day:
            print("Pet of the Day:")
            pprint.pprint(pet_of_the_day)
        else:
            print("Failed to retrieve Pet of the Day.")
        return pet_of_the_day

    def adoption_rescue_stats(
            self,
            adopted: bool = True,
            rescued: bool = False,
            city='all',
            month: int = 0,
            year: int = 0,
            mode: str = "groupby",  # "sum" or "groupby"
            limit: int = 0,
            order: int = -1  # -1 = descending, 1 = ascending
    ) -> Optional[dict]:
        """
        Returns statistics about adopted and/or rescued pets filtered by location and time.

        Args:
            adopted (bool): Include adopted pets statistics (default True).
            rescued (bool): Include rescued pets statistics (default False).
            city (str or list): City name(s) to filter by, or 'all' for no filtering (default 'all').
            month (int): Month number (1-12) to filter by, 0 means no month filtering (default 0).
            year (int): Year to filter by, 0 means current year (default 0). (if month = 0 and year = 0 then filter this month)
            mode (str): "sum" for total count, "groupby" to group counts by location (default "groupby").
            limit (int): Limit the number of groups returned (default 0 = no limit).
            order (int): Sort order of results by count: -1 descending, 1 ascending (default -1).

        Returns:
            dict or None: Statistics dictionary or None if no connection.
        """
        if self.collection is None:
            print("No connection to the collection.")
            return None

        # Time range
        today = datetime.today()
        if month == 0 and year == 0:
            year, month = today.year, today.month
            start = datetime(year, month, 1)
            end = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
        elif month == 0 and year != 0:
            start = datetime(year, 1, 1)
            end = datetime(year + 1, 1, 1)
        elif month != 0 and year != 0:
            start = datetime(year, month, 1)
            end = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
        else:
            print("When month specified, year should be also specified!")
            return None

        # City filter
        if isinstance(city, str) and city.lower() == 'all':
            city_filter = {}
        elif isinstance(city, list):
            city_filter = {"location": {"$in": city}}
        else:
            city_filter = {"location": city}

        results = {}

        # Aggregation pipeline
        def build_pipeline(match_stage):
            pipeline = [
                {"$match": match_stage},
                {"$group": {"_id": "$location", "count": {"$sum": 1}}},
                {"$sort": {"count": order}}
            ]
            if limit > 0:
                pipeline.append({"$limit": limit})
            return pipeline

        # Adopted pets
        if adopted:
            adopted_match = {
                **city_filter,
                "adoption.adopted": True,
                "adoption.adoptionDate": {"$gte": start, "$lt": end}
            }

            if mode == "sum":
                count = self.collection.count_documents(adopted_match)
                results["adopted"] = count
            else:  # groupby
                pipeline = build_pipeline(adopted_match)
                result = self.collection.aggregate(pipeline)
                results["adopted"] = {doc["_id"]: doc["count"] for doc in result}

        # Rescued pets
        if rescued:
            rescued_match = {
                **city_filter,
                "rescueDate": {"$gte": start, "$lt": end}
            }

            if mode == "sum":
                count = self.collection.count_documents(rescued_match)
                results["rescued"] = count
            else:  # groupby
                pipeline = build_pipeline(rescued_match)
                result = self.collection.aggregate(pipeline)
                results["rescued"] = {doc["_id"]: doc["count"] for doc in result}

        return results
