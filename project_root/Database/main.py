# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from fastapi import FastAPI

app = FastAPI()

from typing import Optional
class User(BaseModel):
    username: str
    password: str
    age: Optional[int] = None
    signature: Optional[str] = None

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://csrichaitanya2003:Arceus007@clustermfa.h4u5v.mongodb.net/MFAFileStorage?retryWrites=true&w=majority&appName=ClusterMFA")
JWT_SECRET = os.getenv("JWT_SECRET", "your_jwt_secret")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust to match frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# MongoDB setup
client = MongoClient(MONGO_URI)
db = client['MFAFileStorage']
users_collection = db['Users']

# FastAPI and Security setup
app = FastAPI()
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

# Authentication routes
@app.post("/signup")
async def signup(user: User):
    if users_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already registered")
    user_data = {
        "username": user.username,
        "password": get_password_hash(user.password),
        "age": user.age,
        "signature": user.signature
    }
    users_collection.insert_one(user_data)
    return {"message": "User created successfully"}

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
