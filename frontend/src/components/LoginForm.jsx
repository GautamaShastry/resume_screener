import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';
import Loading from './Loading';
import OtpVerification from './OtpVerification';

const LoginForm = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isOtpSent, setIsOtpSent] = useState(false);
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
        setIsLoading(true);
        const response = await axios.post('http://localhost:8001/api/auth/login', { email, password });
        
        // if login successful, navigate to the OTP screen
        setIsOtpSent(true);

        toast.success(response.data.message);
        } catch (error) {
        toast.error('Login failed. Please check your credentials.');
        } finally {
        setIsLoading(false);
        }
    };

    const handleResendOTP = async () => {
        try {
            setIsLoading(true);
            const response = await axios.post('http://localhost:8001/api/auth/resend-otp', { 
                email 
            });
            toast.success(response.data.message);
        } catch (error) {
            toast.error('Failed to resend OTP. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    if (isLoading) return <Loading />;

    // Show OTP verification screen if first step of login is successful
    if (isOtpSent) {
        return (
            <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-start py-12 px-4">
                <div className="text-center mb-10">
                    <h1 className="text-4xl font-extrabold text-blue-700 mb-2">Resume Analyzer</h1>
                    <p className="text-gray-600">Enter verification code to continue</p>
                </div>
                
                <OtpVerification 
                    email={email} 
                    onResendOTP={handleResendOTP} 
                />
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-start py-12 px-4">
        
        {/* Top Heading */}
        <div className="text-center mb-10">
            <h1 className="text-4xl font-extrabold text-blue-700 mb-2">Resume Analyzer</h1>
            <p className="text-gray-600">Empowering your career with AI</p>
        </div>

        {/* Login Form */}
        <form onSubmit={handleLogin} className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
            <h2 className="text-2xl font-bold text-center mb-6">Login</h2>

            <div className="mb-4">
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">Email <span className='text-red-700'>*</span></label>
            <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="xyz@example.com"
                required
                className="w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
            </div>

            <div className="mb-6">
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">Password <span className='text-red-700'>*</span></label>
            <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="123"
                required
                className="w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
            </div>

            <button
            type="submit"
            className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded font-semibold transition duration-200"
            >
            Login
            </button>

            <p className="text-center mt-6 text-gray-600">
            Don't have an account?{' '}
            <Link to="/signup" className="text-blue-600 hover:underline">
                Signup
            </Link>
            </p>
        </form>
        </div>
    );
};

export default LoginForm;
