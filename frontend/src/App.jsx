import { Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import LandingPage from './components/LandingPage';
import SignupForm from './components/SignupForm';
import LoginForm from './components/LoginForm';
import Dashboard from './components/Dashboard';
import UploadResumePage from './components/UploadResumePage';
import UploadJobPage from './components/UploadJobPage';
import MatchResumePage from './components/MatchResumePage';
import ResultPage from './components/ResultPage';
import MatchHistory from './components/MatchHistory';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { useState, useEffect } from 'react';

const App = () => {
  const [resumeId, setResumeId] = useState(null);
  const [jobDescriptionId, setJobDescriptionId] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));

  // Listen for storage changes to update token state
  useEffect(() => {
    const handleStorageChange = () => {
      setToken(localStorage.getItem('token'));
    };
    window.addEventListener('storage', handleStorageChange);
    // Also check periodically for same-tab changes
    const interval = setInterval(handleStorageChange, 100);
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      clearInterval(interval);
    };
  }, []);

  return (
    <>
      <Navbar />
      <ToastContainer 
        position="top-center" 
        theme="dark"
        toastStyle={{
          backgroundColor: '#1e293b',
          border: '1px solid rgba(255,255,255,0.1)',
          borderRadius: '12px',
        }}
      />
      <Routes>
        <Route path="/" element={token ? <Navigate to="/dashboard" /> : <LandingPage />} />
        <Route path="/signup" element={<SignupForm />} />
        <Route path="/login" element={<LoginForm />} />
        <Route path="/dashboard" element={token ? <Dashboard /> : <Navigate to="/login" />} />
        <Route path="/upload-resume" element={token ? <UploadResumePage setResumeId={setResumeId} /> : <Navigate to="/login" />} />
        <Route path="/upload-job" element={token ? <UploadJobPage setJobDescriptionId={setJobDescriptionId} /> : <Navigate to="/login" />} />
        <Route path="/match" element={token ? <MatchResumePage resumeId={resumeId} jobDescriptionId={jobDescriptionId} /> : <Navigate to="/login" />} />
        <Route path="/result" element={token ? <ResultPage /> : <Navigate to="/login" />} />
        <Route path="/history" element={token ? <MatchHistory /> : <Navigate to="/login" />} />
      </Routes>
    </>
  );
};

export default App;
