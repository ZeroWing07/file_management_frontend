from pymongo import MongoClient
from passlib.context import CryptContext

MONGO_URI="mongodb+srv://csrichaitanya2003:Arceus007@clustermfa.h4u5v.mongodb.net/MFAFileStorage?retryWrites=true&w=majority&appName=ClusterMFA"
client = MongoClient(MONGO_URI)
db = client["MFAFileStorage"]
users_collection = db["Users"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(username: str, password: str):
    hashed_password = pwd_context.hash(password)
    users_collection.insert_one({"username": username, "password": hashed_password})

def authenticate_user(username: str, password: str):
    user = users_collection.find_one({"username": username})
    if user and pwd_context.verify(password, user["password"]):
        return user
    return None