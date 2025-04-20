package com.resume.resume_analyzer.service;

import com.resume.resume_analyzer.dto.JobDescriptionDto;
import com.resume.resume_analyzer.entity.JobDescription;
import com.resume.resume_analyzer.repository.JobDescriptionRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class JobDescriptionService {

    private final JobDescriptionRepository jobDescriptionRepository;

    public Long saveJobDescription(JobDescriptionDto jobDescriptionDto) {
        JobDescription jobDescription = new JobDescription();
        jobDescription.setTitle(jobDescriptionDto.getTitle());
        jobDescription.setDescription(jobDescriptionDto.getDescription());
        jobDescription.setUploadedBy(jobDescriptionDto.getUploadedBy());

        JobDescription savedJob = jobDescriptionRepository.save(jobDescription);
        return savedJob.getId(); // ✅ Return the saved Job Description ID
    }
}
