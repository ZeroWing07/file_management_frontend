import React, { useState } from 'react';
import CanvasComponent from '../components/CanvasComponent';
import DarkModeToggle from '../components/DarkModeToggle';

const SignupPage = () => {
  const [formData, setFormData] = useState({ name: '', age: '', password: '', confirmPassword: '' });

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = () => {
    // Handle signup logic
  };

  return (
    <div>
      <h2>Sign Up</h2>
      <input name="name" placeholder="Name" onChange={handleChange} />
      <input name="age" placeholder="Age" type="number" onChange={handleChange} />
      <input name="password" placeholder="Password" type="password" onChange={handleChange} />
      <input name="confirmPassword" placeholder="Confirm Password" type="password" onChange={handleChange} />
      <CanvasComponent width={300} height={150} />
      <button onClick={handleSubmit}>Submit</button>
      <DarkModeToggle />
    </div>
  );
};

export default SignupPage;