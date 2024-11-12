import React from 'react';
import ReactDOM from 'react-dom/client'; // Update this import
import App from './App';
import { AuthProvider } from './components/AuthContext';

const root = ReactDOM.createRoot(document.getElementById('root')); // Use createRoot
root.render(
    <AuthProvider>
        <App />
    </AuthProvider>
);
