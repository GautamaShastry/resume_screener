package com.resume.resume_analyzer.controller;

import com.resume.resume_analyzer.dto.JobDescriptionDto;
import com.resume.resume_analyzer.entity.JobDescription;
import com.resume.resume_analyzer.repository.JobDescriptionRepository;
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
    private final JobDescriptionRepository jobDescriptionRepository;
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

    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getJobDescriptionDetails(
            @PathVariable Long id,
            @RequestHeader("Authorization") String authorizationHeader) {
        try {
            String email = extractEmailFromAuthHeader(authorizationHeader);
            JobDescription job = jobDescriptionRepository.findById(id)
                    .orElseThrow(() -> new RuntimeException("Job description not found"));

            // Verify ownership
            if (!job.getUploadedBy().equals(email)) {
                return ResponseEntity.status(403).body(Map.of("error", "Unauthorized"));
            }

            Map<String, Object> response = new HashMap<>();
            response.put("id", job.getId());
            response.put("title", job.getTitle());
            response.put("description", job.getDescription());
            response.put("uploadedBy", job.getUploadedBy());

            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        }
    }

    private String extractEmailFromAuthHeader(String authHeader) {
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            String token = authHeader.substring(7);
            return jwtUtil.extractEmail(token);
        }
        throw new RuntimeException("Invalid Authorization Header");
    }
}