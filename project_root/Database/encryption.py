import cv2
import numpy as np
import os
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



def process_signature(image_binary, username):
    """
    Save the signature image locally, convert it into a numpy array, 
    and generate a 128-bit embedding (without flattening).

    Args:
    - image_binary (bytes): Binary data of the signature image.
    - username (str): Username of the user, used for naming the saved file.

    Returns:
    - embedding (np.ndarray): Feature embedding in its original form (without flattening).
    """     
    try:
        # Create a directory to store the signature if it doesn't exist
        os.makedirs("signatures", exist_ok=True)

        # Save the binary data as an image file locally
        file_path = os.path.join("signatures", f"{username}_signature.png")
        with open(file_path, "wb") as file:
            file.write(image_binary)

        # Load the saved image using OpenCV
        img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)  # Read as grayscale

        # Resize the image to the expected input size of the model
        img = cv2.resize(img, (128, 128))

        # Normalize pixel values and reshape for the CNN
        img_array = img / 255.0  # Normalize to range [0, 1]
        img_array = np.expand_dims(img_array, axis=(0, -1))

        # Get the embedding from the model (without flattening)
        embedding = embedder.predict(img_array)

        return embedding  # Return the embedding in its original form

    except Exception as e:
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
     
