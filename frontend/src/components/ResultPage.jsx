import { useLocation, useNavigate } from 'react-router-dom';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { useEffect, useState } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import { FiDownload, FiEye } from 'react-icons/fi';

ChartJS.register(ArcElement, Tooltip, Legend);

const ResultPage = () => {
    const { state } = useLocation();
    const navigate = useNavigate();
    const [data, setData] = useState(null);
    const [isDownloadingPdf, setIsDownloadingPdf] = useState(false);
    const [isLoadingHtml, setIsLoadingHtml] = useState(false);

    const BACKEND_URL = 'http://localhost:8001';

    useEffect(() => {
        if (state) {
            console.log('Result data received:', state);
            setData(state);
        }
    }, [state]);

    const handleDownloadPdf = async () => {
        if (!data?.matchResultId) {
            toast.error('Match result ID not found');
            return;
        }

        try {
            setIsDownloadingPdf(true);
            const token = localStorage.getItem('token');
            
            const response = await axios.get(
                `${BACKEND_URL}/api/report/pdf/${data.matchResultId}`,
                {
                    headers: { 
                        'Authorization': `Bearer ${token}` 
                    },
                    responseType: 'blob'
                }
            );

            // Create download link
            const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `resume-analysis-${data.matchResultId}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);
            
            toast.success('PDF report downloaded successfully!');
        } catch (error) {
            console.error('PDF download error:', error);
            toast.error(error.response?.data?.message || 'Failed to download PDF report');
        } finally {
            setIsDownloadingPdf(false);
        }
    };

    const handleViewHtmlReport = async () => {
        if (!data?.matchResultId) {
            toast.error('Match result ID not found');
            return;
        }

        try {
            setIsLoadingHtml(true);
            const token = localStorage.getItem('token');
            
            const response = await axios.get(
                `${BACKEND_URL}/api/report/html/${data.matchResultId}`,
                {
                    headers: { 
                        'Authorization': `Bearer ${token}` 
                    }
                }
            );

            // Open HTML in new window
            const newWindow = window.open('', '_blank');
            newWindow.document.write(response.data);
            newWindow.document.close();
        } catch (error) {
            console.error('HTML report error:', error);
            toast.error('Failed to load HTML report');
        } finally {
            setIsLoadingHtml(false);
        }
    };

    if (!data) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-blue-500 mx-auto"></div>
                    <p className="mt-4 text-lg text-gray-600">Loading results...</p>
                </div>
            </div>
        );
    }

    const pieData = {
        labels: ['Match %', 'Mismatch %'],
        datasets: [
            {
                data: [data.accuracy, 100 - data.accuracy],
                backgroundColor: ['#4ade80', '#f87171'],
                hoverOffset: 4,
            },
        ],
    };

    return (
        <div className="min-h-screen bg-gray-100 flex flex-col items-center p-6">
            <h2 className="text-3xl font-bold mb-6 text-blue-700">Resume Match Analysis</h2>

            {data.jobTitle && (
                <p className="text-lg text-gray-600 mb-4">Position: <span className="font-semibold">{data.jobTitle}</span></p>
            )}

            <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-5xl">
                <div className="flex flex-col lg:flex-row items-center justify-around mb-8">
                    {/* Pie Chart */}
                    <div className="w-72 h-72 mb-8 lg:mb-0">
                        <Pie data={pieData} />
                    </div>

                    {/* Match Details */}
                    <div className="flex flex-col space-y-6">
                        <div>
                            <h3 className="text-3xl font-bold text-blue-600">
                                Match Score: {data.accuracy}%
                            </h3>
                            <p className="text-sm text-gray-500 mt-1">
                                {data.hasReports ? '✅ Detailed reports available' : ''}
                            </p>
                        </div>

                        <div>
                            <h4 className="text-lg font-semibold mb-2 text-green-600">✓ Key Strengths</h4>
                            <ul className="list-disc ml-5 space-y-1">
                                {data.strengths
                                    ?.split(',')
                                    .filter(Boolean)
                                    .slice(0, 5)
                                    .map((skill, idx) => (
                                        <li key={idx} className="text-gray-700">{skill.trim()}</li>
                                    ))}
                            </ul>
                        </div>

                        <div>
                            <h4 className="text-lg font-semibold mb-2 text-red-600">✗ Areas for Improvement</h4>
                            <ul className="list-disc ml-5 space-y-1">
                                {data.weaknesses
                                    ?.split(',')
                                    .filter(Boolean)
                                    .slice(0, 5)
                                    .map((skill, idx) => (
                                        <li key={idx} className="text-gray-700">{skill.trim()}</li>
                                    ))}
                            </ul>
                        </div>
                    </div>
                </div>

                {/* Action Buttons */}
                {data.hasReports && (
                    <div className="border-t pt-6 mt-6">
                        <h3 className="text-xl font-semibold mb-4 text-center">Download Detailed Reports</h3>
                        <div className="flex flex-col sm:flex-row gap-4 justify-center">
                            <button
                                onClick={handleViewHtmlReport}
                                disabled={isLoadingHtml}
                                className="flex items-center justify-center bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 disabled:bg-gray-400"
                            >
                                <FiEye className="mr-2" size={20} />
                                {isLoadingHtml ? 'Loading...' : 'View Full Report'}
                            </button>

                            <button
                                onClick={handleDownloadPdf}
                                disabled={isDownloadingPdf}
                                className="flex items-center justify-center bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 disabled:bg-gray-400"
                            >
                                <FiDownload className="mr-2" size={20} />
                                {isDownloadingPdf ? 'Downloading...' : 'Download PDF Report'}
                            </button>
                        </div>
                    </div>
                )}

                {/* Additional Insights (if available) */}
                {(data.atsRecommendations?.length > 0 || data.careerAdvice?.length > 0) && (
                    <div className="border-t pt-6 mt-6">
                        <h3 className="text-xl font-semibold mb-4">Additional Insights</h3>
                        
                        {data.atsRecommendations?.length > 0 && (
                            <div className="mb-4">
                                <h4 className="font-semibold text-purple-600 mb-2">ATS Recommendations:</h4>
                                <ul className="list-disc ml-5 space-y-1">
                                    {data.atsRecommendations.slice(0, 3).map((rec, idx) => (
                                        <li key={idx} className="text-gray-700">{rec}</li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        {data.careerAdvice?.length > 0 && (
                            <div>
                                <h4 className="font-semibold text-blue-600 mb-2">Career Advice:</h4>
                                <ul className="list-disc ml-5 space-y-1">
                                    {data.careerAdvice.slice(0, 3).map((advice, idx) => (
                                        <li key={idx} className="text-gray-700">{advice}</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ResultPage;