import React, { useState } from 'react';
import DarkModeToggle from '../components/DarkModeToggle';
import '../App.css';

const EncryptionPage = () => {
  const [file, setFile] = useState(null);

  const handleFileChange = (e) => setFile(e.target.files[0]);

  const handleEncrypt = () => {
    // Handle file encryption
  };

  return (
    <div>
      <h2>Encrypt a File</h2>
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleEncrypt}>Encrypt</button>
      <DarkModeToggle />
    </div>
  );
};

export default EncryptionPage;