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

const LoginPage = () => {
  const [formData, setFormData] = useState({ name: '', password: '' });

  const handleLogin = async () => {
    const response = await fetch("http://localhost:8000/login/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formData),
    });
    const data = await response.json();
    localStorage.setItem("token", data.access_token);
    alert("Logged in successfully");
  };

  return (
    <div>
      <h2>Log In</h2>
      <input name="name" placeholder="Name" onChange={(e) => setFormData({ ...formData, name: e.target.value })} />
      <input name="password" placeholder="Password" type="password" onChange={(e) => setFormData({ ...formData, password: e.target.value })} />
      <button onClick={handleLogin}>Log In</button>
    </div>
  );
};

export default LoginPage;