package com.resume.resume_analyzer.controller;

import com.resume.resume_analyzer.dto.AuthRequestDto;
import com.resume.resume_analyzer.dto.AuthResponseDto;
import com.resume.resume_analyzer.dto.OtpVerificationDto;
import com.resume.resume_analyzer.dto.SignUpRequestDto;
import com.resume.resume_analyzer.service.AuthService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    @PostMapping("/login")
    public ResponseEntity<Map<String, Object>> login(@RequestBody AuthRequestDto request) {
        Map<String, Object> response = authService.login(request);
        return ResponseEntity.ok(response);
    }

    @PostMapping("/verify")
    public ResponseEntity<AuthResponseDto> verifyOtp(@RequestBody OtpVerificationDto request) {
        return ResponseEntity.ok(authService.verifyOtp(request));
    }

    @PostMapping("/signup")
    public ResponseEntity<String> signup(@RequestBody SignUpRequestDto request) {
        return ResponseEntity.ok(authService.signup(request));
    }

    @PostMapping("/resend-otp")
    public ResponseEntity<Map<String, String>> resendOtp(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        String message = authService.resendOtp(email);

        Map<String, String> response = new HashMap<>();
        response.put("message", message);
        response.put("email", email);

        return ResponseEntity.ok(response);
    }
}
