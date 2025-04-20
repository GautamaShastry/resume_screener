package com.resume.resume_analyzer.controller;

import com.resume.resume_analyzer.dto.JobDescriptionDto;
import com.resume.resume_analyzer.service.JobDescriptionService;
import com.resume.resume_analyzer.config.JWTUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/job")
@RequiredArgsConstructor
public class JobDescriptionController {

    private final JobDescriptionService jobDescriptionService;
    private final JWTUtil jwtUtil;

    @PostMapping("/upload")
    public ResponseEntity<Map<String, Object>> uploadJobDescription(
            @RequestBody JobDescriptionDto jobDescriptionDto,
            @RequestHeader("Authorization") String authorizationHeader) {

        String email = extractEmailFromAuthHeader(authorizationHeader);
        jobDescriptionDto.setUploadedBy(email);

        Long jobDescriptionId = jobDescriptionService.saveJobDescription(jobDescriptionDto);

        Map<String, Object> response = new HashMap<>();
        response.put("jobDescriptionId", jobDescriptionId); // ✅ Put ID in Response
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
