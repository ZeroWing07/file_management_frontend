import cv2
import numpy as np
import os
import logging
from tensorflow.keras.models import load_model, Model
from tensorflow.keras.utils import register_keras_serializable
from tensorflow.keras.layers import Lambda
import tensorflow.keras.backend as K
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from dotenv import load_dotenv
import base64

@register_keras_serializable()
def euclidean_distance(vectors):
	# unpack the vectors into separate lists
	(featsA, featsB) = vectors
	# compute the sum of squared distances between the vectors
	sumSquared = K.sum(K.square(featsA - featsB), axis=1,
		keepdims=True)
	# return the euclidean distance between the vectors
	return K.sqrt(K.maximum(sumSquared, K.epsilon()))

load_dotenv()

KEY_ENCRYPTION_SECRET = os.getenv("KEY_ENCRYPTION_SECRET")

# Load the CNN model globally to avoid reloading for each request
MODEL_PATH = 'siamese_model.keras'
cnn_model = load_model(MODEL_PATH)
embedder = Model(inputs=cnn_model.get_layer("functional").input, 
                                 outputs=cnn_model.get_layer("functional").output)

logger = logging.getLogger(__name__)



def process_signature(image_binary, username):
    try:
        # Log the size of incoming binary data
        logger.info(f"Received binary data size: {len(image_binary)} bytes")
        
        # Decode the binary image data
        np_image = np.frombuffer(image_binary, np.uint8)
        logger.info(f"Numpy array shape after frombuffer: {np_image.shape}")
        
        # Decode using cv2.IMREAD_COLOR to ensure RGB format
        img = cv2.imdecode(np_image, cv2.IMREAD_COLOR)
        
        if img is None:
            raise RuntimeError("Failed to decode image from binary data")
            
        logger.info(f"Decoded image shape: {img.shape}")
        logger.info(f"Image dtype: {img.dtype}")
        logger.info(f"Image min/max values: {np.min(img)}/{np.max(img)}")

        # Save the color image first for debugging
        cv2.imwrite(f"signatures/{username}_color.png", img)
        
        # Convert to grayscale
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        logger.info(f"Grayscale image shape: {img_gray.shape}")
        
        # Save the original grayscale image for verification
        cv2.imwrite(f"signatures/{username}_original.png", img_gray)
        
        # Resize the image
        img_resized = cv2.resize(img_gray, (128, 128))
        logger.info(f"Resized image shape: {img_resized.shape}")
        
        # Save resized image for debugging
        cv2.imwrite(f"signatures/{username}_resized.png", img_resized)
        
        # Normalize pixel values and reshape for the CNN
        img_array = img_resized / 255.0
        img_array = np.expand_dims(img_array, axis=(0, -1))
        logger.info(f"Final array shape for model: {img_array.shape}")
        
        # Get the embedding
        embedding = embedder.predict(img_array)
        
        return embedding

    except Exception as e:
        logger.error(f"Error in process_signature: {str(e)}")
        raise RuntimeError(f"Error processing signature image: {e}")
    
def compare_signature(backend_embedding, decryption_embedding):
    """
    Compare two signature embeddings using the Siamese network.

    Args:
    - backend_embedding (np.ndarray): Embedding generated during encryption.
    - decryption_embedding (np.ndarray): Embedding generated during decryption.

    Returns:
    - similarity_score (float): The similarity score between the two embeddings.
    """
    try:
        # Assuming backend_embedding and decryption_embedding are in their original shape

        # Get the final layer from the pre-loaded Siamese model
        final_layer = Model(inputs=[cnn_model.get_layer("lambda").input[0], cnn_model.get_layer("lambda").input[1]], 
                            outputs=cnn_model.output)

        # Use the final layer to predict the similarity score between the two embeddings
        final_output = final_layer.predict([backend_embedding, decryption_embedding])

        # # The output will be a similarity score (closer to 0 is more similar, 1 means different)
        # similarity_score = final_output[0][0]  # Assuming final_output is 2D (batch_size, 1)

        return final_output

    except Exception as e:
        raise RuntimeError(f"Error comparing signatures: {e}")
    
# Function to encrypt content with AES
def encrypt_content(key: bytes, data: bytes) -> bytes:
    # Generate a random IV (Initialization Vector)
    iv = os.urandom(16)
    
    # Create AES cipher
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    # Pad data to be AES block size compatible
    padder = PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()
    
    # Encrypt the padded data
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    
    # Return IV concatenated with encrypted data
    return iv + encrypted_data

# Function to encrypt the AES key
def encrypt_key(key: bytes, secret: bytes) -> bytes:
    # Use HKDF for key derivation
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"key-encryption",
        backend=default_backend()
    ).derive(secret)
    
    # Encrypt the key using the derived key
    cipher = Cipher(algorithms.AES(derived_key), modes.ECB(), backend=default_backend())
    encryptor = cipher.encryptor()
    
    padder = PKCS7(algorithms.AES.block_size).padder()
    padded_key = padder.update(key) + padder.finalize()
    
    encrypted_key = encryptor.update(padded_key) + encryptor.finalize()
    return encrypted_key
     
