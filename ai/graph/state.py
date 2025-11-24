from typing import TypedDict, List, Dict, Optional, Annotated
import operator

class AgentState(TypedDict):
    """State shared across all agents in the workflow"""
    
    # Input data
    resume_file: Optional[bytes]
    resume_filename: str
    job_description: str
    
    # Parsed data
    resume_text: str
    resume_sections: Dict[str, str]
    resume_skills: List[str]
    resume_experience: List[Dict]
    resume_education: List[Dict]
    
    job_title: str
    job_requirements: List[str]
    job_skills: List[str]
    job_experience_required: str
    
    # Analysis results
    match_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    strengths: List[str]
    weaknesses: List[str]
    
    # Report generation
    pdf_report: Optional[bytes]
    html_report: Optional[str]
    
    # Recommendations
    ats_recommendations: List[str]
    career_advice: List[str]
    improvement_suggestions: List[str]
    
    # Metadata
    messages: Annotated[List[str], operator.add]
    current_step: str
    error: Optional[str]