package com.resume.resume_analyzer.repository;

import com.resume.resume_analyzer.entity.MatchResult;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface MatchResultRepository extends JpaRepository<MatchResult, Long> {
    List<MatchResult> findByResumeId(Long resumeId);
}

