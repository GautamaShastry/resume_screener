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
import java.util.Map;
import java.util.Optional;

@Service
@RequiredArgsConstructor
public class MatchResultService {

    private final MatchResultRepository matchResultRepository;
    private final ResumeRepository resumeRepository;
    private final JobDescriptionRepository jobDescriptionRepository;
    private final RestTemplate restTemplate = new RestTemplate();

    private final String AI_SERVICE_URL = "http://localhost:6000/api/analyze";

    public String matchResume(Long resumeId, Long jobDescriptionId) {
        Optional<Resume> resumeOpt = resumeRepository.findById(resumeId);
        Optional<JobDescription> jobDescOpt = jobDescriptionRepository.findById(jobDescriptionId);

        if (resumeOpt.isEmpty() || jobDescOpt.isEmpty()) {
            throw new RuntimeException("Resume or Job Description not found.");
        }

        Resume resume = resumeOpt.get();
        JobDescription jobDescription = jobDescOpt.get();

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

            MatchResult matchResult = new MatchResult();
            matchResult.setResumeId(resumeId);
            matchResult.setJobDescriptionId(jobDescriptionId);
            matchResult.setMatchScore(Double.valueOf(aiResponse.get("matchScore").toString()));
            matchResult.setExtractedSkills(aiResponse.get("skills").toString());
            matchResult.setStrengths(aiResponse.get("strengths").toString());
            matchResult.setWeaknesses(aiResponse.get("weaknesses").toString());
            matchResult.setMatchTime(LocalDateTime.now());

            matchResultRepository.save(matchResult);

            return "Resume matched successfully with AI score: " + matchResult.getMatchScore();

        } catch (Exception e) {
            throw new RuntimeException("Error processing resume or AI service: " + e.getMessage());
        }
    }
}
