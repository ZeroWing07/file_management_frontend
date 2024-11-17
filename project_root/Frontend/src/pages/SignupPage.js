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
      // Convert canvas to Data URL (Base64 encoded)
      const signatureDataUrl = canvasRef.current.toDataURL();

      // Convert Base64 to a Blob
      const byteString = atob(signatureDataUrl.split(',')[1]); // Decode Base64
      const mimeString = signatureDataUrl.split(',')[0].split(':')[1].split(';')[0]; // Get MIME type
      const arrayBuffer = new ArrayBuffer(byteString.length);
      const uintArray = new Uint8Array(arrayBuffer);

      for (let i = 0; i < byteString.length; i++) {
        uintArray[i] = byteString.charCodeAt(i);
      }

      const blob = new Blob([uintArray], { type: mimeString });

      // Create a URL for the Blob and open it in a new tab
      const blobUrl = URL.createObjectURL(blob);
      window.open(blobUrl, '_blank');

      // Prepare JSON payload with the Base64 signature and other user data
      const userData = {
        username: name, // Assume `name` is the username field
        age,
        password,
        signature: signatureDataUrl, // Send the image as a Base64 string
      };

      console.log(userData);

      try {
        // Send the JSON data as a POST request
        const response = await axios.post('http://localhost:8000/signup', userData, {
          headers: {
            'Content-Type': 'application/json',
          },
        });

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
