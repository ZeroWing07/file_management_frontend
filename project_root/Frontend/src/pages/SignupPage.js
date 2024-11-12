// SignupPage.js
import React, { useState, useRef } from 'react';

const SignupPage = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirmPassword: '',
    name: '',
    age: '',
  });
  const [errorMessage, setErrorMessage] = useState('');
  const canvasRef = useRef(null);

  // Handle form input changes
  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  // Clear the canvas
  const clearCanvas = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  };

  // Capture signature drawing
  const handleCanvasDraw = (e) => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
    ctx.strokeStyle = '#000';
    ctx.beginPath();
    ctx.moveTo(e.nativeEvent.offsetX, e.nativeEvent.offsetY);

    const draw = (event) => {
      ctx.lineTo(event.nativeEvent.offsetX, event.nativeEvent.offsetY);
      ctx.stroke();
    };

    const stopDrawing = () => {
      canvas.removeEventListener('mousemove', draw);
      canvas.removeEventListener('mouseup', stopDrawing);
    };

    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', stopDrawing);
  };

  // Handle form submission
  const handleSubmit = async () => {
    if (formData.password !== formData.confirmPassword) {
      setErrorMessage("Passwords do not match");
      return;
    }
    
    // Convert canvas drawing to data URL
    const canvas = canvasRef.current;
    const signature = canvas.toDataURL('image/png');
    
    const response = await fetch("http://localhost:8000/signup/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...formData, signature }),
    });
    const data = await response.json();
    
    if (response.ok) {
      alert(data.message);
    } else {
      setErrorMessage(data.detail || "There was an error with your request.");
    }
  };

  return (
    <div className="form-container">
      <h2>Sign Up</h2>
      <input name="username" placeholder="Username" onChange={handleChange} />
      <input name="name" placeholder="Full Name" onChange={handleChange} />
      <input name="age" placeholder="Age" type="number" onChange={handleChange} />
      <input name="password" placeholder="Password" type="password" onChange={handleChange} />
      <input name="confirmPassword" placeholder="Confirm Password" type="password" onChange={handleChange} />
      
      {errorMessage && <p className="error-message">{errorMessage}</p>}
      
      <h3>Signature:</h3>
      <canvas
        ref={canvasRef}
        width={300}
        height={150}
        style={{ border: '1px solid black' }}
        onMouseDown={handleCanvasDraw}
      />
      <button onClick={clearCanvas}>Clear Signature</button>
      
      <button onClick={handleSubmit}>Submit</button>
    </div>
  );
};

export default SignupPage;
