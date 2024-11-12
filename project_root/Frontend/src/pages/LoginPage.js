// import React, { useState } from 'react';
// import DarkModeToggle from '../components/DarkModeToggle';
// import '../App.css';
// import BackButton from '../components/BackButton';

// const LoginPage = () => {
//   const [formData, setFormData] = useState({ name: '', password: '' });

//   const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

//   const handleLogin = () => {
//     // Handle login logic
//   };

//   return (
//     <div className="form-container">
//       <BackButton />
//       <DarkModeToggle />
//       <h2>Log In</h2>
//       <input className="form-input" name="name" placeholder="Name" onChange={handleChange} />
//       <input className="form-input" name="password" placeholder="Password" type="password" onChange={handleChange} />
//       <button className="form-button" onClick={handleLogin}>Log In</button>
//     </div>
//   );
// };

// export default LoginPage;

// pages/LoginPage.js
import React, { useState } from 'react';
import { useAuth } from '../components/AuthContext';

const LoginPage = () => {
  const { login } = useAuth();
  const [formData, setFormData] = useState({ username: '', password: '' });

  const handleLogin = async () => {
      const response = await fetch("http://127.0.0.1:8000/login/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(formData),
      });
      const data = await response.json();
      if (data.access_token) {
          login(data.access_token);  // Store token using AuthContext
          alert("Logged in successfully");
      } else {
          alert("Login failed");
      }
  };

  return (
      <div>
          <h2>Log In</h2>
          <input name="username" placeholder="Username" onChange={(e) => setFormData({ ...formData, username: e.target.value })} />
          <input name="password" placeholder="Password" type="password" onChange={(e) => setFormData({ ...formData, password: e.target.value })} />
          <button onClick={handleLogin}>Log In</button>
      </div>
  );
};

export default LoginPage;

