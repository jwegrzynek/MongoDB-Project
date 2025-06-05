from database_handler import PetAdoptionDatabase

if __name__ == "__main__":
    URI = ("mongodb+srv://dbNonRelProject:project123@projectcluster.u5uvzky.mongodb.net/"
           "?retryWrites=true&w=majority&appName=ProjectCluster")
    pet_db = PetAdoptionDatabase(uri=URI)

    print("\n📄 One pet document:")
    pet_db.find_one_pet({"type": "Cat"})  # lub np. {"type": "Cat"}
