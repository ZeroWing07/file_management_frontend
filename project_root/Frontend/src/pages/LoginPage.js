import React, { useState } from 'react';
import DarkModeToggle from '../components/DarkModeToggle';

const LoginPage = () => {
  const [formData, setFormData] = useState({ name: '', password: '' });

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleLogin = () => {
    // Handle login logic
  };

  return (
    <div>
      <h2>Log In</h2>
      <input name="name" placeholder="Name" onChange={handleChange} />
      <input name="password" placeholder="Password" type="password" onChange={handleChange} />
      <button onClick={handleLogin}>Log In</button>
      <DarkModeToggle />
    </div>
  );
};

export default LoginPage;