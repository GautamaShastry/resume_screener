import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import axios from 'axios';
import Loading from './Loading';

const UploadResumePage = () => {
    const [file, setFile] = useState(null);
    const [isLoading, setIsLoading] = useState(false); // loading state
    const navigate = useNavigate();

    const handleUpload = async (e) => {
        e.preventDefault();
        if (!file) {
            toast.error('Please upload a resume');
            return;
        }

        const token = localStorage.getItem('token');
        const formData = new FormData();
        formData.append('file', file);

        try {
            setIsLoading(true); // Set loading state to true
            const response = await axios.post('http://localhost:8001/api/resume/upload', formData, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'multipart/form-data'
                }
            });
            localStorage.setItem('resumeId', response.data.resumeId); // Save in localStorage, since when I'm trying to re-render the page, this data is not available
            toast.success('Resume uploaded successfully! Please upload Job Description next.');
            navigate('/upload-job');
        } catch (error) {
            toast.error('Resume upload failed. Please try again.');
        } finally {
            setIsLoading(false); // Reset loading state
        }
    };

    if(isLoading) return <Loading />; // Show loading component while uploading

    return (
        <div className="min-h-screen flex flex-col items-center justify-start pt-20 bg-gray-100 px-4">
            <div className="text-center mb-8">
                <h1 className="text-3xl font-bold text-blue-700 mb-2">Upload Your Resume</h1>
                <p className="text-gray-600">Please upload your resume (PDF or DOCX format) to continue the analysis.</p>
            </div>

            <form onSubmit={handleUpload} className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
                <h2 className="text-2xl font-bold mb-4 text-center">Upload Resume</h2>
                <input
                    type="file"
                    onChange={(e) => setFile(e.target.files[0])}
                    required
                    className="w-full p-2 border rounded mb-6"
                />
                <button
                    type="submit"
                    className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-2 rounded"
                >
                    Upload Resume
                </button>
            </form>
        </div>
    );
};

export default UploadResumePage;
