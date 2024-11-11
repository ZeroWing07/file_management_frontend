import React, { useState } from 'react';
import CanvasComponent from '../components/CanvasComponent';
import DarkModeToggle from '../components/DarkModeToggle';

const DecryptorPage = () => {
  const [password, setPassword] = useState('');

  const handleDecrypt = () => {
    // Handle decryption
  };

  return (
    <div>
      <h2>Decrypt File</h2>
      <input type="password" placeholder="Password" onChange={(e) => setPassword(e.target.value)} />
      <CanvasComponent width={300} height={150} />
      <button onClick={handleDecrypt}>Decrypt</button>
      <DarkModeToggle />
    </div>
  );
};

export default DecryptorPage;