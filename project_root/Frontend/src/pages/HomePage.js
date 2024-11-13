import React from 'react';
import { Link } from 'react-router-dom';
import '../App.css';

const HomePage = () => (
  <div className="homepage">
    <h1>Welcome</h1>
    <Link to="/signup">Sign Up</Link>
    <Link to="/login">Log In</Link>\
  </div>
);

export default HomePage;
