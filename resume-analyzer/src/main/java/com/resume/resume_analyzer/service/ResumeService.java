package com.resume.resume_analyzer.service;

import com.resume.resume_analyzer.entity.Resume;
import com.resume.resume_analyzer.repository.ResumeRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
public class ResumeService {

    private final ResumeRepository resumeRepository;

    public void saveResume(String uploadedBy, MultipartFile file) {
        try {
            Resume resume = new Resume();
            resume.setFileName(file.getOriginalFilename());
            resume.setFileData(file.getBytes());
            resume.setUploadedBy(uploadedBy);
            resume.setUploadTime(LocalDateTime.now());

            resumeRepository.save(resume);

        } catch (IOException e) {
            throw new RuntimeException("Failed to save resume", e);
        }
    }
}
