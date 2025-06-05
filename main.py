from database_handler import PetAdoptionDatabase

if __name__ == "__main__":
    # uri = ("mongodb+srv://dbNonRelProject:project123@projectcluster.u5uvzky.mongodb.net/"
    #        "?retryWrites=true&w=majority&appName=ProjectCluster")
    uri = "mongodb://localhost:27017"
    pet_db = PetAdoptionDatabase(uri=uri)

    print("\n📄 One pet document:")
    pet_db.find_one_pet({"type": "Cat"})  # lub np. {"type": "Cat"}
