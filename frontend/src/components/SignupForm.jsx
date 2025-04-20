import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';
import Loading from './Loading';

const SignupForm = () => {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false); // loading state
    const navigate = useNavigate();

    const handleSignup = async (e) => {
        e.preventDefault();
        try {
            setIsLoading(true); // Set loading state to true
            await axios.post('http://localhost:8000/api/auth/signup', { name, email, password });
            toast.success('Signup successful! Please login.');
            navigate('/login');
        } catch (error) {
        toast.error('Signup failed. Please try again.');
        } finally {
            setIsLoading(false); // Reset loading state
        }
    };

    if(isLoading) return <Loading />; // Show loading component while signing up

    return (
        <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-start py-12 px-4">
            <div className="text-center mb-10">
                <h1 className="text-4xl font-extrabold text-blue-700 mb-2">Resume Analyzer</h1>
                <p className="text-gray-600">Empowering your career with AI</p>
            </div>
            <form onSubmit={handleSignup} className="bg-white p-8 rounded shadow-md w-full max-w-md">
                <h2 className="text-2xl font-bold mb-4 text-center">Signup</h2>
                <input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="Name" required className="w-full p-2 border rounded mb-4" />
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" required className="w-full p-2 border rounded mb-4" />
                <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" required className="w-full p-2 border rounded mb-4" />
                <button type="submit" className="w-full bg-green-600 text-white py-2 rounded mb-4">Signup</button>
                <p className="text-center">Already have an account? <Link to="/login" className="text-blue-600">Login</Link></p>
            </form>
        </div>
    );
};

export default SignupForm;
