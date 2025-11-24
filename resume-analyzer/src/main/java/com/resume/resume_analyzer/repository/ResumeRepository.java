package com.resume.resume_analyzer.repository;

import com.resume.resume_analyzer.entity.Resume;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ResumeRepository extends JpaRepository<Resume, Long> {
    List<Resume> findByUploadedBy(String uploadedBy);
    long countByUploadedBy(String uploadedBy);
    @Query("SELECT r.id FROM Resume r WHERE r.uploadedBy = :uploadedBy")
    List<Long> findIdsByUploadedBy(@Param("uploadedBy") String uploadedBy);
}
