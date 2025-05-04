import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import axios from 'axios';
import { useState } from 'react';
import Loading from './Loading';

const MatchResumePage = () => {
    const [isLoading, setIsLoading] = useState(false); // loading state
    const navigate = useNavigate();

    const handleMatch = async (e) => {
        e.preventDefault();
        const token = localStorage.getItem('token');
        const resumeId = localStorage.getItem('resumeId'); 
        const jobDescriptionId = localStorage.getItem('jobDescriptionId'); 

        if (!resumeId || !jobDescriptionId) {
        toast.error('Resume or Job description not uploaded yet!');
        return;
        }

        try {
            setIsLoading(true); // Set loading state to true
            const response = await axios.post(
                `https://resume-screener-backend-hfz2.onrender.com/api/match/matchResume?resumeId=${resumeId}&jobDescriptionId=${jobDescriptionId}`,
                {}, // empty body, request is sent as params
                {
                headers: { Authorization: `Bearer ${token}` }
                }
            );
            navigate('/result', { state: response.data });
        } catch (error) {
        toast.error('Matching failed. Please try again.');
        } finally {
            setIsLoading(false); // Reset loading state
        }
    };

    if(isLoading) return <Loading />; // Show loading component while matching

    return (
        <div className="min-h-screen flex flex-col items-center justify-start pt-20 bg-gray-100 px-4">
        <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-yellow-700 mb-2">Ready to Match!</h1>
            <p className="text-gray-600">Click the button below to match your uploaded resume with the job description.</p>
        </div>

        <form onSubmit={handleMatch} className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
            <button
            type="submit"
            className="w-full bg-yellow-600 hover:bg-yellow-700 text-white font-semibold py-2 rounded"
            >
            Match Now
            </button>
        </form>
        </div>
    );
};

export default MatchResumePage;
