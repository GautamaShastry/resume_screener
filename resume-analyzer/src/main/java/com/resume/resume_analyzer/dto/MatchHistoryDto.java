package com.resume.resume_analyzer.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class MatchHistoryDto {
    private Long matchResultId;
    private Long resumeId;
    private String resumeFileName;
    private Long jobDescriptionId;
    private String jobTitle;
    private String jobDescriptionPreview;
    private Double matchScore;
    private LocalDateTime matchTime;
    private String analysisId;
    private boolean hasReports;
}