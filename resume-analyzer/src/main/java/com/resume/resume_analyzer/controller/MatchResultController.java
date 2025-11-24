package com.resume.resume_analyzer.controller;

import com.resume.resume_analyzer.dto.MatchHistoryDto;
import com.resume.resume_analyzer.service.MatchResultService;
import com.resume.resume_analyzer.config.JWTUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/match")
public class MatchResultController {

    @Autowired
    private MatchResultService matchResultService;

    @Autowired
    private JWTUtil jwtUtil;

    @PostMapping("/matchResume")
    public ResponseEntity<Map<String, Object>> matchResume(
            @RequestParam("resumeId") Long resumeId,
            @RequestParam("jobDescriptionId") Long jobDescriptionId) {
        try {
            Map<String, Object> result = matchResultService.matchResume(resumeId, jobDescriptionId);
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        }
    }

    @GetMapping("/history")
    public ResponseEntity<List<MatchHistoryDto>> getMatchHistory(
            @RequestHeader("Authorization") String authorizationHeader) {
        try {
            String email = extractEmailFromAuthHeader(authorizationHeader);
            List<MatchHistoryDto> history = matchResultService.getMatchHistory(email);
            return ResponseEntity.ok(history);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(null);
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