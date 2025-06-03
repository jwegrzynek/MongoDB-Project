from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd
import random
from datetime import datetime, timedelta


def medical_check(info):
    if isinstance(info, str):
        info = info.strip().lower()
        if info in ["yes", "no", "not sure", "unknown", "n/a"]:
            return info
        else:
            return "unknown"


def adoption_check(rescue_date, adoption_period):
    today = datetime.today()
    if adoption_period == 'Same Day':
        days = 0
    elif adoption_period == '1-7 Days':
        days = random.randint(1, 7)
    elif adoption_period == '8-30 Days':
        days = random.randint(8, 30)
    elif adoption_period == '31-90 Days':
        days = random.randint(31, 90)
    else:
        days = random.choices(
            [
                random.randint(90, 150),
                random.randint(151, 250),
                random.randint(251, 365),
                random.randint(366, 700)
            ],
            [0.6, 0.3, 0.17, 0.03],
            k=1
        )[0]

    adoption_date = rescue_date + timedelta(days=days)
    random_hour = random.randint(8, 17)
    random_minute = random.randint(0, 59)
    random_second = random.randint(0, 59)

    adoption_date = adoption_date.replace(
        hour=random_hour,
        minute=random_minute,
        second=random_second
    )

    if adoption_date <= today:
        return {
            "adopted": True,
            "adoptionDate": adoption_date,
            "adoptionPeriod": adoption_period,
            "daysInShelter": (adoption_date - rescue_date).days
        }
    else:
        return {
            "adopted": False
        }


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
            "vaccinated": medical_check(row["Vaccinated"]),
            "dewormed": medical_check(row["Dewormed"]),
            "sterilized": medical_check(row["Sterilized"]),
            "health": row["Health"]
        },
        "quantity": int(row["Quantity"]),
        "fee": int(row["Fee"]),
        "location": row["City"],
        "rescuerId": row["RescuerID"],
        "description": row["Description"],
        "adoption": adoption_check(row['RescueDate'], row['AdoptionSpeed']),
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
