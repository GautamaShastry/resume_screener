import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import axios from 'axios';

const UploadJobPage = () => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const navigate = useNavigate();

  const handleUpload = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem('token');

    try {
      const response = await axios.post('http://localhost:8000/api/job/upload', { title, description }, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      localStorage.setItem('jobDescriptionId', response.data.jobDescriptionId); // Save in localStorage
      toast.success('Job Description uploaded successfully! Now match resume.');
      navigate('/match');
    } catch (error) {
      toast.error('Job description upload failed. Please try again.');
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-start pt-20 bg-gray-100 px-4">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-purple-700 mb-2">Upload Job Description</h1>
        <p className="text-gray-600">Provide a job title and detailed description to match it with your resume.</p>
      </div>

      <form onSubmit={handleUpload} className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h2 className="text-2xl font-bold mb-4 text-center">Upload Job Description</h2>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Job Title"
          required
          className="w-full p-2 border rounded mb-4"
        />
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Job Description"
          required
          className="w-full p-2 border rounded mb-6"
          rows="5"
        ></textarea>
        <button
          type="submit"
          className="w-full bg-purple-600 hover:bg-purple-700 text-white font-semibold py-2 rounded"
        >
          Upload Job
        </button>
      </form>
    </div>
  );
};

export default UploadJobPage;
