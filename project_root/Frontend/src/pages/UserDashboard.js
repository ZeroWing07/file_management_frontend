// UserDashboard.js

import React from 'react';
import { useNavigate } from 'react-router-dom';

const UserDashboard = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    // Clear any user authentication tokens or data
    localStorage.removeItem('authToken');
    navigate('/login');
  };

  const handleEncryptFile = () => {
    navigate('/encrypt');
  };

  const handleViewEncryptedFiles = () => {
    navigate('/uploaded-files');
  };

  return (
    <div className="dashboard-container">
      <h1>Welcome to Your Dashboard</h1>
      
      <div className="dashboard-box" onClick={handleEncryptFile}>
        <h2>Encrypt a File</h2>
      </div>
      
      <div className="dashboard-box" onClick={handleViewEncryptedFiles}>
        <h2>View Encrypted Files</h2>
      </div>
      
      <button onClick={handleLogout} className="logout-button">
        Logout
      </button>
    </div>
  );
};

export default UserDashboard;
