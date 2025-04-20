import { Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import SignupForm from './components/SignupForm';
import LoginForm from './components/LoginForm';
import UploadResumePage from './components/UploadResumePage';
import UploadJobPage from './components/UploadJobPage';
import MatchResumePage from './components/MatchResumePage';
import ResultPage from './components/ResultPage';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { useState } from 'react';

const App = () => {
  const [resumeId, setResumeId] = useState(null);
  const [jobDescriptionId, setJobDescriptionId] = useState(null);
  const token = localStorage.getItem('token');

  return (
    <>
      <Navbar />
      <ToastContainer position="top-center" />
      <Routes>
        <Route path="/" element={<Navigate to={token ? "/upload-resume" : "/login"} />} />
        <Route path="/signup" element={<SignupForm />} />
        <Route path="/login" element={<LoginForm />} />
        <Route path="/upload-resume" element={<UploadResumePage setResumeId={setResumeId} />} />
        <Route path="/upload-job" element={<UploadJobPage setJobDescriptionId={setJobDescriptionId} />} />
        <Route path="/match" element={<MatchResumePage resumeId={resumeId} jobDescriptionId={jobDescriptionId} />} />
        <Route path="/result" element={<ResultPage />} />
      </Routes>
    </>
  );
};

export default App;
