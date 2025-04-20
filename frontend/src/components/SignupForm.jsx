import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';

const SignupForm = () => {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleSignup = async (e) => {
        e.preventDefault();
        try {
        await axios.post('http://localhost:8000/api/auth/signup', { name, email, password });
        toast.success('Signup successful! Please login.');
        navigate('/login');
        } catch (error) {
        toast.error('Signup failed. Please try again.');
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <form onSubmit={handleSignup} className="bg-white p-8 rounded shadow-md w-full max-w-md">
            <h2 className="text-2xl font-bold mb-4">Signup</h2>
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
