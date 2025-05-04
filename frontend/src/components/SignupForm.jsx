import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';
import Loading from './Loading';

const SignupForm = () => {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();

    const handleSignup = async (e) => {
        e.preventDefault();
        try {
        setIsLoading(true);
        await axios.post('https://resume-screener-backend-hfz2.onrender.com/api/auth/signup', { name, email, password });
        toast.success('Signup successful! Please login.');
        navigate('/login');
        } catch (error) {
        toast.error('Signup failed. Please try again.');
        } finally {
        setIsLoading(false);
        }
    };

    if (isLoading) return <Loading />;

    return (
        <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-start py-12 px-4">
        <div className="text-center mb-10">
            <h1 className="text-4xl font-extrabold text-blue-700 mb-2">Resume Analyzer</h1>
            <p className="text-gray-600">Empowering your career with AI</p>
        </div>

        <form onSubmit={handleSignup} className="bg-white p-8 rounded shadow-md w-full max-w-md">
            <h2 className="text-2xl font-bold mb-6 text-center">Signup</h2>

            <div className="mb-4">
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">Name <span className='text-red-700'>*</span></label>
            <input
                id="name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="John Doe"
                required
                className="w-full p-2 border rounded"
            />
            </div>

            <div className="mb-4">
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">Email <span className='text-red-700'>*</span></label>
            <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="xyz@example.com"
                required
                className="w-full p-2 border rounded"
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
                className="w-full p-2 border rounded"
            />
            </div>

            <button type="submit" className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-2 rounded">
            Signup
            </button>

            <p className="text-center mt-4">
            Already have an account?{' '}
            <Link to="/login" className="text-blue-600 hover:underline">
                Login
            </Link>
            </p>
        </form>
        </div>
    );
};

export default SignupForm;
