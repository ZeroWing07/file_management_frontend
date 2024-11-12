// import React, { useState } from 'react';
// import CanvasComponent from '../components/CanvasComponent';
// import DarkModeToggle from '../components/DarkModeToggle';
// import '../App.css';
// import BackButton from '../components/BackButton';

// const SignupPage = () => {
//   const [formData, setFormData] = useState({ name: '', age: '', password: '', confirmPassword: '' });

//   const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

//   const handleSubmit = () => {
//     // Handle signup logic
//   };

//   return (
//     <div className="form-container">
//       <BackButton />
//       <DarkModeToggle />
//       <h2>Sign Up</h2>
//       <input className="form-input" name="name" placeholder="Name" onChange={handleChange} />
//       <input className="form-input" name="age" placeholder="Age" type="number" onChange={handleChange} />
//       <input className="form-input" name="password" placeholder="Password" type="password" onChange={handleChange} />
//       <input className="form-input" name="confirmPassword" placeholder="Confirm Password" type="password" onChange={handleChange} />
//       <CanvasComponent width={300} height={300} />
//       <button className="form-button" onClick={handleSubmit}>Submit</button>
//     </div>
//   );
// };

// export default SignupPage;

// pages/SignupPage.js
import React, { useState } from 'react';

const SignupPage = () => {
  const [formData, setFormData] = useState({ name: '', password: '' });

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = async () => {
    const response = await fetch("http://localhost:8000/signup/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formData),
    });
    const data = await response.json();
    alert(data.message);
  };

  return (
    <div>
      <h2>Sign Up</h2>
      <input name="name" placeholder="Name" onChange={handleChange} />
      <input name="password" placeholder="Password" type="password" onChange={handleChange} />
      <button onClick={handleSubmit}>Submit</button>
    </div>
  );
};

export default SignupPage;