# main.py
import base64
import logging
from bson import ObjectId
from fastapi import FastAPI, Depends, HTTPException, Request, UploadFile, File, status
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

import numpy as np

from encryption import process_signature, compare_signature


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
metadata_collection = db["FileMetadata"]
files_collection = db["Files"]

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

@app.get("/")
async def root(request: Request):
    return "Hello"

@app.post("/signup")
async def signup(request: Request):
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
        
        # Decode the Base64 signature directly into binary data
        try:
            if signature:
                signature_binary = base64.b64decode(signature.split(",")[1])
            else:
                raise HTTPException(status_code=400, detail="Signature is missing")
        except Exception as e:
            logger.error(f"Error decoding signature: {e}")
            raise HTTPException(status_code=400, detail="Invalid image data")

        # Process the binary data to generate the embedding
        embedding = process_signature(signature_binary,username)

        print(embedding.size, embedding)

        user_data = {
            "username": username,
            "password": get_password_hash(password),
            "age": age,
            "embedding": embedding.tolist(),  # Convert numpy array to list for JSON storage
        }

        users_collection.insert_one(user_data)
        logger.info(f"User {username} created successfully")
        return {"message": "User created successfully"}

    except Exception as e:
        logger.error(f"Error processing signup: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/token")
async def login(form_data: LoginRequest):  # Use Pydantic model to parse the JSON body
    logger.info(f"Login attempt for user: {form_data.username}")

    # Fetch the user from the database
    user = users_collection.find_one({"username": form_data.username})
    
    if not user or not verify_password(form_data.password, user['password']):
        raise HTTPException(
            status_code=400,
            detail="Invalid credentials"
        )
    
    # Create a JWT token
    access_token_expires = timedelta(minutes=30)  # Token expires in 30 minutes
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
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

# Endpoint to upload and encrypt file
@app.post("/upload-file")
async def upload_file(token: str = Depends(oauth2_scheme), file: UploadFile = File(...)):
    # Decode the JWT to identify the user
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        username = payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    if not username:
        raise HTTPException(status_code=401, detail="Invalid user")

    user = users_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Read file content
    file_content = await file.read()
    
    # Encrypt the file content (replace with your encryption logic)
    encrypted_content = file_content  # Replace this with the actual encryption logic

    # Store the file content as a binary blob in the Files collection
    file_blob = {
        "content": encrypted_content
    }
    file_blob_id = files_collection.insert_one(file_blob).inserted_id

    # Store metadata in the FileMetadata collection
    file_metadata = {
        "filename": file.filename,
        "file_blob_id": file_blob_id,  # Reference to the blob's ID
        "uploaded_by": username,
        "uploaded_at": datetime.utcnow(),
        "size": len(file_content),  # File size
        "content_type": file.content_type  # MIME type
    }
    file_metadata_id = metadata_collection.insert_one(file_metadata).inserted_id

    # Update the user's document with the reference to the metadata document
    users_collection.update_one(
        {"username": username},
        {"$push": {"uploaded_files": file_metadata_id}}
    )

    return {"message": "File uploaded and encrypted successfully", "file_metadata_id": str(file_metadata_id)}

# Endpoint to retrieve user's files
@app.get("/files")
async def get_user_files(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        username = payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = users_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Fetch file metadata references from the user's document
    file_metadata_ids = user.get("uploaded_files", [])
    metadata_cursor = metadata_collection.find({"_id": {"$in": file_metadata_ids}})
    
    # Return a list of metadata entries
    files = [
        {
            "id": str(metadata["_id"]),
            "filename": metadata["filename"],
            "uploaded_at": metadata["uploaded_at"],
            "size": metadata.get("size"),
            "content_type": metadata.get("content_type"),
        }
        for metadata in metadata_cursor
    ]

    return files

# Endpoint to retrieve and decrypt a file
@app.post("/decrypt")
async def decrypt(request: Request):
    try:
        # Parse the JSON body manually
        data = await request.json()

        # Log the incoming data for debugging
        logger.info(f"Received decryption request with data: {data}")

        # Access variables manually from the parsed JSON
        username = data.get("username")
        signature = data.get("signature")

        # Check if the user exists
        user = users_collection.find_one({"username": username})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Decode the Base64 signature directly into binary data
        try:
            if signature:
                signature_binary = base64.b64decode(signature.split(",")[1])
            else:
                raise HTTPException(status_code=400, detail="Signature is missing")
        except Exception as e:
            logger.error(f"Error decoding signature: {e}")
            raise HTTPException(status_code=400, detail="Invalid image data")

        # Process the binary data to generate the decryption embedding
        decryption_embedding = process_signature(signature_binary, username)

        # Retrieve the saved embedding from the user document
        saved_embedding = np.array(user["embedding"])

        # Compare both embeddings
        similarity = compare_signature(decryption_embedding, saved_embedding)
        similarity = similarity.tolist()[0][0]

        # Optionally, set a threshold for the similarity to decide if it's a match
        if similarity > 0.8:  # You can adjust this threshold
            return {"message": "Signature verified successfully"}
        else:
            raise HTTPException(status_code=400, detail="Signature does not match which is" + str(similarity))

    except Exception as e:
        logger.error(f"Error processing decryption request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")