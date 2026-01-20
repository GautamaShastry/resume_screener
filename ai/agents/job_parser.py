"""
Job Parser Agent - Extracts job title, skills, and requirements from job descriptions.
"""
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
import re

from graph.state import AgentState
from tools.nlp_tools import extract_skills
from config import config


class JobParserOutput(BaseModel):
    job_title: str = Field(description="The job title")
    required_skills: List[str] = Field(description="List of required technical skills")
    required_experience: str = Field(description="Required years of experience")
    key_requirements: List[str] = Field(description="Key job requirements")
    nice_to_have: List[str] = Field(description="Nice-to-have qualifications")


def extract_job_title(text: str) -> str:
    """Extract job title from job description using multiple strategies."""
    
    # Strategy 1: Look for explicit role patterns in the text
    role_patterns = [
        # "We are looking for talented individuals" type
        r'looking for (?:talented |experienced )?(.+?)(?:\s+to join|\s+in \d{4}|\s+who)',
        # "Position:" or "Role:" or "Job Title:"
        r'(?:Position|Role|Job Title|Title)\s*[:\-]\s*([^\n]+)',
        # "hiring a/an [title]"
        r'hiring (?:a |an )?([A-Z][a-zA-Z\s]+(?:Engineer|Developer|Scientist|Analyst|Manager|Lead|Architect))',
        # "join.*as a/an [title]"
        r'join.*?as (?:a |an )?([A-Z][a-zA-Z\s]+(?:Engineer|Developer|Scientist|Analyst|Manager|Lead))',
    ]
    
    for pattern in role_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            # Clean up
            title = re.sub(r'\s+', ' ', title)
            title = title.rstrip('.,;:')
            if 10 < len(title) < 80:
                return title
    
    # Strategy 2: Look for team/department context to infer role
    team_role_map = {
        r'recommendation.*(?:infra|infrastructure)': 'Software Engineer - Recommendation Infrastructure',
        r'e-?commerce.*recommendation': 'E-commerce Recommendation Engineer',
        r'machine learning.*(?:infra|infrastructure)': 'ML Infrastructure Engineer',
        r'data.*(?:infra|infrastructure|pipeline)': 'Data Infrastructure Engineer',
        r'backend.*team': 'Backend Engineer',
        r'frontend.*team': 'Frontend Engineer',
        r'platform.*team': 'Platform Engineer',
        r'mobile.*team': 'Mobile Engineer',
        r'ios.*team': 'iOS Engineer',
        r'android.*team': 'Android Engineer',
    }
    
    text_lower = text.lower()
    for pattern, role in team_role_map.items():
        if re.search(pattern, text_lower):
            return role
    
    # Strategy 3: Check responsibilities section for clues
    resp_patterns = [
        (r'build.*recommendation system', 'Recommendation Systems Engineer'),
        (r'build.*(?:large-scale|distributed).*system', 'Software Engineer'),
        (r'design.*(?:high performance|scalable).*system', 'Software Engineer'),
        (r'machine learning.*(?:model|algorithm)', 'Machine Learning Engineer'),
        (r'data pipeline', 'Data Engineer'),
        (r'(?:ios|swift|objective-c)', 'iOS Engineer'),
        (r'(?:android|kotlin)', 'Android Engineer'),
        (r'(?:react|vue|angular|frontend)', 'Frontend Engineer'),
    ]
    
    for pattern, role in resp_patterns:
        if re.search(pattern, text_lower):
            return role
    
    # Strategy 4: Look for common job titles anywhere in text
    common_titles = [
        "Staff Software Engineer", "Senior Software Engineer", "Software Engineer",
        "Machine Learning Engineer", "ML Engineer", "Data Scientist",
        "Data Engineer", "Backend Engineer", "Frontend Engineer",
        "Full Stack Engineer", "DevOps Engineer", "Site Reliability Engineer",
        "Platform Engineer", "Infrastructure Engineer", "Cloud Engineer",
        "iOS Engineer", "Android Engineer", "Mobile Engineer",
        "Security Engineer", "QA Engineer", "Solutions Architect",
    ]
    
    for title in common_titles:
        if title.lower() in text_lower:
            return title
    
    # Strategy 5: Check qualifications for programming languages to infer
    if re.search(r'c\+\+|java(?!script)', text_lower):
        return "Software Engineer"
    if re.search(r'python.*machine learning|ml|deep learning', text_lower):
        return "Machine Learning Engineer"
    
    return "Software Engineer"


def extract_experience_requirement(text: str) -> str:
    """Extract years of experience requirement from job description."""
    patterns = [
        r'(\d+)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:experience|exp)',
        r'(?:experience|exp)[:\s]+(\d+)\+?\s*(?:years?|yrs?)',
        r'(\d+)\s*(?:to|-)\s*(\d+)\s*(?:years?|yrs?)',
        r'(?:minimum|at least|min)\s+(\d+)\s*(?:years?|yrs?)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if match.lastindex and match.lastindex == 2:
                return f"{match.group(1)}-{match.group(2)} years"
            return f"{match.group(1)}+ years"
    
    # Check for "recent graduate" or "entry level"
    if re.search(r'recent graduate|entry.level|new grad|graduate.*\d{4}', text, re.IGNORECASE):
        return "Entry Level / New Grad"
    
    return "Not specified"


def job_parser_agent(state: AgentState) -> AgentState:
    """Agent responsible for parsing and extracting requirements from job description."""
    try:
        job_description = state['job_description']
        
        # Extract skills using NLP
        skills = extract_skills(job_description)
        
        if not config.SKIP_LLM_PARSING:
            # Use LLM for enhanced parsing
            llm = ChatOpenAI(model=config.MODEL_NAME, temperature=config.TEMPERATURE)
            parser = PydanticOutputParser(pydantic_object=JobParserOutput)
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an expert at analyzing job descriptions. Extract the job title and technical skills."),
                ("human", "Analyze this job description:\n{job_description}\n\n{format_instructions}")
            ])
            
            try:
                result = (prompt | llm | parser).invoke({
                    "job_description": job_description[:4000],
                    "format_instructions": parser.get_format_instructions()
                })
                
                state['job_title'] = result.job_title
                state['job_skills'] = list(set(skills + result.required_skills))
                state['job_requirements'] = result.key_requirements
                state['job_experience_required'] = result.required_experience
            except Exception:
                # Fallback to NLP extraction
                state['job_title'] = extract_job_title(job_description)
                state['job_skills'] = skills
                state['job_requirements'] = []
                state['job_experience_required'] = extract_experience_requirement(job_description)
        else:
            # Fast path: NLP-only extraction
            state['job_title'] = extract_job_title(job_description)
            state['job_skills'] = skills
            state['job_requirements'] = []
            state['job_experience_required'] = extract_experience_requirement(job_description)
        
        print(f"DEBUG job_parser: title='{state['job_title']}', skills={len(state['job_skills'])}")
        state['messages'].append("✅ Job description parsed successfully")
        state['current_step'] = "job_parsed"
        
    except Exception as e:
        state['error'] = f"Job description parsing failed: {str(e)}"
        state['messages'].append(f"❌ Job parsing error: {str(e)}")
    
    return state
