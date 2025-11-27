import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';
import Loading from './Loading';
import { FiAward, FiBarChart, FiCheckCircle, FiCpu, FiTarget, FiTrendingUp, FiUsers, FiZap } from 'react-icons/fi';

const Dashboard = () => {
    const [user, setUser] = useState({});
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchUserProfile = async () => {
            const token = localStorage.getItem('token');

            if (!token) {
                console.error('❌ No token found! Redirecting to login...');
                toast.error('Session expired. Please login again.');
                navigate('/login');
                return;
            }
            
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
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-gray-100">
            {/* Hero Section */}
            <div className="bg-gradient-to-r from-blue-700 via-blue-600 to-blue-500 text-white py-16 px-4">
                <div className="max-w-7xl mx-auto">
                    <div className="flex flex-col md:flex-row items-center justify-between">
                        <div className="md:w-2/3 mb-8 md:mb-0">
                            <h1 className="text-4xl md:text-5xl font-bold mb-4">
                                Welcome back, {user.name || 'User'}! 👋
                            </h1>
                            <p className="text-blue-100 text-lg md:text-xl mb-6">
                                Ready to take your career to the next level? Let's optimize your job applications with AI-powered insights.
                            </p>
                            <div className="flex flex-col sm:flex-row gap-4">
                                <Link 
                                    to="/upload-resume" 
                                    className="bg-white text-blue-700 hover:bg-blue-50 px-8 py-4 rounded-lg font-semibold text-lg shadow-md transition duration-300 text-center"
                                >
                                    <FiCheckCircle className="inline mr-2" />
                                    Check Resume Score
                                </Link>
                                <button 
                                    onClick={() => {
                                        document.getElementById('how-it-works')?.scrollIntoView({ 
                                            behavior: 'smooth',
                                            block: 'start'
                                        });
                                    }}
                                    className="bg-blue-800 hover:bg-blue-900 text-white px-8 py-4 rounded-lg font-semibold text-lg shadow-md transition duration-300 text-center"
                                >
                                    Learn How It Works
                                </button>
                            </div>
                        </div>
                        <div className="md:w-1/3 flex justify-center">
                            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 text-center">
                                <FiTrendingUp className="w-20 h-20 mx-auto mb-4 text-yellow-300" />
                                <h3 className="text-2xl font-bold mb-2">95% Success Rate</h3>
                                <p className="text-blue-100">Users report better interview callbacks</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Stats Section */}
            <div className="max-w-7xl mx-auto px-4 -mt-12">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-white rounded-xl shadow-lg p-6 border-t-4 border-blue-500 transform hover:scale-105 transition duration-300">
                        <div className="flex items-center justify-between mb-4">
                            <div>
                                <h3 className="text-gray-500 font-medium mb-1">Total Resumes</h3>
                                <span className="text-3xl font-bold text-blue-600">{user.resumeCount || 0}</span>
                            </div>
                            <div className="bg-blue-100 p-4 rounded-full">
                                <FiBarChart className="w-8 h-8 text-blue-600" />
                            </div>
                        </div>
                        <div className="w-full bg-gray-200 h-2 rounded-full overflow-hidden">
                            <div className="bg-blue-600 h-2 transition-all duration-500" style={{ width: `${Math.min((user.resumeCount || 0) * 10, 100)}%` }}></div>
                        </div>
                    </div>
                    
                    <div className="bg-white rounded-xl shadow-lg p-6 border-t-4 border-purple-500 transform hover:scale-105 transition duration-300">
                        <div className="flex items-center justify-between mb-4">
                            <div>
                                <h3 className="text-gray-500 font-medium mb-1">Job Descriptions</h3>
                                <span className="text-3xl font-bold text-purple-600">{user.jobDescriptionCount || 0}</span>
                            </div>
                            <div className="bg-purple-100 p-4 rounded-full">
                                <FiTarget className="w-8 h-8 text-purple-600" />
                            </div>
                        </div>
                        <div className="w-full bg-gray-200 h-2 rounded-full overflow-hidden">
                            <div className="bg-purple-600 h-2 transition-all duration-500" style={{ width: `${Math.min((user.jobDescriptionCount || 0) * 10, 100)}%` }}></div>
                        </div>
                    </div>
                    
                    <div className="bg-white rounded-xl shadow-lg p-6 border-t-4 border-green-500 transform hover:scale-105 transition duration-300">
                        <div className="flex items-center justify-between mb-4">
                            <div>
                                <h3 className="text-gray-500 font-medium mb-1">Total Matches</h3>
                                <span className="text-3xl font-bold text-green-600">{user.matchCount || 0}</span>
                            </div>
                            <div className="bg-green-100 p-4 rounded-full">
                                <FiAward className="w-8 h-8 text-green-600" />
                            </div>
                        </div>
                        <div className="w-full bg-gray-200 h-2 rounded-full overflow-hidden">
                            <div className="bg-green-600 h-2 transition-all duration-500" style={{ width: `${Math.min((user.matchCount || 0) * 10, 100)}%` }}></div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Features Section */}
            <div className="max-w-7xl mx-auto px-4 py-16">
                <div className="text-center mb-12">
                    <h2 className="text-4xl font-bold text-gray-800 mb-4">Why Choose HireReady?</h2>
                    <p className="text-xl text-gray-600">Transform your job search with cutting-edge AI technology</p>
                </div>
                
                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
                    <div className="bg-white rounded-xl shadow-lg p-6 text-center hover:shadow-2xl transition duration-300">
                        <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                            <FiCpu className="w-8 h-8 text-blue-600" />
                        </div>
                        <h3 className="text-xl font-semibold mb-3">AI-Powered Analysis</h3>
                        <p className="text-gray-600">
                            Advanced algorithms analyze your resume against job descriptions with precision and speed.
                        </p>
                    </div>
                    
                    <div className="bg-white rounded-xl shadow-lg p-6 text-center hover:shadow-2xl transition duration-300">
                        <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                            <FiZap className="w-8 h-8 text-green-600" />
                        </div>
                        <h3 className="text-xl font-semibold mb-3">Instant Results</h3>
                        <p className="text-gray-600">
                            Get detailed match scores and actionable insights in seconds, not hours.
                        </p>
                    </div>
                    
                    <div className="bg-white rounded-xl shadow-lg p-6 text-center hover:shadow-2xl transition duration-300">
                        <div className="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                            <FiTarget className="w-8 h-8 text-purple-600" />
                        </div>
                        <h3 className="text-xl font-semibold mb-3">Targeted Improvement</h3>
                        <p className="text-gray-600">
                            Identify exact skills and keywords to add for each specific job posting.
                        </p>
                    </div>
                    
                    <div className="bg-white rounded-xl shadow-lg p-6 text-center hover:shadow-2xl transition duration-300">
                        <div className="bg-yellow-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                            <FiUsers className="w-8 h-8 text-yellow-600" />
                        </div>
                        <h3 className="text-xl font-semibold mb-3">Trusted by Thousands</h3>
                        <p className="text-gray-600">
                            Join successful job seekers who landed their dream roles with our help.
                        </p>
                    </div>
                </div>
            </div>

            {/* How It Works Section */}
            <div id="how-it-works" className="bg-white py-16">
                <div className="max-w-7xl mx-auto px-4">
                    <h2 className="text-4xl font-bold text-center mb-12 text-gray-800">How It Works</h2>
                    
                    <div className="grid md:grid-cols-3 gap-8">
                        <div className="relative">
                            <div className="flex flex-col items-center text-center">
                                <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-blue-400 rounded-full flex items-center justify-center text-white text-2xl font-bold mb-6 shadow-lg">1</div>
                                <div className="bg-blue-50 rounded-xl p-6 h-full">
                                    <h3 className="text-xl font-semibold mb-3">Upload Your Resume</h3>
                                    <p className="text-gray-600">Upload your resume in PDF or DOCX format. Our system securely processes your document.</p>
                                </div>
                            </div>
                            <div className="hidden md:block absolute top-8 left-full w-full h-0.5 bg-blue-200" style={{width: 'calc(100% - 4rem)', left: '4rem'}}></div>
                        </div>
                        
                        <div className="relative">
                            <div className="flex flex-col items-center text-center">
                                <div className="w-16 h-16 bg-gradient-to-br from-purple-600 to-purple-400 rounded-full flex items-center justify-center text-white text-2xl font-bold mb-6 shadow-lg">2</div>
                                <div className="bg-purple-50 rounded-xl p-6 h-full">
                                    <h3 className="text-xl font-semibold mb-3">Add Job Description</h3>
                                    <p className="text-gray-600">Paste the job description you're targeting. Include all requirements and qualifications.</p>
                                </div>
                            </div>
                            <div className="hidden md:block absolute top-8 left-full w-full h-0.5 bg-purple-200" style={{width: 'calc(100% - 4rem)', left: '4rem'}}></div>
                        </div>
                        
                        <div className="flex flex-col items-center text-center">
                            <div className="w-16 h-16 bg-gradient-to-br from-green-600 to-green-400 rounded-full flex items-center justify-center text-white text-2xl font-bold mb-6 shadow-lg">3</div>
                            <div className="bg-green-50 rounded-xl p-6 h-full">
                                <h3 className="text-xl font-semibold mb-3">Get Detailed Analysis</h3>
                                <p className="text-gray-600">Receive comprehensive analysis with match score, strengths, weaknesses, and improvement tips.</p>
                            </div>
                        </div>
                    </div>
                    
                    <div className="text-center mt-12">
                        <Link 
                            to="/upload-resume" 
                            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-4 rounded-lg font-semibold inline-flex items-center text-lg shadow-lg transform hover:scale-105 transition duration-300"
                        >
                            <FiCheckCircle className="mr-2" size={24} /> 
                            Start Your Free Analysis Now
                        </Link>
                    </div>
                </div>
            </div>

            {/* Quick Actions Section */}
            <div className="max-w-7xl mx-auto px-4 py-16">
                <h2 className="text-3xl font-bold mb-8 text-gray-800">Quick Actions</h2>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2">
                        <div className="p-8 text-white">
                            <div className="w-14 h-14 bg-white/20 rounded-full flex items-center justify-center mb-4">
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                                </svg>
                            </div>
                            <h3 className="text-2xl font-bold mb-2">Upload Resume</h3>
                            <p className="text-green-100 mb-6">Upload your resume and get instant AI-powered analysis.</p>
                            <Link to="/upload-resume" className="bg-white text-green-600 hover:bg-green-50 py-3 px-6 rounded-lg inline-block font-semibold transition duration-200">
                                Get Started →
                            </Link>
                        </div>
                    </div>

                    <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2">
                        <div className="p-8 text-white">
                            <div className="w-14 h-14 bg-white/20 rounded-full flex items-center justify-center mb-4">
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                                </svg>
                            </div>
                            <h3 className="text-2xl font-bold mb-2">Add Job Posting</h3>
                            <p className="text-purple-100 mb-6">Match your resume against specific job requirements.</p>
                            <Link to="/upload-job" className="bg-white text-purple-600 hover:bg-purple-50 py-3 px-6 rounded-lg inline-block font-semibold transition duration-200">
                                Add Job →
                            </Link>
                        </div>
                    </div>

                    <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2">
                        <div className="p-8 text-white">
                            <div className="w-14 h-14 bg-white/20 rounded-full flex items-center justify-center mb-4">
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 4 0 01-2 2h-2a2 2 0 01-2-2z" />
                                </svg>
                            </div>
                            <h3 className="text-2xl font-bold mb-2">View History</h3>
                            <p className="text-blue-100 mb-6">Track your progress and past resume analyses.</p>
                            <Link to="/history" className="bg-white text-blue-600 hover:bg-blue-50 py-3 px-6 rounded-lg inline-block font-semibold transition duration-200">
                                View History →
                            </Link>
                        </div>
                    </div>
                </div>
            </div>

            {/* Testimonials/Success Stories */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 py-16">
                <div className="max-w-7xl mx-auto px-4">
                    <div className="text-center text-white mb-12">
                        <h2 className="text-4xl font-bold mb-4">Success Stories</h2>
                        <p className="text-xl text-blue-100">Join thousands who've improved their job search</p>
                    </div>
                    
                    <div className="grid md:grid-cols-3 gap-8">
                        {[
                            { name: "Sarah J.", role: "Software Engineer", quote: "Increased my interview callback rate by 3x!", score: "87%" },
                            { name: "Michael T.", role: "Marketing Manager", quote: "The ATS optimization tips were game-changing.", score: "92%" },
                            { name: "Emily R.", role: "Data Analyst", quote: "Got my dream job within 2 weeks of using this!", score: "95%" }
                        ].map((testimonial, idx) => (
                            <div key={idx} className="bg-white/10 backdrop-blur-lg rounded-xl p-6 hover:bg-white/20 transition duration-300">
                                <div className="flex items-center mb-4">
                                    <div className="w-12 h-12 bg-yellow-400 rounded-full flex items-center justify-center text-white font-bold text-xl">
                                        {testimonial.name[0]}
                                    </div>
                                    <div className="ml-3">
                                        <h4 className="font-bold text-white">{testimonial.name}</h4>
                                        <p className="text-blue-100 text-sm">{testimonial.role}</p>
                                    </div>
                                </div>
                                <p className="text-white italic mb-4">"{testimonial.quote}"</p>
                                <div className="flex items-center">
                                    <FiAward className="text-yellow-400 mr-2" />
                                    <span className="text-white font-semibold">Match Score: {testimonial.score}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;