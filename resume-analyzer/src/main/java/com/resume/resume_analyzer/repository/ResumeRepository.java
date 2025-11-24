package com.resume.resume_analyzer.repository;

import com.resume.resume_analyzer.entity.Resume;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ResumeRepository extends JpaRepository<Resume, Long> {
    List<Resume> findByUploadedBy(String uploadedBy);
}
