package com.resume.resume_analyzer.controller;

import com.resume.resume_analyzer.dto.JobDescriptionDto;
import com.resume.resume_analyzer.service.JobDescriptionService;
import com.resume.resume_analyzer.config.JWTUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/job")
@RequiredArgsConstructor
public class JobDescriptionController {

    private final JobDescriptionService jobDescriptionService;
    private final JWTUtil jwtUtil;

    @PostMapping("/upload")
    public ResponseEntity<String> uploadJobDescription(
            @RequestBody JobDescriptionDto jobDescriptionDto,
            @RequestHeader("Authorization") String authorizationHeader) {

        String email = extractEmailFromAuthHeader(authorizationHeader);

        jobDescriptionDto.setUploadedBy(email);  // automatically set uploadedBy field

        jobDescriptionService.saveJobDescription(jobDescriptionDto);
        return ResponseEntity.ok("Job Description Uploaded Successfully!");
    }

    private String extractEmailFromAuthHeader(String authHeader) {
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            String token = authHeader.substring(7);
            return jwtUtil.extractEmail(token);
        }
        throw new RuntimeException("Invalid Authorization Header");
    }
}
