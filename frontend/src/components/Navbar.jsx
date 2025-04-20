import { useNavigate } from 'react-router-dom';

const Navbar = () => {
    const navigate = useNavigate();
    const token = localStorage.getItem('token');

    if (!token) return null; 

    return (
            <nav className="bg-blue-600 p-4 flex justify-between items-center">
            <h1 className="text-white font-bold text-xl">Resume Analyzer</h1>
            <div className="flex space-x-4">
                <button
                onClick={() => navigate('/upload-resume')}
                className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded"
                >
                Check Score
                </button>
                <button
                onClick={() => {
                    localStorage.removeItem('token');
                    navigate('/login');
                }}
                className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded"
                >
                Logout
                </button>
            </div>
            </nav>
        );
};

export default Navbar;
