package com.resume.resume_analyzer.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.stereotype.Service;

@Service
public class EmailService {

    @Autowired
    private JavaMailSender emailSender;

    public void sendOtpEmail(String to, String otp) {
        try {
            SimpleMailMessage message = new SimpleMailMessage();
            message.setFrom("gautamashastry@gmail.com");
            message.setTo(to);
            message.setSubject("Resume Analyzer - Your OTP Code");
            message.setText("Your OTP code is: " + otp + "\nThis code will expire in 2 minutes.");

            emailSender.send(message);
            System.out.println("OTP email sent successfully to: " + to);
        } catch (Exception e) {
            System.err.println("Failed to send OTP email: " + e.getMessage());
            e.printStackTrace();
            // In development, print the OTP to console
            System.out.println("DEV MODE - OTP for " + to + ": " + otp);
        }
    }
}