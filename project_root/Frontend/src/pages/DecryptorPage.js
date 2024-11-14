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

  useEffect(() => {
    axios.get(`http://localhost:8000/files/${fileId}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    })
    .then(response => setFileContent(response.data.content))
    .catch(error => console.error("Error fetching file:", error));
  }, [fileId]);

  const handleDecrypt = () => {
    const savedPassword = localStorage.getItem('password')?.trim();
    
    if (!savedPassword) {
        alert("No password set. Please login first.");
        return;
    }

    const trimmedEnteredPassword = enteredPassword.trim();

    console.log("Entered Password:", trimmedEnteredPassword);
    console.log("Saved Password from localStorage:", savedPassword);

    if (trimmedEnteredPassword !== savedPassword) {
        alert("Password mismatch. Please enter the correct password.");
        return;
    }

    // Proceed with decryption if password matches
    console.log("Password matched! Proceeding with decryption...");
    // Your decryption logic here
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