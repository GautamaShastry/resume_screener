package com.resume.resume_analyzer.repository;

import com.resume.resume_analyzer.entity.Resume;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ResumeRepository extends JpaRepository<Resume, Long> {
}
