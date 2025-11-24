package com.resume.resume_analyzer.service;

import com.resume.resume_analyzer.entity.JobDescription;
import com.resume.resume_analyzer.entity.MatchResult;
import com.resume.resume_analyzer.entity.Resume;
import com.resume.resume_analyzer.repository.JobDescriptionRepository;
import com.resume.resume_analyzer.repository.MatchResultRepository;
import com.resume.resume_analyzer.repository.ResumeRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

@Service
@RequiredArgsConstructor
public class MatchResultService {

    private final MatchResultRepository matchResultRepository;
    private final ResumeRepository resumeRepository;
    private final JobDescriptionRepository jobDescriptionRepository;
    private final RestTemplate restTemplate = new RestTemplate();

    // ✅ Use your deployed Flask AI service URL
    private final String AI_SERVICE_URL = "http://localhost:6000/api/analyze";

    public Map<String, Object> matchResume(Long resumeId, Long jobDescriptionId) {
        Optional<Resume> resumeOpt = resumeRepository.findById(resumeId);
        Optional<JobDescription> jobDescOpt = jobDescriptionRepository.findById(jobDescriptionId);

        if (resumeOpt.isEmpty() || jobDescOpt.isEmpty()) {
            throw new RuntimeException("Resume or Job Description not found.");
        }

        Resume resume = resumeOpt.get();
        JobDescription jobDescription = jobDescOpt.get();

        // Validation
        if (resume.getFileData() == null || resume.getFileData().length == 0) {
            throw new RuntimeException("Resume file data is empty");
        }

        if (jobDescription.getDescription() == null || jobDescription.getDescription().trim().isEmpty()) {
            throw new RuntimeException("Job description is empty");
        }

        try {
            // Prepare multipart/form-data
            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();

            ByteArrayResource fileAsResource = new ByteArrayResource(resume.getFileData()) {
                @Override
                public String getFilename() {
                    return resume.getFileName();
                }
            };

            body.add("file", fileAsResource);
            body.add("jobDescriptionText", jobDescription.getDescription());

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.MULTIPART_FORM_DATA);

            HttpEntity<MultiValueMap<String, Object>> entity = new HttpEntity<>(body, headers);

            ResponseEntity<Map> response = restTemplate.exchange(
                    AI_SERVICE_URL,
                    HttpMethod.POST,
                    entity,
                    Map.class
            );

            Map<String, Object> aiResponse = response.getBody();

            // Check for errors
            if (aiResponse != null && aiResponse.containsKey("error")) {
                throw new RuntimeException("AI service returned error: " + aiResponse.get("error"));
            }

            // ✅ Extract all fields from Flask response
            Double accuracy = parseDouble(aiResponse.get("accuracy"));
            String analysisId = (String) aiResponse.get("analysisId");
            Boolean hasReports = (Boolean) aiResponse.getOrDefault("hasReports", false);
            String jobTitle = (String) aiResponse.getOrDefault("jobTitle", "");
            String skills = aiResponse.get("skills") != null ? aiResponse.get("skills").toString() : "N/A";
            String strengths = aiResponse.get("strengths") != null ? aiResponse.get("strengths").toString() : "N/A";
            String weaknesses = aiResponse.get("weaknesses") != null ? aiResponse.get("weaknesses").toString() : "N/A";

            List<String> atsRecommendations = (List<String>) aiResponse.getOrDefault("atsRecommendations", List.of());
            List<String> careerAdvice = (List<String>) aiResponse.getOrDefault("careerAdvice", List.of());
            List<String> improvementSuggestions = (List<String>) aiResponse.getOrDefault("improvementSuggestions", List.of());

            // Save match result into DB
            MatchResult matchResult = new MatchResult();
            matchResult.setResumeId(resumeId);
            matchResult.setJobDescriptionId(jobDescriptionId);
            matchResult.setMatchScore(accuracy);
            matchResult.setExtractedSkills(skills);
            matchResult.setStrengths(strengths);
            matchResult.setWeaknesses(weaknesses);
            matchResult.setMatchTime(LocalDateTime.now());
            matchResult.setAnalysisId(analysisId); // ✅ Store analysisId

            MatchResult savedResult = matchResultRepository.save(matchResult);

            // ✅ Return comprehensive response to frontend
            Map<String, Object> responseMap = new HashMap<>();
            responseMap.put("matchResultId", savedResult.getId());
            responseMap.put("analysisId", analysisId);
            responseMap.put("accuracy", accuracy);
            responseMap.put("matchScore", accuracy);
            responseMap.put("skills", skills);
            responseMap.put("strengths", strengths);
            responseMap.put("weaknesses", weaknesses);
            responseMap.put("hasReports", hasReports);
            responseMap.put("jobTitle", jobTitle);
            responseMap.put("atsRecommendations", atsRecommendations);
            responseMap.put("careerAdvice", careerAdvice);
            responseMap.put("improvementSuggestions", improvementSuggestions);

            return responseMap;

        } catch (Exception e) {
            e.printStackTrace();
            throw new RuntimeException("Error processing resume or AI service: " + e.getMessage());
        }
    }

    private Double parseDouble(Object value) {
        if (value == null) return 0.0;
        if (value instanceof Number) {
            return ((Number) value).doubleValue();
        }
        try {
            return Double.parseDouble(value.toString());
        } catch (NumberFormatException e) {
            return 0.0;
        }
    }
}