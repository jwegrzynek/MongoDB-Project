from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd


def medical_check(value):
    if isinstance(value, str):
        value = value.strip().lower()
        if value in ["yes", "no", "not sure", "unknown", "n/a"]:
            return value
        else:
            return "unknown"



def csv_to_json(row):
    return {
        "name": row["Name"],
        "type": row["Type"],
        "age": int(row["Age"]),
        "breed": {
            "primary": row["Breed1"] if row["Breed1"] != "None" else None,
            "secondary": row["Breed2"] if row["Breed2"] != "None" else None,
        },
        "gender": row["Gender"],
        "colors": list(filter(lambda x: x != "None" and pd.notna(x), [row["Color1"], row["Color2"], row["Color3"]])),
        "maturitySize": row["MaturitySize"],
        "furLength": row["FurLength"],
        "medical": {
            "vaccinated": medical_check(["Vaccinated"]),
            "dewormed": medical_check(["Dewormed"]),
            "sterilized": medical_check(["Sterilized"]),
            "health": row["Health"]
        },
        "quantity": int(row["Quantity"]),
        "fee": int(row["Fee"]),
        "location": {
            "state": row["State"]
        },
        "rescuerId": row["RescuerID"],
        "description": row["Description"],
        "adoptionSpeed": row["AdoptionSpeed"]
    }


def load_csv_to_documents(csv_path):
    df = pd.read_csv(csv_path)
    df = df[:10]
    # Optionally fill NaN values with 'None' string or real Python None
    df.fillna("None", inplace=True)
    documents = df.apply(csv_to_json, axis=1).tolist()
    return documents


uri = "mongodb+srv://dbNonRelProject:project123@projectcluster.u5uvzky.mongodb.net/?retryWrites=true&w=majority&appName=ProjectCluster"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    # Create or access database and collection
    db = client["petsDB"]
    collection = db["petsInformation"]

    docs = load_csv_to_documents("./data/processed_pets.csv")
    collection.insert_many(docs)
    print(f"Inserted {len(docs)} documents into MongoDB")

except Exception as e:
    print(e)
