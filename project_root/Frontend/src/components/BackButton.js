// BackButton.js
import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const BackButton = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleBack = () => {
    // Check if the current location is the login page
    if (location.pathname === '/login') {
      navigate('/'); // Navigate to the homepage if on the login page
    } else {
      navigate(-1); // Otherwise, go back to the previous page
    }
  };

  return (
    <button onClick={handleBack} className="back-button">
      Back
    </button>
  );
};

export default BackButton;
