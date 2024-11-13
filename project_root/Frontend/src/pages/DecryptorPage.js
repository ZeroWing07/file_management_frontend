import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import CanvasComponent from '../components/CanvasComponent';
import '../App.css'
import BackButton from '../components/BackButton';


const DecryptorPage = () => {
  const { fileId } = useParams();
  const [fileContent, setFileContent] = useState(null);
  const [password, setPassword] = useState('');
  const canvasRef = useRef(null);

  useEffect(() => {
    console.log("Fetching file with ID:", fileId); // Log file ID
    axios.get(`http://localhost:8000/files/${fileId}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    })
    .then(response => {
      console.log("API Response:", response); // Log response data
      setFileContent(response.data.content);
    })
    .catch(error => {
      console.error("Error fetching file:", error); // Log error if fetching fails
    });
  }, [fileId]);

  const handleDecrypt = () => {
    // Implement decryption logic here
    alert("File decrypted successfully!");
  };

  return (
    <div>
      <h2>Decrypt File</h2>
      <input
        type="password"
        placeholder="Password"
        onChange={(e) => setPassword(e.target.value)}
      />
      <CanvasComponent ref={canvasRef} width={300} height={150} />
      <button onClick={handleDecrypt}>Decrypt</button>

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
