package com.resume.resume_analyzer.controller;

import com.resume.resume_analyzer.dto.AuthRequestDto;
import com.resume.resume_analyzer.dto.AuthResponseDto;
import com.resume.resume_analyzer.dto.SignUpRequestDto;
import com.resume.resume_analyzer.service.AuthService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    @PostMapping("/login")
    public ResponseEntity<AuthResponseDto> login(@RequestBody AuthRequestDto request) {
        return ResponseEntity.ok(authService.login(request));
    }

    @PostMapping("/signup")
    public ResponseEntity<String> signup(@RequestBody SignUpRequestDto request) {
        return ResponseEntity.ok(authService.signup(request));
    }
}
