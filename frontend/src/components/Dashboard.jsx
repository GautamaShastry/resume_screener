import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import axios from 'axios';
import { toast } from 'react-toastify';
import Loading from './Loading';
import { 
  FiUpload, FiFileText, FiBarChart2, FiClock, FiTrendingUp, 
  FiTarget, FiAward, FiArrowRight, FiZap, FiCheckCircle 
} from 'react-icons/fi';

const Dashboard = () => {
  const [user, setUser] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUserProfile = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
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
  }, [navigate]);

  if (isLoading) return <Loading />;

  const stats = [
    { label: 'Resumes', value: user.resumeCount || 0, icon: FiFileText, color: 'from-blue-500 to-cyan-500', bg: 'bg-blue-500/10' },
    { label: 'Job Descriptions', value: user.jobDescriptionCount || 0, icon: FiTarget, color: 'from-purple-500 to-pink-500', bg: 'bg-purple-500/10' },
    { label: 'Analyses', value: user.matchCount || 0, icon: FiBarChart2, color: 'from-green-500 to-emerald-500', bg: 'bg-green-500/10' },
  ];

  const quickActions = [
    { title: 'Upload Resume', desc: 'Start a new analysis', icon: FiUpload, path: '/upload-resume', color: 'from-blue-600 to-cyan-600' },
    { title: 'Add Job', desc: 'Paste job description', icon: FiFileText, path: '/upload-job', color: 'from-purple-600 to-pink-600' },
    { title: 'View History', desc: 'Past analyses', icon: FiClock, path: '/history', color: 'from-orange-600 to-red-600' },
  ];

  const steps = [
    { num: 1, title: 'Upload Resume', desc: 'PDF or DOCX format' },
    { num: 2, title: 'Add Job Description', desc: 'Paste the job posting' },
    { num: 3, title: 'Get AI Analysis', desc: 'Instant detailed insights' },
  ];

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Background */}
      <div className="fixed inset-0 z-0">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950" />
        <div className="absolute top-0 right-1/4 w-[500px] h-[500px] bg-blue-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-1/4 w-[500px] h-[500px] bg-purple-500/5 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10">
        {/* Hero Section */}
        <div className="px-6 lg:px-12 pt-8 pb-12">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-8">
                <div>
                  <h1 className="text-4xl lg:text-5xl font-bold text-white mb-2">
                    Welcome back, <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">{user.name || 'User'}</span>
                  </h1>
                  <p className="text-gray-400 text-lg">Ready to optimize your next job application?</p>
                </div>
                <Link to="/upload-resume">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="mt-4 lg:mt-0 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white rounded-xl font-semibold flex items-center shadow-lg shadow-blue-500/25 transition-all"
                  >
                    <FiZap className="mr-2" /> New Analysis
                  </motion.button>
                </Link>
              </div>

              {/* Stats Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
                {stats.map((stat, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.1 }}
                    className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-6 hover:border-white/20 transition-all"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-gray-400 text-sm mb-1">{stat.label}</p>
                        <p className="text-4xl font-bold bg-gradient-to-r ${stat.color} bg-clip-text text-transparent">
                          <span className={`bg-gradient-to-r ${stat.color} bg-clip-text text-transparent`}>
                            {stat.value}
                          </span>
                        </p>
                      </div>
                      <div className={`w-14 h-14 ${stat.bg} rounded-xl flex items-center justify-center`}>
                        <stat.icon className={`w-7 h-7 bg-gradient-to-r ${stat.color} text-blue-400`} />
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>

            {/* Quick Actions */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="mb-12"
            >
              <h2 className="text-2xl font-bold text-white mb-6">Quick Actions</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {quickActions.map((action, idx) => (
                  <Link key={idx} to={action.path}>
                    <motion.div
                      whileHover={{ y: -4, scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className={`bg-gradient-to-br ${action.color} rounded-2xl p-6 cursor-pointer shadow-xl transition-all h-full`}
                    >
                      <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center mb-4">
                        <action.icon className="w-6 h-6 text-white" />
                      </div>
                      <h3 className="text-xl font-semibold text-white mb-1">{action.title}</h3>
                      <p className="text-white/70">{action.desc}</p>
                      <div className="mt-4 flex items-center text-white/80 text-sm font-medium">
                        Get Started <FiArrowRight className="ml-2" />
                      </div>
                    </motion.div>
                  </Link>
                ))}
              </div>
            </motion.div>

            {/* How It Works */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-8"
            >
              <h2 className="text-2xl font-bold text-white mb-8 text-center">How It Works</h2>
              <div className="grid md:grid-cols-3 gap-8">
                {steps.map((step, idx) => (
                  <div key={idx} className="text-center relative">
                    <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4 text-2xl font-bold text-white">
                      {step.num}
                    </div>
                    <h3 className="text-lg font-semibold text-white mb-2">{step.title}</h3>
                    <p className="text-gray-400">{step.desc}</p>
                    {idx < 2 && (
                      <div className="hidden md:block absolute top-8 left-[60%] w-[80%] h-0.5 bg-gradient-to-r from-blue-500/50 to-purple-500/50" />
                    )}
                  </div>
                ))}
              </div>
              <div className="text-center mt-8">
                <Link to="/upload-resume">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white rounded-xl font-semibold inline-flex items-center shadow-lg shadow-blue-500/25 transition-all"
                  >
                    <FiCheckCircle className="mr-2" /> Start Your Analysis
                  </motion.button>
                </Link>
              </div>
            </motion.div>

            {/* Features Grid */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="mt-12 grid md:grid-cols-2 lg:grid-cols-4 gap-6"
            >
              {[
                { icon: FiZap, title: 'Instant Analysis', desc: 'Results in seconds' },
                { icon: FiTarget, title: 'ATS Optimized', desc: 'Beat tracking systems' },
                { icon: FiTrendingUp, title: 'Career Insights', desc: 'Growth recommendations' },
                { icon: FiAward, title: 'Match Scoring', desc: 'Detailed compatibility' },
              ].map((feature, idx) => (
                <div key={idx} className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-5 hover:border-white/20 transition-all">
                  <feature.icon className="w-8 h-8 text-blue-400 mb-3" />
                  <h3 className="text-white font-semibold mb-1">{feature.title}</h3>
                  <p className="text-gray-400 text-sm">{feature.desc}</p>
                </div>
              ))}
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
