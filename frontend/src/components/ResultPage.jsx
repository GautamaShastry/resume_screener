import { useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { useEffect, useState } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import { 
  FiDownload, FiEye, FiCheckCircle, FiXCircle, FiTarget, FiTrendingUp, 
  FiHome, FiPlus, FiMessageSquare, FiEdit3, FiGlobe, FiHelpCircle 
} from 'react-icons/fi';

ChartJS.register(ArcElement, Tooltip, Legend);

const ResultPage = () => {
  const { state } = useLocation();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [isDownloadingPdf, setIsDownloadingPdf] = useState(false);
  const [isLoadingHtml, setIsLoadingHtml] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  const BACKEND_URL = 'http://localhost:8001';

  useEffect(() => {
    if (state) setData(state);
  }, [state]);

  const handleDownloadPdf = async () => {
    if (!data?.matchResultId) return toast.error('Match result ID not found');
    try {
      setIsDownloadingPdf(true);
      const token = localStorage.getItem('token');
      const response = await axios.get(`${BACKEND_URL}/api/report/pdf/${data.matchResultId}`, {
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `analysis-${data.matchResultId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('PDF downloaded!');
    } catch (error) {
      toast.error('Failed to download PDF');
    } finally {
      setIsDownloadingPdf(false);
    }
  };

  const handleViewHtmlReport = async () => {
    if (!data?.matchResultId) return toast.error('Match result ID not found');
    try {
      setIsLoadingHtml(true);
      const token = localStorage.getItem('token');
      const response = await axios.get(`${BACKEND_URL}/api/report/html/${data.matchResultId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const newWindow = window.open('', '_blank');
      newWindow.document.write(response.data);
      newWindow.document.close();
    } catch (error) {
      toast.error('Failed to load report');
    } finally {
      setIsLoadingHtml(false);
    }
  };

  if (!data) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-500 border-t-transparent mx-auto"></div>
          <p className="mt-4 text-lg text-gray-400">Loading results...</p>
        </div>
      </div>
    );
  }

  const getScoreColor = (score) => {
    if (score >= 80) return { gradient: 'from-green-500 to-emerald-500', text: 'text-green-400', label: 'Excellent Match!' };
    if (score >= 60) return { gradient: 'from-amber-500 to-orange-500', text: 'text-amber-400', label: 'Good Match' };
    return { gradient: 'from-red-500 to-pink-500', text: 'text-red-400', label: 'Needs Improvement' };
  };

  const scoreInfo = getScoreColor(data.accuracy);

  const pieData = {
    labels: ['Match', 'Gap'],
    datasets: [{
      data: [data.accuracy, 100 - data.accuracy],
      backgroundColor: ['#22c55e', '#334155'],
      borderWidth: 0,
    }],
  };

  const pieOptions = { plugins: { legend: { display: false } }, cutout: '70%' };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: FiTarget },
    { id: 'resume', label: 'Resume Tips', icon: FiEdit3 },
    { id: 'interview', label: 'Interview Prep', icon: FiHelpCircle },
    { id: 'company', label: 'Company Intel', icon: FiGlobe },
  ];

  return (
    <div className="min-h-screen bg-slate-950 py-12 px-4">
      <div className="fixed inset-0 z-0">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950" />
        <div className="absolute top-0 right-1/4 w-[500px] h-[500px] bg-green-500/5 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 max-w-6xl mx-auto">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white mb-4">Analysis Complete!</h1>
          <div className="space-y-2">
            {data.jobTitle && (
              <p className="text-xl text-white font-semibold">{data.jobTitle}</p>
            )}
            <div className="flex justify-center gap-4 text-sm">
              {data.positionType && (
                <span className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full">{data.positionType}</span>
              )}
              {data.experienceRequired && data.experienceRequired !== 'Not specified' && (
                <span className="px-3 py-1 bg-purple-500/20 text-purple-400 rounded-full">{data.experienceRequired}</span>
              )}
            </div>
          </div>
        </motion.div>

        {/* Score Card */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-8 mb-6">
          <div className="flex flex-col lg:flex-row items-center gap-8">
            <div className="relative w-48 h-48">
              <Pie data={pieData} options={pieOptions} />
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <span className={`text-4xl font-bold ${scoreInfo.text}`}>{Math.round(data.accuracy)}%</span>
                  <p className="text-xs text-gray-500">Match</p>
                </div>
              </div>
            </div>
            <div className="flex-1 text-center lg:text-left">
              <div className={`inline-block px-4 py-2 bg-gradient-to-r ${scoreInfo.gradient} rounded-full mb-4`}>
                <span className="text-white font-semibold">{scoreInfo.label}</span>
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">Your Resume Match Score</h2>
              <p className="text-gray-400">Based on AI analysis of your resume against the job requirements</p>
            </div>
          </div>
        </motion.div>

        {/* Tabs */}
        <div className="flex flex-wrap gap-2 mb-6">
          {tabs.map((tab) => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-lg font-medium text-sm flex items-center transition-all ${
                activeTab === tab.id ? 'bg-blue-600 text-white' : 'bg-white/5 text-gray-400 hover:bg-white/10'
              }`}>
              <tab.icon className="w-4 h-4 mr-2" /> {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <motion.div key={activeTab} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.2 }}>
          
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-white/5 rounded-xl border border-white/10 p-6">
                  <div className="flex items-center mb-4">
                    <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center mr-3">
                      <FiCheckCircle className="w-5 h-5 text-green-400" />
                    </div>
                    <h3 className="text-lg font-semibold text-white">Key Strengths</h3>
                  </div>
                  <ul className="space-y-2">
                    {data.strengths?.split(',').filter(Boolean).slice(0, 5).map((skill, idx) => (
                      <li key={idx} className="flex items-center text-gray-300">
                        <span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>{skill.trim()}
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="bg-white/5 rounded-xl border border-white/10 p-6">
                  <div className="flex items-center mb-4">
                    <div className="w-10 h-10 bg-red-500/20 rounded-lg flex items-center justify-center mr-3">
                      <FiXCircle className="w-5 h-5 text-red-400" />
                    </div>
                    <h3 className="text-lg font-semibold text-white">Skills to Develop</h3>
                  </div>
                  <ul className="space-y-2">
                    {data.weaknesses?.split(',').filter(Boolean).slice(0, 5).map((skill, idx) => (
                      <li key={idx} className="flex items-center text-gray-300">
                        <span className="w-2 h-2 bg-red-500 rounded-full mr-3"></span>{skill.trim()}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
              {data.atsRecommendations?.length > 0 && (
                <div className="bg-white/5 rounded-xl border border-white/10 p-6">
                  <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                    <FiTarget className="w-5 h-5 text-purple-400 mr-2" /> ATS Recommendations
                  </h3>
                  <ul className="space-y-2">
                    {data.atsRecommendations.slice(0, 5).map((rec, idx) => (
                      <li key={idx} className="text-gray-300 text-sm flex items-start">
                        <span className="text-purple-400 mr-2">•</span>{rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Resume Tips Tab */}
          {activeTab === 'resume' && (
            <div className="bg-white/5 rounded-xl border border-white/10 p-6">
              <h3 className="text-xl font-semibold text-white mb-6 flex items-center">
                <FiEdit3 className="w-6 h-6 text-cyan-400 mr-3" /> Tailored Resume Suggestions
              </h3>
              {data.tailoredResumeSuggestions?.length > 0 ? (
                <div className="space-y-4">
                  {data.tailoredResumeSuggestions.map((suggestion, idx) => (
                    <div key={idx} className="bg-white/5 rounded-lg p-4 border-l-4 border-cyan-500">
                      <p className="text-cyan-400 text-sm font-medium mb-1">{suggestion.section}</p>
                      <p className="text-white mb-2">{suggestion.change}</p>
                      <p className="text-gray-400 text-sm">{suggestion.reason}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-400">No specific resume suggestions available.</p>
              )}
            </div>
          )}

          {/* Interview Prep Tab */}
          {activeTab === 'interview' && (
            <div className="bg-white/5 rounded-xl border border-white/10 p-6">
              <h3 className="text-xl font-semibold text-white mb-6 flex items-center">
                <FiHelpCircle className="w-6 h-6 text-amber-400 mr-3" /> Likely Interview Questions
              </h3>
              {data.interviewQuestions?.length > 0 ? (
                <div className="space-y-4">
                  {data.interviewQuestions.map((q, idx) => (
                    <div key={idx} className="bg-white/5 rounded-lg p-4">
                      <p className="text-white font-medium mb-2">Q{idx + 1}: {q.question}</p>
                      <p className="text-amber-400 text-sm mb-1"><strong>Why they'll ask:</strong> {q.why}</p>
                      <p className="text-green-400 text-sm"><strong>Tip:</strong> {q.tip}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-400">No interview questions generated.</p>
              )}
            </div>
          )}

          {/* Company Intel Tab */}
          {activeTab === 'company' && (
            <div className="bg-white/5 rounded-xl border border-white/10 p-6">
              <h3 className="text-xl font-semibold text-white mb-6 flex items-center">
                <FiGlobe className="w-6 h-6 text-blue-400 mr-3" /> 
                Company Intel {data.companyIntel?.company_name && `- ${data.companyIntel.company_name}`}
              </h3>
              {data.companyIntel && Object.keys(data.companyIntel).length > 0 ? (
                <div className="space-y-6">
                  {data.companyIntel.recent_tech?.length > 0 && (
                    <div>
                      <h4 className="text-blue-400 font-medium mb-2">Recent Technologies</h4>
                      <div className="flex flex-wrap gap-2">
                        {data.companyIntel.recent_tech.map((tech, idx) => (
                          <span key={idx} className="px-3 py-1 bg-blue-500/20 text-blue-300 rounded-full text-sm">{tech}</span>
                        ))}
                      </div>
                    </div>
                  )}
                  {data.companyIntel.talking_points?.length > 0 && (
                    <div>
                      <h4 className="text-green-400 font-medium mb-2">Talking Points for Interview</h4>
                      <ul className="space-y-2">
                        {data.companyIntel.talking_points.map((point, idx) => (
                          <li key={idx} className="text-gray-300 flex items-start">
                            <span className="text-green-400 mr-2">→</span>{point}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {data.companyIntel.culture_notes?.length > 0 && (
                    <div>
                      <h4 className="text-purple-400 font-medium mb-2">Culture Notes</h4>
                      <p className="text-gray-300">{data.companyIntel.culture_notes.join(' ')}</p>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-gray-400">No company intel available. Try providing a company name with your job description.</p>
              )}
            </div>
          )}
        </motion.div>

        {/* Action Buttons */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}
          className="bg-white/5 rounded-xl border border-white/10 p-6 mt-6">
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            {data.hasReports && (
              <>
                <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} onClick={handleViewHtmlReport}
                  disabled={isLoadingHtml} className="px-6 py-3 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 rounded-xl font-medium flex items-center justify-center">
                  <FiEye className="mr-2" /> {isLoadingHtml ? 'Loading...' : 'View Report'}
                </motion.button>
                <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} onClick={handleDownloadPdf}
                  disabled={isDownloadingPdf} className="px-6 py-3 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-xl font-medium flex items-center justify-center">
                  <FiDownload className="mr-2" /> {isDownloadingPdf ? 'Downloading...' : 'Download PDF'}
                </motion.button>
              </>
            )}
            <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} onClick={() => navigate('/dashboard')}
              className="px-6 py-3 bg-white/5 hover:bg-white/10 text-gray-300 rounded-xl font-medium flex items-center justify-center">
              <FiHome className="mr-2" /> Dashboard
            </motion.button>
            <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} onClick={() => navigate('/upload-resume')}
              className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-medium flex items-center justify-center">
              <FiPlus className="mr-2" /> New Analysis
            </motion.button>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default ResultPage;
