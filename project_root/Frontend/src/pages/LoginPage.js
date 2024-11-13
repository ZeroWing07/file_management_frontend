// pages/LoginPage.js
import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import BackButton from '../components/BackButton';

function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      const response = await axios.post('http://localhost:8000/token', {
        username,
        password,
      });
      localStorage.setItem('token', response.data.access_token); // Store JWT token
      alert("Login successful!");
      navigate('/dashboard'); // Navigate to the dashboard or home
    } catch (error) {
      console.error(error);
      alert("Login failed. Check credentials.");
    }
  };

  return (
    <div className="form-container">
      <BackButton />
      <h2>Login</h2>
      <form onSubmit={handleLogin}>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit">Log In</button>
        <button type="button" onClick={() => navigate('/forgot-password')}>Forgot Password?</button>
      </form>
    </div>
  );
}

export default LoginPage;
