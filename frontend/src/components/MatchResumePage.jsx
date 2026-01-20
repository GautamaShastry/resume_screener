import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { toast } from 'react-toastify';
import axios from 'axios';
import { useState, useEffect } from 'react';
import Loading from './Loading';
import { FiZap, FiFileText, FiBriefcase, FiCheckCircle, FiArrowRight, FiTarget, FiAward, FiTrendingUp, FiDownload } from 'react-icons/fi';

const MatchResumePage = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [resumeInfo, setResumeInfo] = useState(null);
  const [jobInfo, setJobInfo] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchDetails = async () => {
      const token = localStorage.getItem('token');
      const resumeId = localStorage.getItem('resumeId');
      const jobDescriptionId = localStorage.getItem('jobDescriptionId');

      if (!resumeId || !jobDescriptionId) {
        toast.error('Missing resume or job description!');
        navigate('/dashboard');
        return;
      }

      try {
        const [resumeRes, jobRes] = await Promise.all([
          axios.get(`http://localhost:8001/api/resume/${resumeId}`, { headers: { Authorization: `Bearer ${token}` } }),
          axios.get(`http://localhost:8001/api/job/${jobDescriptionId}`, { headers: { Authorization: `Bearer ${token}` } })
        ]);
        setResumeInfo(resumeRes.data);
        setJobInfo(jobRes.data);
      } catch (error) {
        // Continue even if fetch fails
      }
    };
    fetchDetails();
  }, [navigate]);

  const handleMatch = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem('token');
    const resumeId = localStorage.getItem('resumeId');
    const jobDescriptionId = localStorage.getItem('jobDescriptionId');

    if (!resumeId || !jobDescriptionId) {
      toast.error('Missing data!');
      navigate('/dashboard');
      return;
    }

    try {
      setIsLoading(true);
      const response = await axios.post(
        `http://localhost:8001/api/match/matchResume?resumeId=${resumeId}&jobDescriptionId=${jobDescriptionId}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      navigate('/result', { state: response.data });
    } catch (error) {
      toast.error('Analysis failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) return <Loading />;

  const features = [
    { icon: FiTarget, title: 'Match Score', desc: 'Overall compatibility' },
    { icon: FiAward, title: 'Key Strengths', desc: 'What makes you fit' },
    { icon: FiTrendingUp, title: 'Improvements', desc: 'Skills to develop' },
    { icon: FiDownload, title: 'Reports', desc: 'PDF & HTML exports' },
  ];

  const steps = [
    { num: 1, label: 'Upload Resume', done: true },
    { num: 2, label: 'Add Job', done: true },
    { num: 3, label: 'Get Analysis', active: true },
  ];

  return (
    <div className="min-h-screen bg-slate-950 py-12 px-4">
      <div className="fixed inset-0 z-0">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950" />
        <div className="absolute top-0 left-1/3 w-[500px] h-[500px] bg-amber-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/3 w-[500px] h-[500px] bg-orange-500/5 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 max-w-4xl mx-auto">
        {/* Progress Steps */}
        <div className="flex justify-center mb-8">
          {steps.map((step, idx) => (
            <div key={idx} className="flex items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
                step.done 
                  ? 'bg-green-500 text-white'
                  : step.active 
                    ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white' 
                    : 'bg-white/10 text-gray-500'
              }`}>
                {step.done ? <FiCheckCircle className="w-5 h-5" /> : step.num}
              </div>
              <span className={`ml-2 text-sm ${step.active || step.done ? 'text-white' : 'text-gray-500'}`}>
                {step.label}
              </span>
              {idx < 2 && <div className="w-12 h-0.5 mx-4 bg-white/10" />}
            </div>
          ))}
        </div>

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div className="w-16 h-16 bg-gradient-to-br from-amber-500 to-orange-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <FiZap className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">Ready to Analyze!</h1>
          <p className="text-gray-400">Your documents are ready for AI-powered analysis</p>
        </motion.div>

        {/* Summary Cards */}
        <div className="grid md:grid-cols-2 gap-4 mb-8">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-5"
          >
            <div className="flex items-center mb-3">
              <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center mr-3">
                <FiFileText className="w-5 h-5 text-blue-400" />
              </div>
              <div>
                <h3 className="font-semibold text-white">Your Resume</h3>
                <p className="text-xs text-gray-500">Document uploaded</p>
              </div>
            </div>
            <div className="flex items-center text-sm text-green-400">
              <FiCheckCircle className="mr-2 w-4 h-4" />
              {resumeInfo?.fileName || 'Resume ready'}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-5"
          >
            <div className="flex items-center mb-3">
              <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center mr-3">
                <FiBriefcase className="w-5 h-5 text-purple-400" />
              </div>
              <div>
                <h3 className="font-semibold text-white">Job Description</h3>
                <p className="text-xs text-gray-500">Target position</p>
              </div>
            </div>
            <div className="flex items-center text-sm text-green-400">
              <FiCheckCircle className="mr-2 w-4 h-4" />
              {jobInfo?.title || 'Job description ready'}
            </div>
          </motion.div>
        </div>

        {/* Main Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-8"
        >
          <h2 className="text-xl font-bold text-white text-center mb-6">What you'll get:</h2>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {features.map((feature, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 + idx * 0.1 }}
                className="text-center p-4 bg-white/5 rounded-xl"
              >
                <feature.icon className="w-6 h-6 text-amber-400 mx-auto mb-2" />
                <h3 className="font-medium text-white text-sm">{feature.title}</h3>
                <p className="text-xs text-gray-500">{feature.desc}</p>
              </motion.div>
            ))}
          </div>

          <form onSubmit={handleMatch}>
            <motion.button
              type="submit"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full py-5 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-white font-bold rounded-xl flex items-center justify-center text-lg shadow-lg shadow-amber-500/25 transition-all"
            >
              <FiZap className="mr-2 w-6 h-6" />
              Start AI Analysis
              <FiArrowRight className="ml-2 w-6 h-6" />
            </motion.button>
          </form>

          <p className="text-center text-sm text-gray-500 mt-4">
            Analysis typically takes 10-30 seconds
          </p>
        </motion.div>

        {/* Info Note */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-6 bg-blue-500/10 border border-blue-500/20 rounded-xl p-4 flex items-start"
        >
          <div className="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center mr-3 mt-0.5 flex-shrink-0">
            <span className="text-white text-xs font-bold">i</span>
          </div>
          <p className="text-sm text-blue-200/80">
            Your data is secure and only used for this analysis. Download detailed reports after completion.
          </p>
        </motion.div>
      </div>
    </div>
  );
};

export default MatchResumePage;
