package com.resume.resume_analyzer.service;

import com.resume.resume_analyzer.dto.AuthRequestDto;
import com.resume.resume_analyzer.dto.AuthResponseDto;
import com.resume.resume_analyzer.dto.OtpVerificationDto;
import com.resume.resume_analyzer.dto.SignUpRequestDto;
import com.resume.resume_analyzer.entity.User;
import com.resume.resume_analyzer.repository.UserRepository;
import com.resume.resume_analyzer.config.JWTUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JWTUtil jwtUtil;
    private final OtpService otpService;

    public Map<String, Object> login(AuthRequestDto request) {
        User user = userRepository.findByEmail(request.getEmail())
                .orElseThrow(() -> new RuntimeException("Invalid email or password"));

        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new RuntimeException("Invalid email or password");
        }

        // Generate and send OTP
        String otpMessage = otpService.generateAndSendOTP(user.getEmail());

        Map<String, Object> response = new HashMap<>();
        response.put("message", otpMessage);
        response.put("email", user.getEmail());

        return response;
    }

    public AuthResponseDto verifyOtp(OtpVerificationDto request) {

        boolean isValid = otpService.verifyOTP(request.getEmail(), request.getOtpCode());

        if (!isValid) {
            throw new RuntimeException("Invalid or expired OTP");
        }

        User user = userRepository.findByEmail(request.getEmail())
                .orElseThrow(() -> new RuntimeException("Invalid email or password"));

        String token = jwtUtil.generateToken(user.getEmail());

        return new AuthResponseDto(user.getName(), user.getEmail(), token);
    }

    public String signup(SignUpRequestDto request) {
        if (userRepository.findByEmail(request.getEmail()).isPresent()) {
            throw new RuntimeException("Email already registered");
        }
        User user = new User();
        user.setName(request.getName());
        user.setEmail(request.getEmail());
        user.setPassword(passwordEncoder.encode(request.getPassword()));
        userRepository.save(user);
        return "User registered successfully";
    }

    public String resendOtp(String email) {
        userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("User not found"));

        return otpService.generateAndSendOTP(email);
    }
}
