package com.resume.resume_analyzer.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class JobDescriptionDto {
    private String title;
    private String description;
    private String uploadedBy;   // comes from authenticated user
}
