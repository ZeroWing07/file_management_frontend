# main.py
import base64
import logging
import struct
from bson import ObjectId
from fastapi import FastAPI, Depends, HTTPException, Request, UploadFile, File, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse
from io import BytesIO
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
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

import numpy as np
import uuid

from encryption import process_signature, compare_signature, encrypt_key, encrypt_content, decrypt_content ,decrypt_key


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
KEY_ENCRYPTION_SECRET = os.getenv("KEY_ENCRYPTION_SECRET")

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
        #logger.info(f"Received signup request with data: {user}")

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

    # Retrieve user's embedding from the database
    embedding = user.get("embedding")
    if not embedding:
        raise HTTPException(status_code=400, detail="User embedding not found")

    # Generate the file ID
    file_id = str(uuid.uuid4())

    # Pack the embedding list into bytes
    embedding_bytes = struct.pack(f"{len(embedding[0])}f", *(embedding[0]))

    # Generate the AES key by combining the embedding and file ID
    combined_key_material = embedding_bytes + file_id.encode()
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"file-encryption",
        backend=default_backend()
    ).derive(combined_key_material)

    # Encrypt the file content
    encrypted_content = encrypt_content(derived_key, file_content)

    # Save the encrypted file locally
    save_directory = "encrypted_files"  # Directory for saving encrypted files locally
    os.makedirs(save_directory, exist_ok=True)  # Ensure the directory exists
    local_file_path = os.path.join(save_directory, f"{file_id}_{file.filename}.enc")

    try:
        with open(local_file_path, "wb") as encrypted_file:
            encrypted_file.write(encrypted_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file locally: {str(e)}")


    # Encrypt the key using the secret from .env
    encrypted_key = encrypt_key(derived_key, KEY_ENCRYPTION_SECRET.encode())

    # Store the encrypted file content as a binary blob in the Files collection
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
        "content_type": file.content_type,  # MIME type
        "encrypted_key": base64.b64encode(encrypted_key).decode()  # Store the encrypted key as Base64
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

# Add this endpoint to main.py
@app.post("/decrypt-file/{file_id}")
async def decrypt_file(
    file_id: str,
    request: Request
):
    try:
        # Parse the request body
        data = await request.json()
        username = data.get("username")
        signature = data.get("signature")

        # Validate user exists
        user = users_collection.find_one({"username": username})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Convert file_id string to ObjectId
        try:
            file_metadata_id = ObjectId(file_id)
        except:
            raise HTTPException(status_code=400, detail="Invalid file ID")

        # Get file metadata
        file_metadata = metadata_collection.find_one({"_id": file_metadata_id})
        if not file_metadata:
            raise HTTPException(status_code=404, detail="File not found")

        # Verify file ownership
        if file_metadata["uploaded_by"] != username:
            raise HTTPException(status_code=403, detail="Access denied")

        # Process and verify signature
        signature_binary = base64.b64decode(signature.split(",")[1])
        decryption_embedding = process_signature(signature_binary, username)
        saved_embedding = np.array(user["embedding"])
        similarity = compare_signature(decryption_embedding, saved_embedding)
        similarity = similarity.tolist()[0][0]

        if similarity <= 0.80:
            raise HTTPException(status_code=400, detail=f"Signature verification failed with similarity {similarity}")

        # Get the encrypted file content
        file_blob = files_collection.find_one({"_id": file_metadata["file_blob_id"]})
        if not file_blob:
            raise HTTPException(status_code=404, detail="File content not found")

        # Get and decrypt the file key
        encrypted_key = base64.b64decode(file_metadata["encrypted_key"])
        decrypted_key = decrypt_key(encrypted_key, KEY_ENCRYPTION_SECRET.encode())

        # Decrypt the file content
        decrypted_content = decrypt_content(decrypted_key, file_blob["content"])

        # Create a BytesIO object for streaming
        file_stream = BytesIO(decrypted_content)

        # Return the decrypted file as a streaming response
        return StreamingResponse(
            file_stream,
            media_type=file_metadata["content_type"],
            headers={
                "Content-Disposition": f'attachment; filename="{file_metadata["filename"]}"'
            }
        )

    except Exception as e:
        logger.error(f"Error in decrypt_file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Decryption error: {str(e)}")