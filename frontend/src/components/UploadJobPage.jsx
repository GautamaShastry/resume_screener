import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { toast } from 'react-toastify';
import axios from 'axios';
import Loading from './Loading';
import { FiBriefcase, FiCheckCircle, FiArrowRight, FiInfo, FiGlobe, FiLink } from 'react-icons/fi';

const UploadJobPage = () => {
  const [title, setTitle] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [jobUrl, setJobUrl] = useState('');
  const [description, setDescription] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showExample, setShowExample] = useState(false);
  const navigate = useNavigate();

  const exampleJob = {
    title: "Senior Software Engineer",
    company: "Stripe",
    description: `We are seeking a talented Senior Software Engineer to join our growing team.

Key Responsibilities:
- Design and develop scalable web applications
- Lead technical discussions and code reviews
- Mentor junior developers

Required Skills:
- 5+ years of software development experience
- Strong proficiency in JavaScript, React, Node.js
- Experience with cloud platforms (AWS/Azure)
- Excellent problem-solving skills`
  };

  const handleUseExample = () => {
    setTitle(exampleJob.title);
    setCompanyName(exampleJob.company);
    setDescription(exampleJob.description);
    setShowExample(false);
    toast.info('Example loaded!');
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (description.length < 100) {
      toast.error('Job description should be at least 100 characters');
      return;
    }

    const token = localStorage.getItem('token');
    try {
      setIsLoading(true);
      const response = await axios.post('http://localhost:8001/api/job/upload', 
        { title, description, companyName, jobUrl }, 
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      localStorage.setItem('jobDescriptionId', response.data.jobDescriptionId);
      // Store company name for the analysis
      localStorage.setItem('companyName', companyName);
      localStorage.setItem('jobUrl', jobUrl);
      toast.success('Job description saved! Starting analysis...');
      navigate('/match');
    } catch (error) {
      toast.error('Upload failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) return <Loading />;

  const steps = [
    { num: 1, label: 'Upload Resume', done: true },
    { num: 2, label: 'Add Job', active: true },
    { num: 3, label: 'Get Analysis' },
  ];

  return (
    <div className="min-h-screen bg-slate-950 py-12 px-4">
      <div className="fixed inset-0 z-0">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950" />
        <div className="absolute top-0 right-1/4 w-[500px] h-[500px] bg-purple-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-1/4 w-[500px] h-[500px] bg-blue-500/5 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 max-w-3xl mx-auto">
        {/* Progress Steps */}
        <div className="flex justify-center mb-8">
          {steps.map((step, idx) => (
            <div key={idx} className="flex items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
                step.done ? 'bg-green-500 text-white'
                  : step.active ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white' 
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
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <FiBriefcase className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">Add Job Description</h1>
          <p className="text-gray-400">Paste the job posting you're targeting</p>
        </motion.div>

        {/* Form Card */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-8">
          <form onSubmit={handleUpload} className="space-y-5">
            {/* Job Title */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Job Title <span className="text-red-400">*</span>
              </label>
              <input type="text" value={title} onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g., Senior Software Engineer" required
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 transition-all"
              />
            </div>

            {/* Company Name - NEW */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                <FiGlobe className="inline w-4 h-4 mr-1" /> Company Name <span className="text-gray-500">(for company intel)</span>
              </label>
              <input type="text" value={companyName} onChange={(e) => setCompanyName(e.target.value)}
                placeholder="e.g., Stripe, Google, Amazon"
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all"
              />
            </div>

            {/* Job URL - NEW */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                <FiLink className="inline w-4 h-4 mr-1" /> Job Posting URL <span className="text-gray-500">(optional)</span>
              </label>
              <input type="url" value={jobUrl} onChange={(e) => setJobUrl(e.target.value)}
                placeholder="https://jobs.lever.co/company/..."
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all"
              />
            </div>

            {/* Job Description */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="block text-sm font-medium text-gray-300">
                  Job Description <span className="text-red-400">*</span>
                </label>
                <button type="button" onClick={() => setShowExample(!showExample)}
                  className="text-sm text-purple-400 hover:text-purple-300 font-medium">
                  {showExample ? 'Hide Example' : 'View Example'}
                </button>
              </div>

              {showExample && (
                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}
                  className="mb-4 bg-purple-500/10 border border-purple-500/20 rounded-xl p-4">
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-semibold text-purple-300">Example:</h4>
                    <button type="button" onClick={handleUseExample}
                      className="text-sm bg-purple-600 hover:bg-purple-500 text-white px-3 py-1 rounded-lg">
                      Use This
                    </button>
                  </div>
                  <p className="text-sm text-gray-300 font-medium">{exampleJob.title} at {exampleJob.company}</p>
                  <p className="text-xs text-gray-400 whitespace-pre-line mt-1">{exampleJob.description.substring(0, 150)}...</p>
                </motion.div>
              )}

              <textarea value={description} onChange={(e) => setDescription(e.target.value)}
                placeholder="Paste the complete job description here..." required
                className="w-full px-4 py-4 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 transition-all min-h-[200px] resize-y"
              />
              <div className="flex justify-between items-center mt-2">
                <span className={`text-sm font-medium ${description.length >= 100 ? 'text-green-400' : 'text-amber-400'}`}>
                  {description.length} characters {description.length < 100 && '(min 100)'}
                </span>
              </div>
            </div>

            <motion.button type="submit" disabled={description.length < 100}
              whileHover={description.length >= 100 ? { scale: 1.02 } : {}}
              whileTap={description.length >= 100 ? { scale: 0.98 } : {}}
              className={`w-full py-4 rounded-xl font-semibold flex items-center justify-center transition-all ${
                description.length >= 100
                  ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white shadow-lg shadow-purple-500/25'
                  : 'bg-white/10 text-gray-500 cursor-not-allowed'
              }`}>
              Analyze Resume <FiArrowRight className="ml-2" />
            </motion.button>
          </form>
        </motion.div>

        {/* Tips */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}
          className="mt-6 bg-blue-500/10 border border-blue-500/20 rounded-xl p-5">
          <h3 className="font-semibold text-blue-400 mb-2 flex items-center">
            <FiInfo className="mr-2" /> Tips for better results:
          </h3>
          <ul className="text-sm text-blue-200/70 space-y-1">
            <li>• Add the <strong>company name</strong> to get company intel and talking points</li>
            <li>• Include the complete job description with all requirements</li>
            <li>• The more details, the better the interview prep questions</li>
          </ul>
        </motion.div>
      </div>
    </div>
  );
};

export default UploadJobPage;
