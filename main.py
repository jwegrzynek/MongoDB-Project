from database_handler import PetAdoptionDatabase
from datetime import datetime
from bson import ObjectId

if __name__ == "__main__":
    #uri = ("mongodb+srv://dbNonRelProject:project123@projectcluster.u5uvzky.mongodb.net/"
           #"?retryWrites=true&w=majority&appName=ProjectCluster")
    uri = "mongodb://localhost:27017"
    pet_db = PetAdoptionDatabase(uri=uri)

    # print("\n Create pet document:")
    # sample_pet = {
    #     "name": "Luna",
    #     "type": "Dog",
    #     "age": 3,
    #     "breed": {
    #         "primary": "Labrador Retriever",
    #         "secondary": None
    #     },
    #     "gender": "Female",
    #     "colors": ["Black", "White"],
    #     "maturitySize": "Medium",
    #     "furLength": "Short",
    #     "medical": {
    #         "vaccinated": "Yes",
    #         "dewormed": "Yes",
    #         "sterilized": "Yes",
    #         "health": "Healthy"
    #     },
    #     "quantity": 1,
    #     "fee": 0,
    #     "location": "Kraków",
    #     "rescuerId": "rescuer123",
    #     "rescueDate": datetime.today(),
    #     "description": "Przyjazna i energiczna suczka, idealna dla rodziny z dziećmi.",
    #     "adoption": {
    #         "adopted": False
    #     }
    # }
    # pet_db.create_pet(sample_pet)

    # pet_db.read_pets({'_id': 14991})

    # pet_db.delete_pet({'_id': 11111})
    # pet_db.read_pets({'_id': 11111})
    # print("\n One pet document:")
    # pet_db.read_pets({"type": "Cat"})

    # pet_db.get_recent_rescues()
    # pet_db.get_pets_by_shelter_stay(stay_type="longest", n=3, threshold_months=12, comparison= 'shorter')
    # pet_db.is_ready_for_adoption(14993)
    pet_db.adopt_pet(14990)

