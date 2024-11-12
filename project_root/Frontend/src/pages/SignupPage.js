import React, { useState, useRef } from 'react';
import axios from 'axios';
import CanvasComponent from '../components/CanvasComponent';
import BackButton from '../components/BackButton';
import '../App.css'

const SignupPage = () => {
  const [name, setName] = useState('');
  const [age, setAge] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const canvasRef = useRef(null);

  const handleSignup = async () => {
    if (canvasRef.current) {  // Check if canvasRef.current is defined
      const signatureDataUrl = canvasRef.current.toDataURL();

      // Prepare form data, including the signature image
      const userData = {
        name,
        age,
        password,
        signature: signatureDataUrl,  // Include the signature image data as a URL
      };

      try {
        const response = await axios.post('http://localhost:8000/signup', userData);
        if (response.status === 200) {
          alert('Signup successful!');
          // Redirect to login or another page if needed
        }
      } catch (error) {
        console.error('Signup failed', error);
        alert('Signup failed. Please try again.');
      }
    } else {
      alert("Signature canvas is not available.");
    }
  };

  return (
    <div>
      <h1>Signup</h1>
      <input type="text" placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} />
      <input type="number" placeholder="Age" value={age} onChange={(e) => setAge(e.target.value)} />
      <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
      <input type="password" placeholder="Confirm Password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} />
      
      <h3>Draw your signature:</h3>
      <CanvasComponent ref={canvasRef} width={300} height={100} />

      <button onClick={handleSignup}>Sign Up</button>
      <BackButton />
    </div>
  );
};

export default SignupPage;
