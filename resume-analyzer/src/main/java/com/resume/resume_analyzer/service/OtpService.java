package com.resume.resume_analyzer.service;

import com.resume.resume_analyzer.entity.Otp;
import com.resume.resume_analyzer.repository.OtpRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.Optional;
import java.util.Random;

@Service
@RequiredArgsConstructor
public class OtpService {

    private final OtpRepository otpRepository;
    private final EmailService emailService;

    public String generateAndSendOTP(String email) {
        // Delete any existing unverified OTP for this email
        Optional<Otp> existingOtp = otpRepository.findByEmailAndVerifiedFalse(email);
        existingOtp.ifPresent(otp -> otpRepository.delete(otp));

        // Generate random 6-digit OTP
        String otpCode = generateRandomOTP();

        // Create new OTP entity
        Otp otp = new Otp();
        otp.setEmail(email);
        otp.setOtpCode(otpCode);
        otp.setExpiryTime(LocalDateTime.now().plusMinutes(2)); // OTP valid for 2 minutes
        otp.setVerified(false);

        // Save to database
        otpRepository.save(otp);

        // Send OTP via email
        emailService.sendOtpEmail(email, otpCode);

        return "OTP sent successfully to " + email;
    }

    public boolean verifyOTP(String email, String otpCode) {
        Optional<Otp> otpOpt = otpRepository.findByEmailAndOtpCodeAndVerifiedFalse(email, otpCode);

        if (otpOpt.isEmpty()) {
            return false;
        }

        Otp otp = otpOpt.get();

        // Check if OTP is expired
        if (otp.getExpiryTime().isBefore(LocalDateTime.now())) {
            return false;
        }

        // Mark OTP as verified
        otp.setVerified(true);
        otpRepository.save(otp);

        return true;
    }

    private String generateRandomOTP() {
        Random random = new Random();
        int number = random.nextInt(900000) + 100000;
        return String.format("%06d", number); // Ensures 6-digit format with leading zeros
    }
}