import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import axios from 'axios';
import Loading from './Loading';
import { FiUploadCloud, FiFile, FiX, FiCheckCircle } from 'react-icons/fi';

const UploadResumePage = () => {
    const [file, setFile] = useState(null);
    const [isDragging, setIsDragging] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();

    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);
        
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile) {
            validateAndSetFile(droppedFile);
        }
    };

    const validateAndSetFile = (selectedFile) => {
        const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
        const maxSize = 5 * 1024 * 1024; // 5MB

        if (!allowedTypes.includes(selectedFile.type)) {
            toast.error('Please upload a PDF or DOCX file');
            return;
        }

        if (selectedFile.size > maxSize) {
            toast.error('File size must be less than 5MB');
            return;
        }

        setFile(selectedFile);
        toast.success('File selected successfully!');
    };

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            validateAndSetFile(selectedFile);
        }
    };

    const handleRemoveFile = () => {
        setFile(null);
    };

    const handleUpload = async (e) => {
        e.preventDefault();
        if (!file) {
            toast.error('Please upload a resume');
            return;
        }

        const token = localStorage.getItem('token');
        const formData = new FormData();
        formData.append('file', file);

        try {
            setIsLoading(true);
            const response = await axios.post('http://localhost:8001/api/resume/upload', formData, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'multipart/form-data'
                }
            });
            localStorage.setItem('resumeId', response.data.resumeId);
            toast.success('Resume uploaded successfully! Please upload Job Description next.');
            navigate('/upload-job');
        } catch (error) {
            toast.error('Resume upload failed. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    if (isLoading) return <Loading />;

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-gray-100 flex flex-col items-center justify-start pt-12 px-4">
            {/* Header Section */}
            <div className="text-center mb-8 max-w-2xl">
                <div className="inline-block p-3 bg-blue-100 rounded-full mb-4">
                    <FiUploadCloud className="w-12 h-12 text-blue-600" />
                </div>
                <h1 className="text-4xl font-bold text-gray-800 mb-3">Upload Your Resume</h1>
                <p className="text-lg text-gray-600">
                    Upload your resume to get an AI-powered analysis and match it with job descriptions
                </p>
            </div>

            {/* Main Upload Container */}
            <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-2xl">
                {/* Upload Area */}
                <form onSubmit={handleUpload}>
                    <div
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onDrop={handleDrop}
                        className={`border-3 border-dashed rounded-xl p-12 text-center transition-all duration-300 ${
                            isDragging 
                                ? 'border-blue-500 bg-blue-50' 
                                : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
                        }`}
                    >
                        {!file ? (
                            <>
                                <FiUploadCloud className="w-20 h-20 mx-auto mb-4 text-gray-400" />
                                <h3 className="text-xl font-semibold text-gray-700 mb-2">
                                    Drag & Drop your resume here
                                </h3>
                                <p className="text-gray-500 mb-6">or</p>
                                <label className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-8 rounded-lg cursor-pointer inline-block transition duration-200">
                                    Browse Files
                                    <input
                                        type="file"
                                        onChange={handleFileChange}
                                        accept=".pdf,.docx"
                                        className="hidden"
                                    />
                                </label>
                                <p className="text-sm text-gray-500 mt-4">
                                    Supported formats: PDF, DOCX (Max 5MB)
                                </p>
                            </>
                        ) : (
                            <div className="bg-green-50 border-2 border-green-200 rounded-lg p-6">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center space-x-4">
                                        <div className="bg-green-100 p-3 rounded-full">
                                            <FiFile className="w-8 h-8 text-green-600" />
                                        </div>
                                        <div className="text-left">
                                            <p className="font-semibold text-gray-800">{file.name}</p>
                                            <p className="text-sm text-gray-500">
                                                {(file.size / 1024).toFixed(2)} KB
                                            </p>
                                        </div>
                                    </div>
                                    <button
                                        type="button"
                                        onClick={handleRemoveFile}
                                        className="text-red-500 hover:text-red-700 transition duration-200"
                                    >
                                        <FiX className="w-6 h-6" />
                                    </button>
                                </div>
                                <div className="flex items-center justify-center mt-4 text-green-600">
                                    <FiCheckCircle className="w-5 h-5 mr-2" />
                                    <span className="font-medium">Ready to upload</span>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Upload Button */}
                    {file && (
                        <button
                            type="submit"
                            className="w-full mt-6 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold py-4 rounded-lg transition duration-200 transform hover:scale-105 shadow-lg"
                        >
                            Continue to Job Description →
                        </button>
                    )}
                </form>

                {/* Info Cards */}
                <div className="grid md:grid-cols-3 gap-4 mt-8">
                    <div className="bg-blue-50 p-4 rounded-lg text-center">
                        <div className="text-2xl font-bold text-blue-600 mb-1">1</div>
                        <p className="text-sm text-gray-700">Upload Resume</p>
                    </div>
                    <div className="bg-gray-100 p-4 rounded-lg text-center">
                        <div className="text-2xl font-bold text-gray-400 mb-1">2</div>
                        <p className="text-sm text-gray-500">Add Job Description</p>
                    </div>
                    <div className="bg-gray-100 p-4 rounded-lg text-center">
                        <div className="text-2xl font-bold text-gray-400 mb-1">3</div>
                        <p className="text-sm text-gray-500">Get Analysis</p>
                    </div>
                </div>
            </div>

            {/* Tips Section */}
            <div className="mt-8 max-w-2xl bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                <h3 className="font-semibold text-yellow-800 mb-3 flex items-center">
                    <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                    </svg>
                    Tips for best results:
                </h3>
                <ul className="text-sm text-yellow-800 space-y-1 list-disc list-inside">
                    <li>Use your most updated resume</li>
                    <li>Ensure the file is readable and not password-protected</li>
                    <li>Include relevant skills and experience for accurate matching</li>
                </ul>
            </div>
        </div>
    );
};

export default UploadResumePage;