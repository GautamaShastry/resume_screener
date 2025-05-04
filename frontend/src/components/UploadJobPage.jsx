import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import axios from 'axios';
import Loading from './Loading';

const UploadJobPage = () => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleUpload = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem('token');

    try {
      setIsLoading(true);
      const response = await axios.post('https://resume-screener-backend-hfz2.onrender.com/api/job/upload', { title, description }, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      localStorage.setItem('jobDescriptionId', response.data.jobDescriptionId);
      toast.success('Job Description uploaded successfully! Now match resume.');
      navigate('/match');
    } catch (error) {
      toast.error('Job description upload failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) return <Loading />;

  return (
    <div className="min-h-screen flex flex-col items-center justify-start pt-20 bg-gray-100 px-4">
      
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-purple-700 mb-2">Add Job Description</h1>
        <p className="text-gray-600">Provide a job title and detailed description to match it with your resume.</p>
      </div>

      <form onSubmit={handleUpload} className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h2 className="text-2xl font-bold mb-6 text-center">Add Job Description</h2>

        <div className="mb-4">
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">Job Title <span className='text-red-700'>*</span></label>
          <input
            id="title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Enter Job Title ..."
            required
            className="w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-purple-400"
          />
        </div>

        <div className="mb-6">
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">Job Description <span className='text-red-700'>*</span></label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Enter Job Description ..."
            required
            className="w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-purple-400"
            rows="5"
          ></textarea>
        </div>

        <button
          type="submit"
          className="w-full bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 rounded transition duration-200"
        >
          Add Job Description
        </button>
      </form>
    </div>
  );
};

export default UploadJobPage;
