"""
Shared state for all agents in the LangGraph workflow.
"""

from typing import TypedDict, List, Dict, Optional, Annotated, Any
import operator


class AgentState(TypedDict):
    """State shared across all agents in the workflow"""
    
    # Input data
    resume_file: Optional[bytes]
    resume_filename: str
    job_description: str
    job_url: Optional[str]
    company_name: Optional[str]
    
    # Parsed resume data
    resume_text: str
    resume_sections: Dict[str, str]
    resume_skills: List[str]
    resume_experience: List[Dict]
    resume_education: List[Dict]
    
    # Parsed job data
    job_title: str
    position_type: str  # Full-time, Part-time, Contract, Internship
    job_requirements: List[str]
    job_skills: List[str]
    job_experience_required: str
    
    # Match analysis results
    match_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    strengths: List[str]
    weaknesses: List[str]
    
    # Original recommendations
    ats_recommendations: List[str]
    career_advice: List[str]
    improvement_suggestions: List[str]
    
    # NEW: Enhanced features
    company_intel: Dict[str, Any]  # Company research results
    interview_questions: List[Dict[str, str]]  # Likely interview Qs
    tailored_resume_suggestions: List[Dict[str, str]]  # Specific resume edits
    
    # Reports
    pdf_report: Optional[bytes]
    html_report: Optional[str]
    
    # Metadata
    messages: Annotated[List[str], operator.add]
    current_step: str
    error: Optional[str]
