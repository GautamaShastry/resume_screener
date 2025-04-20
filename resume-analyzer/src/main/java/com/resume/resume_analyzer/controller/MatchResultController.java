package com.resume.resume_analyzer.controller;

import com.resume.resume_analyzer.service.MatchResultService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/match")
public class MatchResultController {

    @Autowired
    private MatchResultService matchResultService;

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
}
