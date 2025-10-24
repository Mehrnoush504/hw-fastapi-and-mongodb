from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["starcoach-api"]
users = db["users"]

users.insert_one({"name": "Bob", "age": 30})
