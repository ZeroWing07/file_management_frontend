import React from 'react';
import { Link } from 'react-router-dom';
import DarkModeToggle from '../components/DarkModeToggle';

const UserDashboard = () => (
  <div>
    <h2>User Dashboard</h2>
    <Link to="/encrypt">Encrypt a File</Link>
    <Link to="/files">View Encrypted Files</Link>
    <DarkModeToggle />
  </div>
);

export default UserDashboard;