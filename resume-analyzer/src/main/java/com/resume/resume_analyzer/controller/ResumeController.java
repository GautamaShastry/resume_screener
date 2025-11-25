package com.resume.resume_analyzer.controller;

import com.resume.resume_analyzer.entity.Resume;
import com.resume.resume_analyzer.repository.ResumeRepository;
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
    private final ResumeRepository resumeRepository;
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

    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getResumeDetails(
            @PathVariable Long id,
            @RequestHeader("Authorization") String authorizationHeader) {
        try {
            String email = extractEmailFromAuthHeader(authorizationHeader);
            Resume resume = resumeRepository.findById(id)
                    .orElseThrow(() -> new RuntimeException("Resume not found"));

            // Verify ownership
            if (!resume.getUploadedBy().equals(email)) {
                return ResponseEntity.status(403).body(Map.of("error", "Unauthorized"));
            }

            Map<String, Object> response = new HashMap<>();
            response.put("id", resume.getId());
            response.put("fileName", resume.getFileName());
            response.put("uploadedAt", resume.getUploadTime());
            response.put("uploadedBy", resume.getUploadedBy());

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