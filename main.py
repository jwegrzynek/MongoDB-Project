from database_handler import PetAdoptionDatabase
from datetime import datetime
from bson import ObjectId

if __name__ == "__main__":
    # uri = ("mongodb+srv://dbNonRelProject:project123@projectcluster.u5uvzky.mongodb.net/"
    #        "?retryWrites=true&w=majority&appName=ProjectCluster")
    uri = "mongodb://localhost:27017"
    pet_db = PetAdoptionDatabase(uri=uri)

    print("=================================================")

    # Create new pet document
    pet_db.create_pet(
        name="Luna",
        type="Dog",
        age=4,
        breed_primary="Labrador Retriever",
        gender="Female",
        colors=["Black", "White"],
        maturity_size="Medium",
        fur_length="Short",
        vaccinated="Yes",
        dewormed="Yes",
        sterilized="Yes",
        health="Healthy",
        quantity=1,
        fee=0,
        location="Lębork",
        rescuer_id="rescuer123",
        description="Przyjazna i energiczna suczka, idealna dla rodziny z dziećmi.",
    )

    print("=================================================")

    # Read pet
    pet_db.read_pets({'_id': 14991})

    print("=================================================")

    # Delete pet
    pet_db.delete_pet({'_id': 11111})
    pet_db.read_pets({'_id': 11111})

    print("=================================================")

    # Find pets for adoption
    pets = pet_db.find_pets_for_adoption(
        pet_type="Dog",
        max_age=24,
        max_fee=50,
        location="Lębork",
        maturity_size="Medium",
        fur_length="Long"
    )

    for pet in pets:
        print(f"Pet name: {pet["name"]}, Age: {pet["age"]}, Fee: {pet["fee"]}")

    print("=================================================")

    # Find pets by description
    pets = pet_db.find_pets_by_description(["child", "children"])
    for pet in pets:
        print(f"Pet name: {pet["name"]}, Description: {pet["description"]}")

    print("=================================================")

    # Get pets by age
    pet_db.get_pets_by_age(order="oldest", n=5, adopted=False)

    print("=================================================")

    # Get pets by shelter stay
    pet_db.get_pets_by_shelter_stay(stay_type="longest", n=2, threshold_months=5, comparison="longer")

    print("=================================================")

    # Find pets ready for adoption
    pets = pet_db.pets_ready_for_adoption()
    for pet in pets[:5]:
        print(f"Pet id: {pet["_id"]}, Health: {pet["medical"]}")

    print("=================================================")

    # Adoption methods
    pet_db.is_ready_for_adoption(14950)
    print()
    pet_db.prepare_pet_for_adoption(14950)
    print()
    pet_db.is_ready_for_adoption(14950)
    print()
    pet_db.adopt_pet(14950)
    print()
    pet_db.read_pets({'_id': 14950})

    print("=================================================")

    # Pet of the day
    pet_db.get_pet_of_the_day()

    print("=================================================")

    # Statistics
    # All cities, May 2024
    print(pet_db.adoption_rescue_stats(month=5, year=2024, adopted=True, rescued=True, limit=5))

    # Only selected cities (adopted, rescued, in 2023, ascending)
    print(pet_db.adoption_rescue_stats(city=["Gdańsk", "Lębork", "Sopot"], year=2023, rescued=True, mode='groupby',
                                       order=1))

    # All cities, February 2024, adopted, sum
    print(pet_db.adoption_rescue_stats(adopted=True, month=2, year=2024, mode="sum"))

    # Default (adopted, this month, grouped by city)
    print(pet_db.adoption_rescue_stats())
