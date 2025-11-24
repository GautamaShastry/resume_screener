package com.resume.resume_analyzer.service;

import com.resume.resume_analyzer.dto.UserProfileDto;
import com.resume.resume_analyzer.entity.User;
import com.resume.resume_analyzer.repository.UserRepository;
import com.resume.resume_analyzer.repository.ResumeRepository;
import com.resume.resume_analyzer.repository.JobDescriptionRepository;
import com.resume.resume_analyzer.repository.MatchResultRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;
    private final ResumeRepository resumeRepository;
    private final JobDescriptionRepository jobDescriptionRepository;
    private final MatchResultRepository matchResultRepository;

    public UserProfileDto getUserProfile(String email) {
        System.out.println("=== UserService.getUserProfile called ===");
        System.out.println("Email: " + email);

        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("User not found"));

        System.out.println("User found: " + user.getName());

        // ✅ Use countBy methods instead of loading full entities
        long resumeCount = resumeRepository.countByUploadedBy(email);
        System.out.println("Resume count: " + resumeCount);

        long jobDescriptionCount = jobDescriptionRepository.countByUploadedBy(email);
        System.out.println("Job description count: " + jobDescriptionCount);

        // For match count, we still need resume IDs but don't load the LOB data
        long matchCount = matchResultRepository.countByResumeIdIn(
                resumeRepository.findIdsByUploadedBy(email)
        );
        System.out.println("Match count: " + matchCount);

        // Create and return DTO
        UserProfileDto profileDto = new UserProfileDto();
        profileDto.setName(user.getName());
        profileDto.setEmail(user.getEmail());
        profileDto.setResumeCount((int) resumeCount);
        profileDto.setJobDescriptionCount((int) jobDescriptionCount);
        profileDto.setMatchCount((int) matchCount);

        System.out.println("Profile DTO created successfully");
        return profileDto;
    }
}