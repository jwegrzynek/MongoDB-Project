from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://dbNonRelProject:project123@projectcluster.u5uvzky.mongodb.net/?retryWrites=true&w=majority&appName=ProjectCluster"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    # Create or access database and collection
    db = client["sampleDB"]
    collection = db["sampleCollection"]

    # Insert sample data
    sample_data = [
        {"name": "Alice", "age": 30, "email": "alice@example.com"},
        {"name": "Bob", "age": 25, "email": "bob@example.com"},
        {"name": "Charlie", "age": 35, "email": "charlie@example.com"}
    ]
    result = collection.insert_many(sample_data)
    print("Inserted document IDs:", result.inserted_ids)

except Exception as e:
    print(e)
