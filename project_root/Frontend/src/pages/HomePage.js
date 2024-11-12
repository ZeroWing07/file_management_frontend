import React from 'react';
import { Link } from 'react-router-dom';
import DarkModeToggle from '../components/DarkModeToggle';
import '../App.css';

const HomePage = () => (
  <div>
    <h1>Welcome</h1>
    <Link to="/signup">Sign Up</Link>
    <Link to="/login">Log In</Link>
    <DarkModeToggle />
  </div>
);

export default HomePage;