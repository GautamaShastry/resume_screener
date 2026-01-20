import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import axios from 'axios';
import { toast } from 'react-toastify';
import { FiMail, FiArrowRight, FiRefreshCw } from 'react-icons/fi';

const OtpVerification = ({ email, onResendOTP }) => {
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [isLoading, setIsLoading] = useState(false);
  const [timeLeft, setTimeLeft] = useState(120);
  const navigate = useNavigate();
  const inputs = useRef([]);

  const handleChange = (index, e) => {
    const value = e.target.value;
    if (!/^\d*$/.test(value)) return;
    
    const newOtp = [...otp];
    newOtp[index] = value.slice(0, 1);
    setOtp(newOtp);
    
    if (value && index < 5) {
      inputs.current[index + 1].focus();
    }
  };

  const handleKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      inputs.current[index - 1].focus();
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text');
    if (/^\d{6}$/.test(pastedData)) {
      const digits = pastedData.split('');
      setOtp(digits);
      inputs.current[5].focus();
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    const otpString = otp.join('');
    
    if (otpString.length !== 6) {
      toast.error('Please enter the complete OTP');
      return;
    }
    
    try {
      setIsLoading(true);
      const response = await axios.post('http://localhost:8001/api/auth/verify', {
        email,
        otpCode: otpString
      });
      
      localStorage.setItem('token', response.data.token);
      toast.success('Login successful!');
      navigate('/dashboard');
    } catch (error) {
      toast.error('Invalid or expired OTP. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft((prevTime) => {
        if (prevTime <= 0) {
          clearInterval(timer);
          return 0;
        }
        return prevTime - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-white/5 backdrop-blur-xl rounded-3xl border border-white/10 p-8 shadow-2xl w-full max-w-md"
    >
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <FiMail className="w-8 h-8 text-white" />
        </div>
        <h2 className="text-2xl font-bold text-white mb-2">Verify Your Email</h2>
        <p className="text-gray-400">We sent a 6-digit code to</p>
        <p className="text-blue-400 font-medium">{email}</p>
      </div>

      <div className="flex justify-center gap-3 mb-6">
        {[0, 1, 2, 3, 4, 5].map((index) => (
          <motion.input
            key={index}
            ref={(el) => (inputs.current[index] = el)}
            type="text"
            value={otp[index]}
            onChange={(e) => handleChange(index, e)}
            onKeyDown={(e) => handleKeyDown(index, e)}
            onPaste={index === 0 ? handlePaste : undefined}
            maxLength="1"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className="w-12 h-14 text-2xl font-bold text-center bg-white/5 border border-white/20 rounded-xl text-white focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all"
          />
        ))}
      </div>

      <div className="text-center mb-6">
        <div className="inline-flex items-center px-4 py-2 bg-white/5 rounded-full">
          <span className="text-gray-400 text-sm">Time remaining: </span>
          <span className={`ml-2 font-mono font-semibold ${timeLeft < 30 ? 'text-red-400' : 'text-blue-400'}`}>
            {formatTime(timeLeft)}
          </span>
        </div>
      </div>

      <motion.button
        onClick={handleVerify}
        disabled={isLoading}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className="w-full py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white rounded-xl font-semibold flex items-center justify-center shadow-lg shadow-blue-500/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed mb-4"
      >
        {isLoading ? (
          <span className="flex items-center">
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Verifying...
          </span>
        ) : (
          <>Verify Code <FiArrowRight className="ml-2" /></>
        )}
      </motion.button>

      <motion.button
        type="button"
        onClick={onResendOTP}
        disabled={timeLeft > 0 && timeLeft < 120}
        whileHover={timeLeft === 0 || timeLeft === 120 ? { scale: 1.02 } : {}}
        whileTap={timeLeft === 0 || timeLeft === 120 ? { scale: 0.98 } : {}}
        className={`w-full py-3 rounded-xl font-medium flex items-center justify-center transition-all ${
          timeLeft > 0 && timeLeft < 120
            ? 'text-gray-500 bg-white/5 cursor-not-allowed'
            : 'text-blue-400 bg-blue-500/10 hover:bg-blue-500/20 border border-blue-500/30'
        }`}
      >
        <FiRefreshCw className={`mr-2 ${timeLeft > 0 && timeLeft < 120 ? '' : 'animate-pulse'}`} />
        {timeLeft > 0 && timeLeft < 120 ? `Resend in ${formatTime(timeLeft)}` : 'Resend Code'}
      </motion.button>
    </motion.div>
  );
};

export default OtpVerification;
