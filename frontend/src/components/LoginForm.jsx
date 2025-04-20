import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';

const LoginForm = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
        const response = await axios.post('http://localhost:8000/api/auth/login', { email, password });
        localStorage.setItem('token', response.data.token);
        toast.success('Login successful!');
        navigate('/upload-resume');
        } catch (error) {
        toast.error('Login failed. Please try again.');
        }
    };

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

            <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email"
            required
            className="w-full p-3 border border-gray-300 rounded mb-4 focus:outline-none focus:ring-2 focus:ring-blue-400"
            />

            <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            required
            className="w-full p-3 border border-gray-300 rounded mb-6 focus:outline-none focus:ring-2 focus:ring-blue-400"
            />

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
