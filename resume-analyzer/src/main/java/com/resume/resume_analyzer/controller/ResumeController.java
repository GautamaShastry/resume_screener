package com.resume.resume_analyzer.controller;

import com.resume.resume_analyzer.service.ResumeService;
import com.resume.resume_analyzer.config.JWTUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/resume")
@RequiredArgsConstructor
public class ResumeController {

    private final ResumeService resumeService;
    private final JWTUtil jwtUtil;

    @PostMapping("/upload")
    public ResponseEntity<Map<String, Object>> uploadResume(
            @RequestParam("file") MultipartFile file,
            @RequestHeader("Authorization") String authorizationHeader) {

        String email = extractEmailFromAuthHeader(authorizationHeader);
        Long resumeId = resumeService.saveResume(email, file); // Return saved ID

        Map<String, Object> response = new HashMap<>();
        response.put("resumeId", resumeId); // ✅ Return in response
        return ResponseEntity.ok(response);
    }

    private String extractEmailFromAuthHeader(String authHeader) {
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            String token = authHeader.substring(7);
            return jwtUtil.extractEmail(token);
        }
        throw new RuntimeException("Invalid Authorization Header");
    }
}
