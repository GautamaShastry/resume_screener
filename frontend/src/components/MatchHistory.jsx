import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import axios from 'axios';
import Loading from './Loading';
import { 
    FiClock, 
    FiFileText, 
    FiBriefcase, 
    FiTrendingUp, 
    FiDownload,
    FiEye,
    FiTrash2,
    FiCalendar
} from 'react-icons/fi';

const MatchHistory = () => {
    const [history, setHistory] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [filter, setFilter] = useState('all'); // all, high, medium, low
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
            console.error('Error fetching history:', error);
            toast.error('Failed to load match history');
        } finally {
            setIsLoading(false);
        }
    };

    const getScoreColor = (score) => {
        if (score >= 80) return 'text-green-600 bg-green-50 border-green-200';
        if (score >= 60) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
        return 'text-red-600 bg-red-50 border-red-200';
    };

    const getScoreBadge = (score) => {
        if (score >= 80) return { label: 'Excellent', color: 'bg-green-500' };
        if (score >= 60) return { label: 'Good', color: 'bg-yellow-500' };
        return { label: 'Needs Work', color: 'bg-red-500' };
    };

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
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
            const response = await axios.get(
                `http://localhost:8001/api/report/pdf/${matchResultId}`,
                {
                    headers: { Authorization: `Bearer ${token}` },
                    responseType: 'blob'
                }
            );

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `resume-analysis-${matchResultId}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
            toast.success('PDF downloaded successfully!');
        } catch (error) {
            toast.error('Failed to download PDF');
        }
    };

    const handleViewReport = async (matchResultId) => {
        const token = localStorage.getItem('token');
        try {
            const response = await axios.get(
                `http://localhost:8001/api/report/html/${matchResultId}`,
                {
                    headers: { Authorization: `Bearer ${token}` }
                }
            );

            const newWindow = window.open();
            newWindow.document.write(response.data);
            newWindow.document.close();
        } catch (error) {
            toast.error('Failed to view report');
        }
    };

    if (isLoading) return <Loading />;

    return (
        <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-gray-100 py-12 px-4">
            <div className="max-w-6xl mx-auto">
                {/* Header Section */}
                <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center">
                            <div className="bg-indigo-100 p-3 rounded-full mr-4">
                                <FiClock className="w-8 h-8 text-indigo-600" />
                            </div>
                            <div>
                                <h1 className="text-3xl font-bold text-gray-800">Match History</h1>
                                <p className="text-gray-600">View all your past resume analyses</p>
                            </div>
                        </div>
                        <div className="text-right">
                            <p className="text-3xl font-bold text-indigo-600">{history.length}</p>
                            <p className="text-sm text-gray-600">Total Matches</p>
                        </div>
                    </div>

                    {/* Filter Tabs */}
                    <div className="flex space-x-2 mt-6">
                        <button
                            onClick={() => setFilter('all')}
                            className={`px-4 py-2 rounded-lg font-medium transition duration-200 ${
                                filter === 'all'
                                    ? 'bg-indigo-600 text-white'
                                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                        >
                            All ({history.length})
                        </button>
                        <button
                            onClick={() => setFilter('high')}
                            className={`px-4 py-2 rounded-lg font-medium transition duration-200 ${
                                filter === 'high'
                                    ? 'bg-green-600 text-white'
                                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                        >
                            Excellent (≥80%)
                        </button>
                        <button
                            onClick={() => setFilter('medium')}
                            className={`px-4 py-2 rounded-lg font-medium transition duration-200 ${
                                filter === 'medium'
                                    ? 'bg-yellow-600 text-white'
                                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                        >
                            Good (60-79%)
                        </button>
                        <button
                            onClick={() => setFilter('low')}
                            className={`px-4 py-2 rounded-lg font-medium transition duration-200 ${
                                filter === 'low'
                                    ? 'bg-red-600 text-white'
                                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                        >
                            Needs Work (&lt;60%)
                        </button>
                    </div>
                </div>

                {/* History List */}
                {filteredHistory.length === 0 ? (
                    <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
                        <div className="bg-gray-100 p-6 rounded-full inline-block mb-4">
                            <FiClock className="w-16 h-16 text-gray-400" />
                        </div>
                        <h3 className="text-xl font-semibold text-gray-700 mb-2">No Match History</h3>
                        <p className="text-gray-500 mb-6">
                            {filter !== 'all' 
                                ? `No matches found in the ${filter} category` 
                                : "You haven't matched any resumes yet"}
                        </p>
                        <button
                            onClick={() => navigate('/upload-resume')}
                            className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200"
                        >
                            Start Your First Match
                        </button>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {filteredHistory.map((item) => {
                            const badge = getScoreBadge(item.matchScore);
                            return (
                                <div
                                    key={item.matchResultId}
                                    className="bg-white rounded-xl shadow-lg hover:shadow-xl transition duration-200 overflow-hidden"
                                >
                                    <div className="p-6">
                                        <div className="flex items-start justify-between">
                                            {/* Left Section - Match Details */}
                                            <div className="flex-1">
                                                <div className="flex items-center space-x-4 mb-4">
                                                    {/* Match Score Circle */}
                                                    <div className={`flex items-center justify-center w-20 h-20 rounded-full border-4 ${getScoreColor(item.matchScore)}`}>
                                                        <div className="text-center">
                                                            <p className="text-2xl font-bold">{Math.round(item.matchScore)}</p>
                                                            <p className="text-xs">Match</p>
                                                        </div>
                                                    </div>

                                                    {/* Job & Resume Info */}
                                                    <div className="flex-1">
                                                        <div className="flex items-center mb-2">
                                                            <span className={`${badge.color} text-white text-xs font-semibold px-3 py-1 rounded-full mr-2`}>
                                                                {badge.label}
                                                            </span>
                                                            <span className="text-xs text-gray-500 flex items-center">
                                                                <FiCalendar className="mr-1" />
                                                                {formatDate(item.matchTime)}
                                                            </span>
                                                        </div>
                                                        
                                                        <h3 className="text-lg font-bold text-gray-800 mb-1 flex items-center">
                                                            <FiBriefcase className="mr-2 text-purple-600" />
                                                            {item.jobTitle || 'Untitled Position'}
                                                        </h3>
                                                        
                                                        <p className="text-sm text-gray-600 mb-2 flex items-center">
                                                            <FiFileText className="mr-2 text-blue-600" />
                                                            {item.resumeFileName || 'Resume'}
                                                        </p>
                                                        
                                                        {item.jobDescriptionPreview && (
                                                            <p className="text-xs text-gray-500 line-clamp-2">
                                                                {item.jobDescriptionPreview}
                                                            </p>
                                                        )}
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Right Section - Actions */}
                                            <div className="flex flex-col space-y-2 ml-4">
                                                {item.hasReports && (
                                                    <>
                                                        <button
                                                            onClick={() => handleViewReport(item.matchResultId)}
                                                            className="flex items-center justify-center bg-blue-50 hover:bg-blue-100 text-blue-600 font-medium py-2 px-4 rounded-lg transition duration-200"
                                                        >
                                                            <FiEye className="mr-2" />
                                                            View
                                                        </button>
                                                        <button
                                                            onClick={() => handleDownloadPDF(item.matchResultId)}
                                                            className="flex items-center justify-center bg-green-50 hover:bg-green-100 text-green-600 font-medium py-2 px-4 rounded-lg transition duration-200"
                                                        >
                                                            <FiDownload className="mr-2" />
                                                            PDF
                                                        </button>
                                                    </>
                                                )}
                                            </div>
                                        </div>

                                        {/* Bottom Stats */}
                                        <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-gray-200">
                                            <div className="text-center">
                                                <p className="text-xs text-gray-500 mb-1">Resume ID</p>
                                                <p className="text-sm font-semibold text-gray-700">#{item.resumeId}</p>
                                            </div>
                                            <div className="text-center">
                                                <p className="text-xs text-gray-500 mb-1">Job ID</p>
                                                <p className="text-sm font-semibold text-gray-700">#{item.jobDescriptionId}</p>
                                            </div>
                                            <div className="text-center">
                                                <p className="text-xs text-gray-500 mb-1">Analysis ID</p>
                                                <p className="text-sm font-semibold text-gray-700 truncate">
                                                    {item.analysisId ? `...${item.analysisId.substring(item.analysisId.length - 8)}` : 'N/A'}
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
};

export default MatchHistory;