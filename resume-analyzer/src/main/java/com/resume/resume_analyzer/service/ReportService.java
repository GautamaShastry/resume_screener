package com.resume.resume_analyzer.service;

import com.resume.resume_analyzer.entity.MatchResult;
import com.resume.resume_analyzer.repository.MatchResultRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
@RequiredArgsConstructor
public class ReportService {

    private final MatchResultRepository matchResultRepository;
    private final RestTemplate restTemplate;

    private final String AI_SERVICE_BASE_URL = "http://localhost:6000";

    public byte[] getPdfReport(Long matchResultId) {
        System.out.println("=== getPdfReport called ===");
        System.out.println("Match Result ID: " + matchResultId);

        MatchResult result = matchResultRepository.findById(matchResultId)
                .orElseThrow(() -> new RuntimeException("Match result not found with ID: " + matchResultId));

        System.out.println("Found match result with Analysis ID: " + result.getAnalysisId());

        if (result.getAnalysisId() == null || result.getAnalysisId().isEmpty()) {
            throw new RuntimeException("Analysis ID not found for this match result");
        }

        try {
            String url = AI_SERVICE_BASE_URL + "/api/report/pdf/" + result.getAnalysisId();
            System.out.println("Fetching PDF from: " + url);

            ResponseEntity<byte[]> response = restTemplate.exchange(
                    url,
                    HttpMethod.GET,
                    null,
                    byte[].class
            );

            if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                System.out.println("✅ PDF fetched successfully, size: " + response.getBody().length + " bytes");
                return response.getBody();
            } else {
                throw new RuntimeException("Failed to fetch PDF from AI service. Status: " + response.getStatusCode());
            }
        } catch (Exception e) {
            System.err.println("❌ Error fetching PDF report: " + e.getMessage());
            e.printStackTrace();
            throw new RuntimeException("Error fetching PDF report: " + e.getMessage());
        }
    }

    public String getHtmlReport(Long matchResultId) {
        System.out.println("=== getHtmlReport called ===");
        System.out.println("Match Result ID: " + matchResultId);

        MatchResult result = matchResultRepository.findById(matchResultId)
                .orElseThrow(() -> new RuntimeException("Match result not found with ID: " + matchResultId));

        System.out.println("Found match result with Analysis ID: " + result.getAnalysisId());

        if (result.getAnalysisId() == null || result.getAnalysisId().isEmpty()) {
            throw new RuntimeException("Analysis ID not found for this match result");
        }

        try {
            String url = AI_SERVICE_BASE_URL + "/api/report/html/" + result.getAnalysisId();
            System.out.println("Fetching HTML from: " + url);

            ResponseEntity<String> response = restTemplate.exchange(
                    url,
                    HttpMethod.GET,
                    null,
                    String.class
            );

            if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                System.out.println("✅ HTML fetched successfully, length: " + response.getBody().length() + " characters");
                return response.getBody();
            } else {
                throw new RuntimeException("Failed to fetch HTML from AI service. Status: " + response.getStatusCode());
            }
        } catch (Exception e) {
            System.err.println("❌ Error fetching HTML report: " + e.getMessage());
            e.printStackTrace();
            throw new RuntimeException("Error fetching HTML report: " + e.getMessage());
        }
    }
}