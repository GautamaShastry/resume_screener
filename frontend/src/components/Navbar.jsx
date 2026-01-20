import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FiLogOut, FiHome, FiFileText, FiClock, FiZap } from 'react-icons/fi';

const Navbar = () => {
  const navigate = useNavigate();
  const token = localStorage.getItem('token');

  if (!token) return null;

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('resumeId');
    localStorage.removeItem('jobDescriptionId');
    navigate('/login');
  };

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
      className="sticky top-0 z-50 bg-slate-900/80 backdrop-blur-xl border-b border-white/10"
    >
      <div className="max-w-7xl mx-auto px-6 lg:px-12">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/dashboard" className="flex items-center space-x-2">
            <div className="w-9 h-9 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <FiFileText className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
              HireReady
            </span>
          </Link>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-1">
            <Link
              to="/dashboard"
              className="px-4 py-2 text-gray-300 hover:text-white hover:bg-white/5 rounded-lg transition-all flex items-center"
            >
              <FiHome className="mr-2 w-4 h-4" /> Dashboard
            </Link>
            <Link
              to="/history"
              className="px-4 py-2 text-gray-300 hover:text-white hover:bg-white/5 rounded-lg transition-all flex items-center"
            >
              <FiClock className="mr-2 w-4 h-4" /> History
            </Link>
          </div>

          {/* Actions */}
          <div className="flex items-center space-x-3">
            <Link to="/upload-resume">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white rounded-lg font-medium text-sm flex items-center shadow-lg shadow-blue-500/20 transition-all"
              >
                <FiZap className="mr-2 w-4 h-4" /> New Analysis
              </motion.button>
            </Link>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleLogout}
              className="px-4 py-2 bg-white/5 hover:bg-red-500/20 text-gray-300 hover:text-red-400 rounded-lg font-medium text-sm flex items-center border border-white/10 hover:border-red-500/30 transition-all"
            >
              <FiLogOut className="mr-2 w-4 h-4" /> Logout
            </motion.button>
          </div>
        </div>
      </div>
    </motion.nav>
  );
};

export default Navbar;
