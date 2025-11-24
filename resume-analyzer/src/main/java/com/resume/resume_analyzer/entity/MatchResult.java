package com.resume.resume_analyzer.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;
import java.util.Date;

@Entity
@Data
@AllArgsConstructor
@NoArgsConstructor
public class MatchResult {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private Long resumeId;

    private Long jobDescriptionId;

    private Double matchScore;

    @Column(length = 5000)
    private String extractedSkills;

    @Column(length = 5000)
    private String strengths;

    @Column(length = 5000)
    private String weaknesses;

    private LocalDateTime matchTime;

    private String analysisId;
}

