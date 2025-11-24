package com.resume.resume_analyzer.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class UserProfileDto {
    private String name;
    private String email;
    private Integer resumeCount;
    private Integer jobDescriptionCount;
    private Integer matchCount;
}