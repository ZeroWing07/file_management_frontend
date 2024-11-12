import React, { useEffect, useState } from 'react';
import { useAuth } from '../components/AuthContext';

const ProtectedComponent = () => {
  const { authToken } = useAuth();
  const [data, setData] = useState(null);

  useEffect(() => {
      const fetchData = async () => {
          const response = await fetch("http://127.0.0.1:8000/protected-route/", {
              headers: {
                  "Authorization": `Bearer ${authToken}`
              }
          });
          const result = await response.json();
          setData(result);
      };

      if (authToken) {
          fetchData();
      }
  }, [authToken]);

  if (!authToken) return <p>Please log in to view this page.</p>;
  return <div>{data ? JSON.stringify(data) : "Loading..."}</div>;
};

export default ProtectedComponent;
