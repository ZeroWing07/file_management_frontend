import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import BackButton from '../components/BackButton';


const UploadedFilesPage = () => {
  const [files, setFiles] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    axios.get("http://localhost:8000/files", {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    })
    .then(response => setFiles(response.data))
    .catch(error => console.error("Error fetching files:", error));
  }, []);

  const handleFileSelect = (fileId) => {
    navigate(`/decryptor/${fileId}`);
  };

  return (
    <div>
      <h2>Uploaded Files</h2>
      <ul>
        {files.map(file => (
          <li key={file.id} onClick={() => handleFileSelect(file.id)}>
            {file.filename}
          </li>
        ))}
      </ul>
      <BackButton/>
    </div>
  );
};

export default UploadedFilesPage;
