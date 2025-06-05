from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd
import random
from datetime import datetime, timedelta
from time import time


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


def row_to_document(row):
    return {
        "name": row["Name"] if row["Name"] != "None" else None,
        "type": row["Type"],
        "age": int(row["Age"]),
        "breed": {
            "primary": row["Breed1"] if pd.notna(row["Breed1"]) and row["Breed1"] != "None" else None,
            "secondary": row["Breed2"] if pd.notna(row["Breed2"]) and row["Breed2"] != "None" else None,
        },
        "gender": row["Gender"],
        "colors": list(filter(lambda x: x != "None" and pd.notna(x), [row["Color1"], row["Color2"], row["Color3"]])),
        "maturitySize": row["MaturitySize"],
        "furLength": row["FurLength"],
        "medical": {
            "vaccinated": row["Vaccinated"],
            "dewormed": row["Dewormed"],
            "sterilized": row["Sterilized"],
            "health": row["Health"]
        },
        "quantity": int(row["Quantity"]),
        "fee": int(row["Fee"]),
        "location": row["City"],
        "rescuerId": row["RescuerID"],
        "rescueDate": pd.to_datetime(row['RescueDate']),
        "description": row["Description"] if row["Description"] != "None" else None,
        "adoption": adoption_check(pd.to_datetime(row['RescueDate']), row['AdoptionSpeed']),
    }


def documents_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    df.fillna('None', inplace=True)
    documents = df.apply(row_to_document, axis=1).tolist()
    return documents


def return_schema():
    schema = {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["name", "type", "age", "breed", "gender", "colors", "maturitySize", "furLength", "medical",
                             "quantity", "fee", "rescuerId", "rescueDate", "adoption", "description", "location"],
                "properties": {
                    "name": {
                        "bsonType": ["string", "null"],
                        "description": "Name of the animal"
                    },
                    "type": {
                        "bsonType": "string",
                        "description": "Type of animal (e.g., Dog, Cat)"
                    },
                    "age": {
                        "bsonType": "int",
                        "minimum": 0,
                        "description": "Age in years"
                    },
                    "breed": {
                        "bsonType": "object",
                        "properties": {
                            "primary": {
                                "bsonType": ["string", "null"],
                                "description": "Primary breed"
                            },
                            "secondary": {
                                "bsonType": ["string", "null"],
                                "description": "Secondary breed if mixed"
                            }
                        }
                    },
                    "gender": {
                        "enum": ["Male", "Female", "Mixed", "Unknown"],
                        "description": "Gender of the animal (Mixed if many animals)"
                    },
                    "colors": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "string",
                            "description": "Color of the animal"
                        }
                    },
                    "maturitySize": {
                        "enum": ["Small", "Medium", "Large", "Extra Large", "Unknown"],
                        "description": "Expected size of grown animal"
                    },
                    "furLength": {
                        "enum": ["Short", "Medium", "Long", "Bald", "Unknown"],
                        "description": "Length of fur"
                    },
                    "medical": {
                        "bsonType": "object",
                        "required": ["vaccinated", "dewormed", "sterilized", "health"],
                        "properties": {
                            "vaccinated": {
                                "enum": ["Yes", "No", "Not sure", "Unknown"],
                                "description": "Vaccination status"
                            },
                            "dewormed": {
                                "enum": ["Yes", "No", "Not sure", "Unknown"],
                                "description": "Deworming status"
                            },
                            "sterilized": {
                                "enum": ["Yes", "No", "Not sure", "Unknown"],
                                "description": "Sterilization status"
                            },
                            "health": {
                                "enum": ["Healthy", "Minor Injury", "Serious Injury", "Unknown"],
                                "description": "Overall health status"
                            }
                        }
                    },
                    "quantity": {
                        "bsonType": "int",
                        "minimum": 1,
                        "description": "Number of animals in this record"
                    },
                    "fee": {
                        "bsonType": "int",
                        "minimum": 0,
                        "description": "Adoption fee"
                    },
                    "location": {
                        "bsonType": "string",
                        "description": "Location where animal is available"
                    },
                    "rescuerId": {
                        "bsonType": "string",
                        "description": "ID of the rescuer"
                    },
                    "rescueDate": {
                        "bsonType": "date",
                        "description": "Date when animal was rescued"
                    },
                    "description": {
                        "bsonType": ["string", "null"],
                        "description": "Description of the animal"
                    },
                    "adoption": {
                        "bsonType": "object",
                        "required": ["adopted"],
                        "properties": {
                            "adopted": {
                                "bsonType": "bool",
                                "description": "Whether the animal has been adopted"
                            },
                            "adoptionDate": {
                                "bsonType": ["date", "null"],
                                "description": "Date of adoption if adopted"
                            },
                            "adoptionPeriod": {
                                "enum": ["Same Day", "1-7 Days", "8-30 Days", "31-90 Days", "Over 100 Days", "null"],
                                "description": "How long it took to be adopted (period)"
                            },
                            "daysInShelter": {
                                "bsonType": ["int", "null"],
                                "description": "Number of days in shelter"
                            }
                        }
                    }
                }

            }
        },
        "validationLevel": "strict",
        "validationAction": "error"
    }

    return schema


def create_database(csv_path: str, database_uri: str, database_name: str, collection_name: str, schema: dict):
    # Create a new client and connect to the server
    client = MongoClient(database_uri, server_api=ServerApi('1'))

    try:
        # Start stoper
        start = time()

        # Test connection
        client.admin.command('ping')
        print("✅ Connected to MongoDB!")

        # Access the database
        db = client[database_name]

        # Drop existing collection if it exists (optional but recommended for development)
        if "petsInformation" in db.list_collection_names():
            db.drop_collection("petsInformation")
            print("🔁 Dropped existing 'petsInformation' collection.")

        # Create new collection with schema validation
        db.create_collection(collection_name, **schema)
        print("📦 Created 'petsInformation' collection with schema validation.")

        # Load data from CSV and insert
        docs = documents_from_csv(csv_path)
        collection = db[collection_name]  # Get the newly created collection
        collection.insert_many(docs)
        print(f"✅ Inserted {len(docs)} documents into MongoDB.")

        # Stop stoper
        stop = time()
        print(f"⌚️ The database creation process took: {round(stop - start, 2)} sec")

    except Exception as e:
        print("❌ Error occurred:", e)


if __name__ == "__main__":
    database_uri = ("mongodb+srv://dbNonRelProject:project123@projectcluster.u5uvzky.mongodb.net/"
                    "?retryWrites=true&w=majority&appName=ProjectCluster")
    csv_path = "pets.csv"
    database_name = "petsDB"
    collection_name = "petsInformation"
    schema = return_schema()

    create_database(
        csv_path=csv_path,
        database_uri=database_uri,
        database_name=database_name,
        collection_name=collection_name,
        schema=schema
    )
