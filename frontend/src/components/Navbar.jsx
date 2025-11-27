import { useNavigate } from 'react-router-dom';
import { FiLogOut, FiHome } from 'react-icons/fi'; 

const Navbar = () => {
    const navigate = useNavigate();
    const token = localStorage.getItem('token');

    if (!token) return null; 

    return (
        <nav className="bg-blue-900 p-4 flex justify-between items-center shadow-md">
            <h1 
                onClick={() => navigate('/dashboard')}
                className="text-white font-extrabold text-2xl cursor-pointer hover:text-blue-100 transition duration-200 flex items-center"
            >
                <FiHome className="mr-2" />
                Home 
            </h1>

            <div className="flex items-center space-x-4">
                <button
                    onClick={() => navigate('/upload-resume')}
                    className="bg-green-500 hover:bg-green-600 text-white font-semibold px-4 py-2 rounded transition duration-200"
                >
                    Check Score
                </button>

                <button
                    onClick={() => {
                        localStorage.removeItem('token');
                        localStorage.removeItem('resumeId');
                        localStorage.removeItem('jobDescriptionId');
                        navigate('/login');
                    }}
                    className="flex items-center bg-red-500 hover:bg-red-600 text-white font-semibold px-4 py-2 rounded transition duration-200"
                >
                    <FiLogOut className="mr-2 text-lg" /> 
                    Logout
                </button>
            </div>
        </nav>
    );
};

export default Navbar;