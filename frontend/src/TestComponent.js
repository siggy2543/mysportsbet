import React, { useState, useEffect } from 'react';

const TestComponent = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    console.log('🚀 TestComponent mounted, starting API test...');
    
    const testAPI = async () => {
      try {
        console.log('📡 Fetching from API...');
        const response = await fetch('http://localhost:8000/api/health');
        console.log('📡 Response:', response.status, response.statusText);
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        
        const result = await response.json();
        console.log('✅ API data received:', result);
        setData(result);
        setError(null);
      } catch (err) {
        console.error('❌ API Error:', err.message);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    testAPI();
  }, []);

  if (loading) {
    return <div style={{padding: '20px'}}>🔄 Testing API connection...</div>;
  }

  if (error) {
    return <div style={{padding: '20px', color: 'red'}}>❌ API Error: {error}</div>;
  }

  return (
    <div style={{padding: '20px'}}>
      <h2>✅ API Connection Successful!</h2>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
};

export default TestComponent;