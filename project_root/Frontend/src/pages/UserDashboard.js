import React from 'react';
import { Link } from 'react-router-dom';
import DarkModeToggle from '../components/DarkModeToggle';
import '../App.css';

const UserDashboard = () => (
  <div className="form-container">
    <button className="back-button">&larr; Back</button>
    <DarkModeToggle />
    <h2>User Dashboard</h2>
    <Link to="/encrypt" className="page-link">Encrypt a File</Link>
    <Link to="/files" className="page-link">View Encrypted Files</Link>
  </div>
);

export default UserDashboard;