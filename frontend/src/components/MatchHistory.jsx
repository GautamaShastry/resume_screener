import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { toast } from 'react-toastify';
import axios from 'axios';
import Loading from './Loading';
import { FiClock, FiFileText, FiBriefcase, FiDownload, FiEye, FiCalendar, FiPlus } from 'react-icons/fi';

const MatchHistory = () => {
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const navigate = useNavigate();

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    try {
      setIsLoading(true);
      const response = await axios.get('http://localhost:8001/api/match/history', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setHistory(response.data);
    } catch (error) {
      toast.error('Failed to load history');
    } finally {
      setIsLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'from-green-500 to-emerald-500';
    if (score >= 60) return 'from-amber-500 to-orange-500';
    return 'from-red-500 to-pink-500';
  };

  const getScoreBadge = (score) => {
    if (score >= 80) return { label: 'Excellent', bg: 'bg-green-500/20', text: 'text-green-400' };
    if (score >= 60) return { label: 'Good', bg: 'bg-amber-500/20', text: 'text-amber-400' };
    return { label: 'Needs Work', bg: 'bg-red-500/20', text: 'text-red-400' };
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', { 
      month: 'short', day: 'numeric', year: 'numeric'
    });
  };

  const filteredHistory = history.filter(item => {
    if (filter === 'all') return true;
    if (filter === 'high') return item.matchScore >= 80;
    if (filter === 'medium') return item.matchScore >= 60 && item.matchScore < 80;
    if (filter === 'low') return item.matchScore < 60;
    return true;
  });

  const handleDownloadPDF = async (matchResultId) => {
    const token = localStorage.getItem('token');
    try {
      const response = await axios.get(`http://localhost:8001/api/report/pdf/${matchResultId}`, {
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `analysis-${matchResultId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('PDF downloaded!');
    } catch (error) {
      toast.error('Failed to download PDF');
    }
  };

  const handleViewReport = async (matchResultId) => {
    const token = localStorage.getItem('token');
    try {
      const response = await axios.get(`http://localhost:8001/api/report/html/${matchResultId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const newWindow = window.open();
      newWindow.document.write(response.data);
      newWindow.document.close();
    } catch (error) {
      toast.error('Failed to view report');
    }
  };

  if (isLoading) return <Loading />;

  const filters = [
    { key: 'all', label: 'All' },
    { key: 'high', label: '≥80%', color: 'text-green-400' },
    { key: 'medium', label: '60-79%', color: 'text-amber-400' },
    { key: 'low', label: '<60%', color: 'text-red-400' },
  ];

  return (
    <div className="min-h-screen bg-slate-950 py-12 px-4">
      <div className="fixed inset-0 z-0">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950" />
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-indigo-500/5 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 max-w-5xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col md:flex-row md:items-center md:justify-between mb-8"
        >
          <div className="flex items-center mb-4 md:mb-0">
            <div className="w-14 h-14 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center mr-4">
              <FiClock className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">Match History</h1>
              <p className="text-gray-400">{history.length} total analyses</p>
            </div>
          </div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => navigate('/upload-resume')}
            className="px-5 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-medium flex items-center shadow-lg shadow-blue-500/25"
          >
            <FiPlus className="mr-2" /> New Analysis
          </motion.button>
        </motion.div>

        {/* Filters */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="flex flex-wrap gap-2 mb-6"
        >
          {filters.map((f) => (
            <button
              key={f.key}
              onClick={() => setFilter(f.key)}
              className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${
                filter === f.key
                  ? 'bg-white/10 text-white border border-white/20'
                  : 'bg-white/5 text-gray-400 hover:bg-white/10 border border-transparent'
              }`}
            >
              <span className={f.color}>{f.label}</span>
            </button>
          ))}
        </motion.div>

        {/* History List */}
        {filteredHistory.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-12 text-center"
          >
            <div className="w-20 h-20 bg-white/5 rounded-full flex items-center justify-center mx-auto mb-4">
              <FiClock className="w-10 h-10 text-gray-500" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">No History Found</h3>
            <p className="text-gray-400 mb-6">
              {filter !== 'all' ? `No matches in this category` : "Start your first analysis"}
            </p>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate('/upload-resume')}
              className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-medium"
            >
              Start Analysis
            </motion.button>
          </motion.div>
        ) : (
          <div className="space-y-4">
            {filteredHistory.map((item, idx) => {
              const badge = getScoreBadge(item.matchScore);
              return (
                <motion.div
                  key={item.matchResultId}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-6 hover:border-white/20 transition-all"
                >
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="flex items-center gap-4">
                      {/* Score Circle */}
                      <div className={`w-16 h-16 rounded-xl bg-gradient-to-br ${getScoreColor(item.matchScore)} flex items-center justify-center`}>
                        <span className="text-2xl font-bold text-white">{Math.round(item.matchScore)}</span>
                      </div>
                      
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`${badge.bg} ${badge.text} text-xs font-semibold px-2 py-1 rounded-full`}>
                            {badge.label}
                          </span>
                          <span className="text-xs text-gray-500 flex items-center">
                            <FiCalendar className="mr-1 w-3 h-3" />
                            {formatDate(item.matchTime)}
                          </span>
                        </div>
                        <h3 className="text-lg font-semibold text-white flex items-center">
                          <FiBriefcase className="mr-2 w-4 h-4 text-purple-400" />
                          {item.jobTitle || 'Untitled Position'}
                        </h3>
                        <p className="text-sm text-gray-400 flex items-center">
                          <FiFileText className="mr-2 w-4 h-4 text-blue-400" />
                          {item.resumeFileName || 'Resume'}
                        </p>
                      </div>
                    </div>

                    {/* Actions */}
                    {item.hasReports && (
                      <div className="flex gap-2">
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => handleViewReport(item.matchResultId)}
                          className="px-4 py-2 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 rounded-lg font-medium text-sm flex items-center transition-all"
                        >
                          <FiEye className="mr-2 w-4 h-4" /> View
                        </motion.button>
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => handleDownloadPDF(item.matchResultId)}
                          className="px-4 py-2 bg-green-500/10 hover:bg-green-500/20 text-green-400 rounded-lg font-medium text-sm flex items-center transition-all"
                        >
                          <FiDownload className="mr-2 w-4 h-4" /> PDF
                        </motion.button>
                      </div>
                    )}
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default MatchHistory;
