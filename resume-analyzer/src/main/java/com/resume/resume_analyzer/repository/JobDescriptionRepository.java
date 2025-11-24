package com.resume.resume_analyzer.repository;

import com.resume.resume_analyzer.entity.JobDescription;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface JobDescriptionRepository extends JpaRepository<JobDescription, Long> {
    List<JobDescription> findByUploadedBy(String email);
    long countByUploadedBy(String email);
}