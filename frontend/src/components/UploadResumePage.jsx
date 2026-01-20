import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { toast } from 'react-toastify';
import axios from 'axios';
import Loading from './Loading';
import { FiUploadCloud, FiFile, FiX, FiCheckCircle, FiArrowRight } from 'react-icons/fi';

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
    if (droppedFile) validateAndSetFile(droppedFile);
  };

  const validateAndSetFile = (selectedFile) => {
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    const maxSize = 5 * 1024 * 1024;

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
    if (selectedFile) validateAndSetFile(selectedFile);
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
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'multipart/form-data' }
      });
      localStorage.setItem('resumeId', response.data.resumeId);
      toast.success('Resume uploaded! Add job description next.');
      navigate('/upload-job');
    } catch (error) {
      toast.error('Upload failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) return <Loading />;

  const steps = [
    { num: 1, label: 'Upload Resume', active: true },
    { num: 2, label: 'Add Job', active: false },
    { num: 3, label: 'Get Analysis', active: false },
  ];

  return (
    <div className="min-h-screen bg-slate-950 py-12 px-4">
      <div className="fixed inset-0 z-0">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950" />
        <div className="absolute top-0 right-1/4 w-[500px] h-[500px] bg-blue-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-1/4 w-[500px] h-[500px] bg-purple-500/5 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 max-w-2xl mx-auto">
        {/* Progress Steps */}
        <div className="flex justify-center mb-8">
          {steps.map((step, idx) => (
            <div key={idx} className="flex items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
                step.active 
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white' 
                  : 'bg-white/10 text-gray-500'
              }`}>
                {step.num}
              </div>
              <span className={`ml-2 text-sm ${step.active ? 'text-white' : 'text-gray-500'}`}>
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
          <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <FiUploadCloud className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">Upload Your Resume</h1>
          <p className="text-gray-400">Drop your PDF or DOCX file to get started</p>
        </motion.div>

        {/* Upload Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-8"
        >
          <form onSubmit={handleUpload}>
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-xl p-12 text-center transition-all ${
                isDragging 
                  ? 'border-blue-500 bg-blue-500/10' 
                  : 'border-white/20 hover:border-white/40'
              }`}
            >
              {!file ? (
                <>
                  <FiUploadCloud className="w-16 h-16 mx-auto mb-4 text-gray-500" />
                  <h3 className="text-xl font-semibold text-white mb-2">
                    Drag & Drop your resume
                  </h3>
                  <p className="text-gray-500 mb-6">or</p>
                  <label className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-semibold rounded-xl cursor-pointer inline-block transition-all shadow-lg shadow-blue-500/25">
                    Browse Files
                    <input type="file" onChange={handleFileChange} accept=".pdf,.docx" className="hidden" />
                  </label>
                  <p className="text-sm text-gray-500 mt-4">PDF, DOCX (Max 5MB)</p>
                </>
              ) : (
                <motion.div
                  initial={{ scale: 0.9, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  className="bg-green-500/10 border border-green-500/30 rounded-xl p-6"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 bg-green-500/20 rounded-xl flex items-center justify-center">
                        <FiFile className="w-6 h-6 text-green-400" />
                      </div>
                      <div className="text-left">
                        <p className="font-semibold text-white">{file.name}</p>
                        <p className="text-sm text-gray-400">{(file.size / 1024).toFixed(2)} KB</p>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={() => setFile(null)}
                      className="text-red-400 hover:text-red-300 p-2 hover:bg-red-500/10 rounded-lg transition-all"
                    >
                      <FiX className="w-5 h-5" />
                    </button>
                  </div>
                  <div className="flex items-center justify-center mt-4 text-green-400">
                    <FiCheckCircle className="w-5 h-5 mr-2" />
                    <span className="font-medium">Ready to upload</span>
                  </div>
                </motion.div>
              )}
            </div>

            {file && (
              <motion.button
                type="submit"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="w-full mt-6 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-semibold rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/25 transition-all"
              >
                Continue to Job Description <FiArrowRight className="ml-2" />
              </motion.button>
            )}
          </form>
        </motion.div>

        {/* Tips */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="mt-6 bg-amber-500/10 border border-amber-500/20 rounded-xl p-5"
        >
          <h3 className="font-semibold text-amber-400 mb-2">Tips for best results:</h3>
          <ul className="text-sm text-amber-200/70 space-y-1">
            <li>• Use your most updated resume</li>
            <li>• Ensure the file is readable and not password-protected</li>
            <li>• Include relevant skills for accurate matching</li>
          </ul>
        </motion.div>
      </div>
    </div>
  );
};

export default UploadResumePage;
