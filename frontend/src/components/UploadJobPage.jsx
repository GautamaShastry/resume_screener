import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import axios from 'axios';
import Loading from './Loading';
import { FiBriefcase, FiAlertCircle, FiCheckCircle } from 'react-icons/fi';

const UploadJobPage = () => {
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [showExample, setShowExample] = useState(false);
    const navigate = useNavigate();

    const exampleJob = {
        title: "Senior Software Engineer",
        description: `We are seeking a talented Senior Software Engineer to join our growing team.

Key Responsibilities:
- Design and develop scalable web applications
- Lead technical discussions and code reviews
- Mentor junior developers
- Collaborate with cross-functional teams

Required Skills:
- 5+ years of software development experience
- Strong proficiency in JavaScript, React, Node.js
- Experience with cloud platforms (AWS/Azure)
- Excellent problem-solving skills

Preferred Qualifications:
- Master's degree in Computer Science
- Experience with microservices architecture
- Knowledge of DevOps practices`
    };

    const handleUseExample = () => {
        setTitle(exampleJob.title);
        setDescription(exampleJob.description);
        setShowExample(false);
        toast.info('Example loaded! Feel free to modify it.');
    };

    const handleUpload = async (e) => {
        e.preventDefault();
        
        if (description.length < 100) {
            toast.error('Job description should be at least 100 characters');
            return;
        }

        const token = localStorage.getItem('token');

        try {
            setIsLoading(true);
            const response = await axios.post('http://localhost:8001/api/job/upload', 
                { title, description }, 
                { headers: { 'Authorization': `Bearer ${token}` } }
            );
            localStorage.setItem('jobDescriptionId', response.data.jobDescriptionId);
            toast.success('Job Description uploaded successfully! Now match resume.');
            navigate('/match');
        } catch (error) {
            toast.error('Job description upload failed. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const getCharacterCountColor = () => {
        if (description.length < 100) return 'text-red-500';
        if (description.length < 300) return 'text-yellow-500';
        return 'text-green-500';
    };

    if (isLoading) return <Loading />;

    return (
        <div className="min-h-screen bg-gradient-to-br from-purple-50 to-gray-100 flex flex-col items-center justify-start pt-12 px-4 pb-12">
            {/* Header Section */}
            <div className="text-center mb-8 max-w-2xl">
                <div className="inline-block p-3 bg-purple-100 rounded-full mb-4">
                    <FiBriefcase className="w-12 h-12 text-purple-600" />
                </div>
                <h1 className="text-4xl font-bold text-gray-800 mb-3">Add Job Description</h1>
                <p className="text-lg text-gray-600">
                    Provide the job details to get a tailored resume analysis
                </p>
            </div>

            {/* Main Form Container */}
            <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-3xl">
                <form onSubmit={handleUpload}>
                    {/* Job Title Input */}
                    <div className="mb-6">
                        <label htmlFor="title" className="block text-sm font-semibold text-gray-700 mb-2">
                            Job Title <span className='text-red-600'>*</span>
                        </label>
                        <input
                            id="title"
                            type="text"
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            placeholder="e.g., Senior Software Engineer, Marketing Manager"
                            required
                            className="w-full p-4 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition duration-200"
                        />
                    </div>

                    {/* Job Description Textarea */}
                    <div className="mb-4">
                        <div className="flex justify-between items-center mb-2">
                            <label htmlFor="description" className="block text-sm font-semibold text-gray-700">
                                Job Description <span className='text-red-600'>*</span>
                            </label>
                            <button
                                type="button"
                                onClick={() => setShowExample(!showExample)}
                                className="text-sm text-purple-600 hover:text-purple-700 font-medium"
                            >
                                {showExample ? 'Hide Example' : 'View Example'}
                            </button>
                        </div>

                        {/* Example Box */}
                        {showExample && (
                            <div className="mb-4 bg-purple-50 border-2 border-purple-200 rounded-lg p-4">
                                <div className="flex justify-between items-start mb-2">
                                    <h4 className="font-semibold text-purple-800">Example Job Posting:</h4>
                                    <button
                                        type="button"
                                        onClick={handleUseExample}
                                        className="text-sm bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 rounded"
                                    >
                                        Use This
                                    </button>
                                </div>
                                <p className="text-sm text-gray-700 font-medium mb-1">{exampleJob.title}</p>
                                <p className="text-xs text-gray-600 whitespace-pre-line">{exampleJob.description.substring(0, 200)}...</p>
                            </div>
                        )}

                        <textarea
                            id="description"
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            placeholder="Paste the complete job description here including responsibilities, requirements, qualifications, etc."
                            required
                            className="w-full p-4 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition duration-200 min-h-[300px] resize-y"
                        ></textarea>

                        {/* Character Count */}
                        <div className="flex justify-between items-center mt-2">
                            <div className="flex items-center space-x-2">
                                {description.length >= 100 ? (
                                    <FiCheckCircle className="text-green-500" />
                                ) : (
                                    <FiAlertCircle className="text-yellow-500" />
                                )}
                                <span className={`text-sm font-medium ${getCharacterCountColor()}`}>
                                    {description.length} characters
                                    {description.length < 100 && ` (minimum 100 required)`}
                                </span>
                            </div>
                            <span className="text-xs text-gray-500">
                                Recommended: 300-1000 characters
                            </span>
                        </div>
                    </div>

                    {/* Submit Button */}
                    <button
                        type="submit"
                        disabled={description.length < 100}
                        className={`w-full font-semibold py-4 rounded-lg transition duration-200 transform hover:scale-105 shadow-lg ${
                            description.length >= 100
                                ? 'bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white'
                                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                        }`}
                    >
                        Continue to Match →
                    </button>
                </form>

                {/* Progress Indicator */}
                <div className="grid md:grid-cols-3 gap-4 mt-8">
                    <div className="bg-green-50 p-4 rounded-lg text-center border-2 border-green-200">
                        <div className="text-2xl font-bold text-green-600 mb-1">✓</div>
                        <p className="text-sm text-gray-700">Resume Uploaded</p>
                    </div>
                    <div className="bg-purple-50 p-4 rounded-lg text-center border-2 border-purple-200">
                        <div className="text-2xl font-bold text-purple-600 mb-1">2</div>
                        <p className="text-sm text-gray-700 font-semibold">Add Job Description</p>
                    </div>
                    <div className="bg-gray-100 p-4 rounded-lg text-center">
                        <div className="text-2xl font-bold text-gray-400 mb-1">3</div>
                        <p className="text-sm text-gray-500">Get Analysis</p>
                    </div>
                </div>
            </div>

            {/* Tips Section */}
            <div className="mt-8 max-w-3xl bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h3 className="font-semibold text-blue-800 mb-3 flex items-center">
                    <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                    </svg>
                    Tips for accurate analysis:
                </h3>
                <ul className="text-sm text-blue-800 space-y-2">
                    <li className="flex items-start">
                        <span className="mr-2">•</span>
                        <span>Include the complete job description with all requirements and qualifications</span>
                    </li>
                    <li className="flex items-start">
                        <span className="mr-2">•</span>
                        <span>Add specific skills, technologies, and tools mentioned in the posting</span>
                    </li>
                    <li className="flex items-start">
                        <span className="mr-2">•</span>
                        <span>Include information about required experience level and education</span>
                    </li>
                </ul>
            </div>
        </div>
    );
};

export default UploadJobPage;