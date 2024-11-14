import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import HomePage from './pages/HomePage';
import SignupPage from './pages/SignupPage';
import LoginPage from './pages/LoginPage';
import UserDashboard from './pages/UserDashboard';
import EncryptionPage from './pages/EncryptionPage';
import UploadedFilesPage from './pages/UploadedFilesPage';
import DecryptorPage from './pages/DecryptorPage';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/signup" element={<SignupPage />} /> 
        <Route path="/login" element={<LoginPage />} />
        <Route path="/dashboard" element={<UserDashboard />} />
        <Route path="/encrypt" element={<EncryptionPage />} />
        <Route path="/uploaded-files" element={<UploadedFilesPage />} />
        <Route path="/decryptor/:fileId" element={<DecryptorPage />} />
      </Routes>
    </Router>
  );
};

export default App;