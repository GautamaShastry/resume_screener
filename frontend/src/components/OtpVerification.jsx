// OTPVerification.jsx
import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';

const OtpVerification = ({ email, onResendOTP }) => {
    const [otp, setOtp] = useState(['', '', '', '', '', '']);
    const [isLoading, setIsLoading] = useState(false);
    const [timeLeft, setTimeLeft] = useState(120); // 2 minutes countdown
    const navigate = useNavigate();
    const inputs = useRef([]);

    // Handle input change and auto-focus next input
    const handleChange = (index, e) => {
        const value = e.target.value;
        
        // Only allow numbers
        if (!/^\d*$/.test(value)) return;
        
        // Update the OTP array
        const newOtp = [...otp];
        newOtp[index] = value.slice(0, 1); // Take only the first digit
        setOtp(newOtp);
        
        // Auto-focus next input after entering a digit
        if (value && index < 5) {
        inputs.current[index + 1].focus();
        }
    };

    // Handle backspace and auto-focus previous input
    const handleKeyDown = (index, e) => {
        if (e.key === 'Backspace' && !otp[index] && index > 0) {
        inputs.current[index - 1].focus();
        }
    };

    // Handle paste event
    const handlePaste = (e) => {
        e.preventDefault();
        const pastedData = e.clipboardData.getData('text');
        
        // Check if pasted content is a 6-digit number
        if (/^\d{6}$/.test(pastedData)) {
        // Split the pasted string into an array of characters
        const digits = pastedData.split('');
        setOtp(digits);
        
        // Focus the last input
        inputs.current[3].focus();
        }
    };

    // Verify OTP
    const handleVerify = async (e) => {
        e.preventDefault();
        const otpString = otp.join('');
        
        // Check if OTP is complete
        if (otpString.length !== 6) {
        toast.error('Please enter the complete the OTP Verification');
        return;
        }
        
        try {
        setIsLoading(true);
        const response = await axios.post('http://localhost:8001/api/auth/verify', {
            email,
            otpCode: otpString
        });
        
        // Save token and redirect to dashboard
        localStorage.setItem('token', response.data.token);
        toast.success('Login successful!');
        navigate('/dashboard');
        } catch (error) {
        toast.error('Invalid or expired OTP. Please try again.');
        } finally {
        setIsLoading(false);
        }
    };

    // Countdown timer
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

    // Format time as MM:SS
    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    return (
        <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h2 className="text-2xl font-bold text-center mb-6">Verify Your Account</h2>
        
        <div className="mb-6">
            <p className="text-center text-gray-700 mb-2">We sent a verification code to:</p>
            <p className="text-center font-semibold text-gray-900 mb-4">{email}</p>
            
            <div className="flex justify-center space-x-3 mb-6">
            {[0, 1, 2, 3, 4, 5].map((index) => (
                <input
                key={index}
                ref={(el) => (inputs.current[index] = el)}
                type="text"
                value={otp[index]}
                onChange={(e) => handleChange(index, e)}
                onKeyDown={(e) => handleKeyDown(index, e)}
                onPaste={index === 0 ? handlePaste : undefined}
                maxLength="1"
                className="w-14 h-14 text-2xl font-bold text-center border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
            ))}
            </div>
            
            <div className="text-center mb-4">
            <p className="text-gray-600">
                Time remaining: <span className="font-medium">{formatTime(timeLeft)}</span>
            </p>
            </div>
        </div>

        <button
            onClick={handleVerify}
            disabled={isLoading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded font-semibold transition duration-200 mb-4"
        >
            {isLoading ? 'Verifying...' : 'Verify'}
        </button>
        
        <button
            type="button"
            onClick={onResendOTP}
            disabled={timeLeft > 0 && timeLeft < 120}
            className={`w-full py-2 font-medium rounded border ${
            timeLeft > 0 && timeLeft < 120
                ? 'text-gray-400 border-gray-300 cursor-not-allowed'
                : 'text-blue-600 border-blue-600 hover:bg-blue-50'
            }`}
        >
            {timeLeft > 0 && timeLeft < 120 ? `Resend OTP in ${formatTime(timeLeft)}` : 'Resend OTP'}
        </button>
        </div>
    );
};

export default OtpVerification;