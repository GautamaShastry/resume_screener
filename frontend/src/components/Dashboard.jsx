import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';
import Loading from './Loading';
import { FiAward, FiBarChart, FiCheckCircle, FiCpu, FiTarget } from 'react-icons/fi';

const Dashboard = () => {
    const [user, setUser] = useState({});
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchUserProfile = async () => {
        const token = localStorage.getItem('token');
        
        try {
            const response = await axios.get('http://localhost:8001/api/user/profile', {
            headers: { Authorization: `Bearer ${token}` }
            });
            setUser(response.data);
        } catch (error) {
            toast.error('Failed to load profile data');
        } finally {
            setIsLoading(false);
        }
        };

        fetchUserProfile();
    }, []);

    if (isLoading) return <Loading />;

    return (
        <div className="min-h-screen bg-gray-100">
        {/* Welcome Section */}
        <div className="bg-gradient-to-r from-blue-700 to-blue-500 text-white py-12 px-4">
            <div className="max-w-7xl mx-auto">
            <h1 className="text-3xl font-bold mb-2">Welcome, {user.name || 'User'}!</h1>
            <p className="text-blue-100 text-lg">Let's optimize your job search with AI-powered resume matching.</p>
            <div className="mt-8">
                <Link 
                to="/upload-resume" 
                className="bg-white text-blue-700 hover:bg-blue-50 px-6 py-3 rounded-lg font-semibold text-lg shadow-md transition duration-300"
                >
                Check Your Resume Score
                </Link>
            </div>
            </div>
        </div>

        {/* About the App Section */}
        <div className="max-w-7xl mx-auto px-4 py-12 bg-white shadow-sm mt-8 rounded-lg">
            <h2 className="text-3xl font-bold text-center mb-8 text-gray-800">About Resume Analyzer</h2>
            
            <div className="grid md:grid-cols-2 gap-8 mb-12">
            <div className="flex flex-col items-center text-center p-6 bg-blue-50 rounded-lg">
                <FiCpu className="w-12 h-12 text-blue-600 mb-4" />
                <h3 className="text-xl font-semibold mb-2">AI-Powered Analysis</h3>
                <p className="text-gray-600">
                Our advanced AI analyzes your resume against job descriptions to identify strengths and weaknesses, 
                helping you optimize your application for each position.
                </p>
            </div>
            
            <div className="flex flex-col items-center text-center p-6 bg-green-50 rounded-lg">
                <FiBarChart className="w-12 h-12 text-green-600 mb-4" />
                <h3 className="text-xl font-semibold mb-2">Match Score</h3>
                <p className="text-gray-600">
                Get a detailed match score that shows how well your resume aligns with specific job requirements,
                along with actionable insights to improve your chances.
                </p>
            </div>
            
            <div className="flex flex-col items-center text-center p-6 bg-purple-50 rounded-lg">
                <FiTarget className="w-12 h-12 text-purple-600 mb-4" />
                <h3 className="text-xl font-semibold mb-2">Skill Gap Analysis</h3>
                <p className="text-gray-600">
                Identify missing skills and keywords that are crucial for the jobs you're targeting,
                helping you tailor your resume for maximum impact.
                </p>
            </div>
            
            <div className="flex flex-col items-center text-center p-6 bg-yellow-50 rounded-lg">
                <FiAward className="w-12 h-12 text-yellow-600 mb-4" />
                <h3 className="text-xl font-semibold mb-2">Career Advancement</h3>
                <p className="text-gray-600">
                Track your progress over time, build a stronger resume, and increase your chances of 
                landing interviews for your dream jobs.
                </p>
            </div>
            </div>
            
            {/* How It Works Section */}
            <h2 className="text-2xl font-bold text-center mb-6 text-gray-800">How It Works</h2>
            
            <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="flex flex-col items-center text-center">
                <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white text-xl font-bold mb-4">1</div>
                <h3 className="text-lg font-semibold mb-2">Upload Your Resume</h3>
                <p className="text-gray-600">Upload your resume in PDF or DOCX format to our secure platform.</p>
            </div>
            
            <div className="flex flex-col items-center text-center">
                <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white text-xl font-bold mb-4">2</div>
                <h3 className="text-lg font-semibold mb-2">Add Job Description</h3>
                <p className="text-gray-600">Paste the job description text you want to match against.</p>
            </div>
            
            <div className="flex flex-col items-center text-center">
                <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white text-xl font-bold mb-4">3</div>
                <h3 className="text-lg font-semibold mb-2">Get Your Score</h3>
                <p className="text-gray-600">Receive a detailed analysis with score, strengths, and improvement areas.</p>
            </div>
            </div>
            
            <div className="text-center mt-8">
            <Link 
                to="/upload-resume" 
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold inline-flex items-center"
            >
                <FiCheckCircle className="mr-2" /> Start Analyzing Now
            </Link>
            </div>
        </div>

        {/* Dashboard Cards */}
        <div className="max-w-7xl mx-auto px-4 py-8 mt-4">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Quick Actions</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Card 1 */}
            <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300">
                <div className="p-6">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mb-4">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                </div>
                <h3 className="text-xl font-semibold mb-2">Upload Resume</h3>
                <p className="text-gray-600 mb-4">Upload your resume and get it analyzed.</p>
                <Link to="/upload-resume" className="bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded inline-block font-medium">
                    Upload Resume
                </Link>
                </div>
            </div>

            {/* Card 2 */}
            <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300">
                <div className="p-6">
                <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mb-4">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                </div>
                <h3 className="text-xl font-semibold mb-2">Add Job Description</h3>
                <p className="text-gray-600 mb-4">Add a job description to match against your resume.</p>
                <Link to="/upload-job" className="bg-purple-600 hover:bg-purple-700 text-white py-2 px-4 rounded inline-block font-medium">
                    Add Job
                </Link>
                </div>
            </div>

            {/* Card 3 */}
            <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300">
                <div className="p-6">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-4">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                </div>
                <h3 className="text-xl font-semibold mb-2">Match History</h3>
                <p className="text-gray-600 mb-4">View your previous resume-job matches.</p>
                <Link to="/history" className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded inline-block font-medium">
                    View History
                </Link>
                </div>
            </div>
            </div>
        </div>

        {/* Stats Section */}
        <div className="max-w-7xl mx-auto px-4 py-8">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Your Activity</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center justify-between mb-2">
                <h3 className="text-gray-500 font-medium">Resumes</h3>
                <span className="text-2xl font-bold text-blue-600">{user.resumeCount || 0}</span>
                </div>
                <div className="w-full bg-gray-200 h-1 rounded-full overflow-hidden">
                <div className="bg-blue-600 h-1" style={{ width: `${Math.min((user.resumeCount || 0) * 10, 100)}%` }}></div>
                </div>
            </div>
            
            <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center justify-between mb-2">
                <h3 className="text-gray-500 font-medium">Job Descriptions</h3>
                <span className="text-2xl font-bold text-purple-600">{user.jobDescriptionCount || 0}</span>
                </div>
                <div className="w-full bg-gray-200 h-1 rounded-full overflow-hidden">
                <div className="bg-purple-600 h-1" style={{ width: `${Math.min((user.jobDescriptionCount || 0) * 10, 100)}%` }}></div>
                </div>
            </div>
            
            <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center justify-between mb-2">
                <h3 className="text-gray-500 font-medium">Matches</h3>
                <span className="text-2xl font-bold text-green-600">{user.matchCount || 0}</span>
                </div>
                <div className="w-full bg-gray-200 h-1 rounded-full overflow-hidden">
                <div className="bg-green-600 h-1" style={{ width: `${Math.min((user.matchCount || 0) * 10, 100)}%` }}></div>
                </div>
            </div>
            </div>
        </div>
        </div>
    );
};

export default Dashboard;