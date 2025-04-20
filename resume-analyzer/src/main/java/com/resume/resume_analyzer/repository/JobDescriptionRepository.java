package com.resume.resume_analyzer.repository;

import com.resume.resume_analyzer.entity.JobDescription;
import org.springframework.data.jpa.repository.JpaRepository;

public interface JobDescriptionRepository extends JpaRepository<JobDescription, Long> {
}