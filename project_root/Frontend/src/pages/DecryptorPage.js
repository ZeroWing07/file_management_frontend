import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import CanvasComponent from '../components/CanvasComponent';
import '../App.css';
import BackButton from '../components/BackButton';

const DecryptorPage = () => {
  const { fileId } = useParams();
  const [fileContent, setFileContent] = useState(null);
  const [enteredPassword, setEnteredPassword] = useState('');
  const canvasRef = useRef(null);

  const handleDecrypt = async () => {
    try {
      // Get the token from localStorage
      const token = localStorage.getItem("token");
      if (!token) {
        alert("Token not found. Please login first.");
        return;
      }

      // Decode the token to extract the username
      const decodedToken = JSON.parse(atob(token.split(".")[1]));
      const username = decodedToken?.sub; // Assuming 'sub' contains the username
      if (!username) {
        alert("Username not found in token. Please login again.");
        return;
      }

      // Get the signature from the canvas
      const canvas = canvasRef.current;
      if (!canvas) {
        alert("Signature canvas not found. Please sign again.");
        return;
      }

      const signature = canvas.toDataURL("image/png");

      // Call the decrypt endpoint using Axios
      const response = await axios.post(
        "http://localhost:8000/decrypt",
        {
          username: username,
          signature: signature,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      // Handle the response
      console.log("Decryption successful:", response.data);
      alert("Decryption successful! File is being processed.");
      // Add logic to handle the decrypted file here
    } catch (error) {
      if (error.response) {
        // Server responded with a status other than 2xx
        alert(`Decryption failed: ${error.response.data.detail}`);
        console.error("Decryption error response:", error.response.data);
      } else {
        // Other errors
        console.error("Error during decryption:", error);
        alert("An error occurred during decryption. Please try again.");
      }
    }
  };


  // Call the clearCanvas method on the canvasRef
  const handleClearCanvas = () => {
    canvasRef.current.clearCanvas();
  };

  return (
    <div>
      <h2>Decrypt File</h2>
      <input
        type="password"
        placeholder="Password"
        value={enteredPassword}
        onChange={(e) => setEnteredPassword(e.target.value)}
      />
      <CanvasComponent ref={canvasRef} width={300} height={300} />
      <button onClick={handleDecrypt}>Decrypt</button>
      <button onClick={handleClearCanvas}>Clear Canvas</button> {/* Clear Canvas Button */}

      {fileContent ? (
        <a href={`data:application/octet-stream;base64,${fileContent}`} download="decrypted_file">
          Download File
        </a>
      ) : (
        <p>Loading file content...</p>
      )}
      <BackButton />
    </div>
  );
};

export default DecryptorPage;