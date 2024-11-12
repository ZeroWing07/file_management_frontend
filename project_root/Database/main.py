# from fastapi import FastAPI, File, UploadFile
# import shutil
# from pathlib import Path
# from pymongo import MongoClient
# import os

# MONGO_URI = "mongodb+srv://csrichaitanya2003:Arceus007@@clustermfa.h4u5v.mongodb.net/?retryWrites=true&w=majority&appName=ClusterMFA"
# client = MongoClient(MONGO_URI)
# db = client.get_database("<database>")

# app = FastAPI()

# uploads_dir = Path(__file__).parent / "uploads"
# uploads_dir.mkdir(exist_ok=True)

# @app.post("/upload-image/")
# async def upload_image(file: UploadFile = File(...)):
#     file_path = uploads_dir / file.filename
#     with file_path.open("wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
#     return {"message": f"File '{file.filename}' uploaded successfully"}


from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pymongo import MongoClient
from datetime import datetime, timedelta
from pydantic import BaseModel
from auth import create_user, authenticate_user
import os

# Load environment variables (for MongoDB URL, JWT secret)
MONGO_URI = "mongodb+srv://encoded_csrichaitanya2003:encoded_Arceus007@@clustermfa.h4u5v.mongodb.net/?retryWrites=true&w=majority&appName=ClusterMFA"
JWT_SECRET = "your_jwt_secret"

# MongoDB Connection
client = MongoClient(MONGO_URI)
db = client["MFAFileStorage"]  # Database name
users_collection = db["Users"]  # Collection name

app = FastAPI()

# Password Hashing and JWT Configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    password: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")
    return encoded_jwt

@app.post("/signup/")
async def signup(user: User):
    # Check if user exists
    if users_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already registered")

    # Create and save user
    hashed_password = get_password_hash(user.password)
    users_collection.insert_one({"username": user.username, "password": hashed_password})
    return {"message": "User created successfully"}

@app.post("/login/", response_model=Token)
async def login(user: User):
    db_user = users_collection.find_one({"username": user.username})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/protected-route/")
async def protected_route(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {"message": "This is a protected route"}