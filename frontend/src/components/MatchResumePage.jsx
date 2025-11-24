import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import axios from 'axios';
import { useState, useEffect } from 'react';
import Loading from './Loading';
import { FiZap, FiFileText, FiBriefcase, FiCheckCircle, FiArrowRight } from 'react-icons/fi';

const MatchResumePage = () => {
    const [isLoading, setIsLoading] = useState(false);
    const [resumeInfo, setResumeInfo] = useState(null);
    const [jobInfo, setJobInfo] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        // Fetch resume and job info to display
        const fetchDetails = async () => {
            const token = localStorage.getItem('token');
            const resumeId = localStorage.getItem('resumeId');
            const jobDescriptionId = localStorage.getItem('jobDescriptionId');

            if (!resumeId || !jobDescriptionId) {
                toast.error('Missing resume or job description!');
                navigate('/dashboard');
                return;
            }

            try {
                // Fetch resume details
                const resumeResponse = await axios.get(
                    `http://localhost:8001/api/resume/${resumeId}`,
                    { headers: { Authorization: `Bearer ${token}` } }
                );
                setResumeInfo(resumeResponse.data);

                // Fetch job description details
                const jobResponse = await axios.get(
                    `http://localhost:8001/api/job/${jobDescriptionId}`,
                    { headers: { Authorization: `Bearer ${token}` } }
                );
                setJobInfo(jobResponse.data);
            } catch (error) {
                console.error('Error fetching details:', error);
                // Continue even if fetch fails - user can still match
            }
        };

        fetchDetails();
    }, [navigate]);

    const handleMatch = async (e) => {
        e.preventDefault();
        const token = localStorage.getItem('token');
        const resumeId = localStorage.getItem('resumeId');
        const jobDescriptionId = localStorage.getItem('jobDescriptionId');

        if (!resumeId || !jobDescriptionId) {
            toast.error('Resume or Job description not uploaded yet!');
            navigate('/dashboard');
            return;
        }

        try {
            setIsLoading(true);
            const response = await axios.post(
                `http://localhost:8001/api/match/matchResume?resumeId=${resumeId}&jobDescriptionId=${jobDescriptionId}`,
                {},
                { headers: { Authorization: `Bearer ${token}` } }
            );
            navigate('/result', { state: response.data });
        } catch (error) {
            toast.error('Matching failed. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    if (isLoading) return <Loading />;

    return (
        <div className="min-h-screen bg-gradient-to-br from-yellow-50 to-gray-100 flex flex-col items-center justify-start pt-12 px-4 pb-12">
            {/* Header Section */}
            <div className="text-center mb-8 max-w-3xl">
                <div className="inline-block p-3 bg-yellow-100 rounded-full mb-4">
                    <FiZap className="w-12 h-12 text-yellow-600" />
                </div>
                <h1 className="text-4xl font-bold text-gray-800 mb-3">Ready to Analyze!</h1>
                <p className="text-lg text-gray-600">
                    Your resume and job description are ready. Let's see how well they match!
                </p>
            </div>

            {/* Summary Cards */}
            <div className="grid md:grid-cols-2 gap-6 w-full max-w-5xl mb-8">
                {/* Resume Card */}
                <div className="bg-white rounded-xl shadow-lg p-6 border-t-4 border-blue-500">
                    <div className="flex items-center mb-4">
                        <div className="bg-blue-100 p-3 rounded-full mr-4">
                            <FiFileText className="w-6 h-6 text-blue-600" />
                        </div>
                        <div>
                            <h3 className="text-lg font-bold text-gray-800">Your Resume</h3>
                            <p className="text-sm text-gray-500">Document uploaded</p>
                        </div>
                    </div>
                    {resumeInfo ? (
                        <div className="space-y-2">
                            <div className="flex items-center text-sm">
                                <FiCheckCircle className="text-green-500 mr-2" />
                                <span className="text-gray-700">
                                    {resumeInfo.fileName || 'Resume uploaded'}
                                </span>
                            </div>
                            {resumeInfo.uploadedAt && (
                                <p className="text-xs text-gray-500">
                                    Uploaded: {new Date(resumeInfo.uploadedAt).toLocaleDateString()}
                                </p>
                            )}
                        </div>
                    ) : (
                        <div className="flex items-center text-sm text-green-600">
                            <FiCheckCircle className="mr-2" />
                            <span>Resume successfully uploaded</span>
                        </div>
                    )}
                </div>

                {/* Job Description Card */}
                <div className="bg-white rounded-xl shadow-lg p-6 border-t-4 border-purple-500">
                    <div className="flex items-center mb-4">
                        <div className="bg-purple-100 p-3 rounded-full mr-4">
                            <FiBriefcase className="w-6 h-6 text-purple-600" />
                        </div>
                        <div>
                            <h3 className="text-lg font-bold text-gray-800">Job Description</h3>
                            <p className="text-sm text-gray-500">Target position</p>
                        </div>
                    </div>
                    {jobInfo ? (
                        <div className="space-y-2">
                            <div className="flex items-center text-sm">
                                <FiCheckCircle className="text-green-500 mr-2" />
                                <span className="text-gray-700 font-medium">
                                    {jobInfo.title || 'Job description added'}
                                </span>
                            </div>
                            {jobInfo.description && (
                                <p className="text-xs text-gray-600 line-clamp-2">
                                    {jobInfo.description.substring(0, 100)}...
                                </p>
                            )}
                        </div>
                    ) : (
                        <div className="flex items-center text-sm text-green-600">
                            <FiCheckCircle className="mr-2" />
                            <span>Job description successfully added</span>
                        </div>
                    )}
                </div>
            </div>

            {/* Main Action Card */}
            <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-3xl">
                <div className="text-center mb-8">
                    <h2 className="text-2xl font-bold text-gray-800 mb-3">
                        Everything is Ready!
                    </h2>
                    <p className="text-gray-600">
                        Click the button below to start the AI-powered analysis
                    </p>
                </div>

                {/* What You'll Get Section */}
                <div className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-xl p-6 mb-8">
                    <h3 className="font-semibold text-gray-800 mb-4 text-center">
                        What you'll get in the analysis:
                    </h3>
                    <div className="grid md:grid-cols-2 gap-4">
                        <div className="flex items-start space-x-3">
                            <div className="bg-yellow-400 rounded-full p-1 mt-1">
                                <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                </svg>
                            </div>
                            <div>
                                <p className="font-medium text-gray-800">Match Score</p>
                                <p className="text-sm text-gray-600">Overall compatibility percentage</p>
                            </div>
                        </div>
                        <div className="flex items-start space-x-3">
                            <div className="bg-yellow-400 rounded-full p-1 mt-1">
                                <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                </svg>
                            </div>
                            <div>
                                <p className="font-medium text-gray-800">Key Strengths</p>
                                <p className="text-sm text-gray-600">What makes you a good fit</p>
                            </div>
                        </div>
                        <div className="flex items-start space-x-3">
                            <div className="bg-yellow-400 rounded-full p-1 mt-1">
                                <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                </svg>
                            </div>
                            <div>
                                <p className="font-medium text-gray-800">Areas to Improve</p>
                                <p className="text-sm text-gray-600">Skills you might need to add</p>
                            </div>
                        </div>
                        <div className="flex items-start space-x-3">
                            <div className="bg-yellow-400 rounded-full p-1 mt-1">
                                <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                </svg>
                            </div>
                            <div>
                                <p className="font-medium text-gray-800">Detailed Reports</p>
                                <p className="text-sm text-gray-600">PDF & HTML downloadable reports</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Match Button */}
                <form onSubmit={handleMatch}>
                    <button
                        type="submit"
                        className="w-full bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600 text-white font-bold py-5 rounded-xl transition duration-200 transform hover:scale-105 shadow-lg flex items-center justify-center text-lg"
                    >
                        <FiZap className="mr-2 text-2xl" />
                        Start AI Analysis
                        <FiArrowRight className="ml-2 text-2xl" />
                    </button>
                </form>

                <p className="text-center text-sm text-gray-500 mt-4">
                    Analysis typically takes 10-30 seconds
                </p>
            </div>

            {/* Info Note */}
            <div className="mt-8 max-w-3xl bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start">
                <svg className="w-5 h-5 text-blue-600 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                <p className="text-sm text-blue-800">
                    Your data is secure and will only be used for this analysis. You can download detailed reports after the analysis is complete.
                </p>
            </div>
        </div>
    );
};

export default MatchResumePage;