import React, { useState } from 'react';
import axios from 'axios';
import '../App.css';
import BackButton from '../components/BackButton';

const EncryptionPage = () => {
  const [file, setFile] = useState(null);

  const handleFileChange = (e) => setFile(e.target.files[0]);

  const handleEncrypt = async () => {
    const formData = new FormData();
    formData.append("file", file);
  
    try {
      const response = await axios.post("http://localhost:8000/upload-file", formData, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (response.status === 200) alert("File encrypted and uploaded!");
    } catch (error) {
      console.error("Error uploading file:", error);
      alert("Upload failed. Please try again.");
    }
  };
  
  return (
    <div>
      <h2>Encrypt a File</h2>
      <div className="file-upload">
        <input type="file" onChange={handleFileChange} />
        <button onClick={handleEncrypt}>Encrypt</button>
      </div>
      <BackButton />
    </div>
  );
};

export default EncryptionPage;