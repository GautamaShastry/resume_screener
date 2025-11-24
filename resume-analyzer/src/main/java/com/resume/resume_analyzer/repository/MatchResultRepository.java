package com.resume.resume_analyzer.repository;

import com.resume.resume_analyzer.entity.MatchResult;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface MatchResultRepository extends JpaRepository<MatchResult, Long> {
    List<MatchResult> findByResumeId(Long resumeId);
    List<MatchResult> findAllByResumeIdIn(List<Long> resumeIds);
    long countByResumeIdIn(List<Long> resumeIds);
}

