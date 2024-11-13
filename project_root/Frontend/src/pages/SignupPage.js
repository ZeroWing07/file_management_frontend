import React, { useState, useRef } from 'react';
import axios from 'axios';
import CanvasComponent from '../components/CanvasComponent';
import BackButton from '../components/BackButton';
import '../App.css';

const SignupPage = () => {
  const [name, setName] = useState('');
  const [age, setAge] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const canvasRef = useRef(null);

  const handleSignup = async () => {
    if (canvasRef.current) {
      const signatureDataUrl = canvasRef.current.toDataURL();
  
      // Prepare form data, including the signature image
      const userData = {
        name,
        age,
        password,
        signature: signatureDataUrl,
      };
  
      try {
        const response = await axios.post('http://localhost:8000/signup', userData);
        if (response.status === 200) {
          alert('Signup successful!');
        }
      } catch (error) {
        console.error('Signup failed:', error.response ? error.response.data : error.message);
        alert(error.response?.data?.detail || 'Signup failed. Please try again.');
      }
    } else {
      alert("Signature canvas is not available.");
    }
  };

  const handleClearCanvas = () => {
    if (canvasRef.current) {
      canvasRef.current.clearCanvas(); // Clear the canvas
    }
  };

  return (
    <div className="signup-container">
      <h1>Signup</h1>
      <input type="text" placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} />
      <input type="number" placeholder="Age" value={age} onChange={(e) => setAge(e.target.value)} />
      <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
      <input type="password" placeholder="Confirm Password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} />
      
      <h3>Draw your signature:</h3>
      <CanvasComponent ref={canvasRef} width={200} height={200} />
      <button onClick={handleClearCanvas}>Clear Canvas</button> {/* Clear Canvas Button */}

      <button onClick={handleSignup}>Sign Up</button>
      <BackButton />
    </div>
  );
};

export default SignupPage;
