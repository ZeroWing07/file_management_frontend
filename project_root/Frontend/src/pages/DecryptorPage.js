import React, { useState, useRef } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import CanvasComponent from '../components/CanvasComponent';
import '../App.css';
import BackButton from '../components/BackButton';

const DecryptorPage = () => {
  const { fileId } = useParams();
  const [isDecrypting, setIsDecrypting] = useState(false);
  const [decryptedFile, setDecryptedFile] = useState(null);
  const [error, setError] = useState(null);
  const canvasRef = useRef(null);

  const handleDecrypt = async () => {
    try {
      setIsDecrypting(true);
      setError(null);

      // Get the token from localStorage
      const token = localStorage.getItem("token");
      if (!token) {
        throw new Error("Token not found. Please login first.");
      }

      // Decode the token to extract the username
      const decodedToken = JSON.parse(atob(token.split(".")[1]));
      const username = decodedToken?.sub;
      if (!username) {
        throw new Error("Username not found in token. Please login again.");
      }

      // Get the signature from the canvas
      const canvas = canvasRef.current;
      if (!canvas) {
        throw new Error("Signature canvas not found. Please sign again.");
      }

      const signature = canvas.toDataURL("image/png");

      // Call the decrypt-file endpoint using Axios
      const response = await axios.post(
        `http://localhost:8000/decrypt-file/${fileId}`,
        {
          username: username,
          signature: signature,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
          responseType: 'blob', // Important: tells axios to handle the response as a blob
        }
      );

      // Create a blob URL for the decrypted file
      const file = new File(
        [response.data],
        getFilenameFromHeader(response.headers['content-disposition']) || 'decrypted-file',
        { type: response.headers['content-type'] }
      );

      setDecryptedFile({
        blob: URL.createObjectURL(response.data),
        name: getFilenameFromHeader(response.headers['content-disposition']) || 'decrypted-file',
        type: response.headers['content-type']
      });

    } catch (error) {
      let errorMessage = "An error occurred during decryption. Please try again.";

      if (error.response) {
        // Try to parse error message from response
        if (error.response.data instanceof Blob) {
          // If the error response is a blob, read it
          const text = await error.response.data.text();
          try {
            const errorData = JSON.parse(text);
            errorMessage = errorData.detail || errorMessage;
          } catch (e) {
            errorMessage = text || errorMessage;
          }
        } else {
          errorMessage = error.response.data.detail || errorMessage;
        }
      } else if (error.message) {
        errorMessage = error.message;
      }

      setError(errorMessage);
    } finally {
      setIsDecrypting(false);
    }
  };

  // Helper function to extract filename from Content-Disposition header
  const getFilenameFromHeader = (contentDisposition) => {
    if (!contentDisposition) return null;
    const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(contentDisposition);
    if (matches != null && matches[1]) {
      return matches[1].replace(/['"]/g, '');
    }
    return null;
  };

  const handleDownload = () => {
    if (decryptedFile) {
      const link = document.createElement('a');
      link.href = decryptedFile.blob;
      link.download = decryptedFile.name;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  // Clean up the blob URL when component unmounts
  React.useEffect(() => {
    return () => {
      if (decryptedFile && decryptedFile.blob) {
        URL.revokeObjectURL(decryptedFile.blob);
      }
    };
  }, [decryptedFile]);

  const handleClearCanvas = () => {
    canvasRef.current.clearCanvas();
  };

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">Decrypt File</h2>

      <div className="mb-4">
        <CanvasComponent ref={canvasRef} width={300} height={300} />
        <div className="mt-2 space-x-2">
          <button
            onClick={handleClearCanvas}
            className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
          >
            Clear Signature
          </button>
        </div>
      </div>

      <div className="space-y-4">
        <button
          onClick={handleDecrypt}
          disabled={isDecrypting}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
        >
          {isDecrypting ? 'Decrypting...' : 'Decrypt File'}
        </button>

        {error && (
          <div className="text-red-500 p-2 bg-red-50 rounded">
            {error}
          </div>
        )}

        {decryptedFile && (
          <div className="p-4 bg-green-50 rounded">
            <p className="text-green-700 mb-2">File decrypted successfully!</p>
            <button
              onClick={handleDownload}
              className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
            >
              Download {decryptedFile.name}
            </button>
          </div>
        )}
      </div>

      <BackButton />
    </div>
  );
};

export default DecryptorPage;