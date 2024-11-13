# main.py
import base64
import logging
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(max_request_size=10*1024*1024)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ensure this matches the frontend URL
    allow_credentials=False,
    allow_methods=["*"],  # Allow all methods (POST, GET, etc.)
    allow_headers=["*"],  # Allow all headers
)

from typing import Optional
class User(BaseModel):
    username: str
    password: str
    age: int
    signature: str

# Load environment variables
load_dotenv()
MONGO_URI = "mongodb+srv://amogus:sussyimposter@clustermfa.h4u5v.mongodb.net/MFAFileStorage?retryWrites=true&w=majority&appName=ClusterMFA"
JWT_SECRET = os.getenv("JWT_SECRET", "8417bc78ad9f51e44f33c7cb681c5ad116662d382540710b080d39493c0247316d007ad817979f46f8e1b5b1532e47cef2fb1b3ab2a9b379b2165db80c4e6b4a4ab2c66d6d3dd8f26d51233fa12766e60065f96028b9cb4c0da729c0cc155757b08a28db39b21f3ae30285dd4fcc5efa6e7324baacc2f3682973457d9401027d05b904e019149c95caf2832eeb250af8d374729e98e43c3b1ef046f0ecbd3ed2a6f92a3a97e0ba6b6f8a98dcd7834b92d4828ed96be8f287d53731f5d003b135036a9de500a976971ac1c6fb7ec9d8e85f1d846929e80d0f8a2de31c7442696aad99e21e542296d0fa1c594aba45600ff6c27ff5b0a8ff004c08b4ad2f91b0a4")

# MongoDB setup
client = MongoClient(MONGO_URI)
db = client['MFAFileStorage']
users_collection = db['Users']

# FastAPI and Security setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWT token function
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")

# Models
class User(BaseModel):
    username: str
    password: str

# Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

@app.post("/signup")
async def signup(request: Request):  # Use Request to manually access the request body
    try:
        # Parse the JSON body manually
        user = await request.json()

        # Log the incoming user data for debugging
        logger.info(f"Received signup request with data: {user}")

        # Access variables manually from the parsed JSON
        username = user.get("username")
        password = user.get("password")
        age = user.get("age")
        signature = user.get("signature")

        # Check if the user already exists
        if users_collection.find_one({"username": username}):
            raise HTTPException(status_code=400, detail="Username already registered")
        
        # Decode the Base64 signature back to binary data (optional, for storage)
        try:
            if signature:
                signature_binary = base64.b64decode(signature.split(",")[1])
            else:
                signature_binary = None
        except Exception as e:
            logger.error(f"Error decoding signature: {e}")
            raise HTTPException(status_code=400, detail="Invalid image data")

        user_data = {
            "username": username,
            "password": get_password_hash(password),
            "age": age,
            "signature": signature_binary  # Store binary data in MongoDB
        }

        users_collection.insert_one(user_data)
        logger.info(f"User {username} created successfully")
        return {"message": "User created successfully"}

    except Exception as e:
        logger.error(f"Error processing signup: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_collection.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user['password']):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user["username"]}, expires_delta=timedelta(minutes=30))
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        return {"username": username}
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
