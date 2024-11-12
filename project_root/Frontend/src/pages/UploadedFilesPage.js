import React from 'react';
import DarkModeToggle from '../components/DarkModeToggle';
import '../App.css';

const UploadedFilesPage = () => (
  <div className="form-container">
    <button className="back-button">&larr; Back</button>
    <DarkModeToggle />
    <h2>Uploaded Files</h2>
    {/* List of files will go here */}
  </div>
);

export default UploadedFilesPage;