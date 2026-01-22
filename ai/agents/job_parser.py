"""
Job Parser Agent - Hybrid approach:
- NLP for fast skill extraction (from known database)
- LLM for accurate job title extraction (single fast call)
- Redis caching for repeated JD parsing
"""
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from typing import List
import re

from graph.state import AgentState
from tools.nlp_tools import extract_skills
from tools.cache import cache, hash_content, jd_parse_cache_key
from config import config


def extract_job_title_with_llm(job_description: str) -> dict:
    """Use LLM to extract job title, position type, and experience - with caching."""
    # Check cache first
    jd_hash = hash_content(job_description[:2000])
    cache_key = jd_parse_cache_key(jd_hash)
    
    cached_result = cache.get(cache_key)
    if cached_result:
        print(f"🎯 JD Parse Cache HIT")
        return cached_result
    
    print(f"❌ JD Parse Cache MISS - calling LLM")
    
    try:
        llm = ChatOpenAI(model=config.MODEL_NAME, temperature=0.1)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Extract job information from this job description.
Reply in EXACTLY this format (no other text):
TITLE: [exact job title like "Software Engineer", "Data Scientist", etc.]
POSITION_TYPE: [Full-time, Part-time, Contract, Internship, or Not specified]
EXPERIENCE: [years required like "5+ years" or "Entry Level" or "Not specified"]"""),
            ("human", "{job_description}")
        ])
        
        response = llm.invoke(prompt.format(job_description=job_description[:2000]))
        content = response.content
        
        # Parse response
        title = "Software Engineer"
        position_type = "Full-time"
        experience = "Not specified"
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('TITLE:'):
                title = line.replace('TITLE:', '').strip()
            elif line.startswith('POSITION_TYPE:'):
                position_type = line.replace('POSITION_TYPE:', '').strip()
            elif line.startswith('EXPERIENCE:'):
                experience = line.replace('EXPERIENCE:', '').strip()
        
        result = {"title": title, "position_type": position_type, "experience": experience}
        
        # Cache for 24 hours (same JD = same result)
        cache.set(cache_key, result, ttl=86400)
        
        return result
    except Exception as e:
        print(f"LLM extraction failed: {e}")
        return {"title": None, "position_type": None, "experience": None}


def extract_job_title_nlp(text: str) -> str:
    """Fallback: Extract job title using regex patterns."""
    text_lower = text.lower()
    
    # Pattern 1: Team/department context
    team_patterns = [
        (r'recommendation.*(?:infra|infrastructure)', 'Software Engineer - Recommendation Infrastructure'),
        (r'e-?commerce.*recommendation', 'E-commerce Software Engineer'),
        (r'machine learning.*(?:infra|infrastructure)', 'ML Infrastructure Engineer'),
        (r'data.*(?:infra|infrastructure|platform)', 'Data Platform Engineer'),
        (r'backend.*team', 'Backend Engineer'),
        (r'frontend.*team', 'Frontend Engineer'),
        (r'platform.*team', 'Platform Engineer'),
        (r'mobile.*team', 'Mobile Engineer'),
    ]
    
    for pattern, role in team_patterns:
        if re.search(pattern, text_lower):
            return role
    
    # Pattern 2: Common job titles
    job_titles = [
        "Staff Software Engineer", "Senior Software Engineer", "Software Engineer",
        "Machine Learning Engineer", "ML Engineer", "Data Scientist", "Data Engineer",
        "Backend Engineer", "Frontend Engineer", "Full Stack Engineer",
        "DevOps Engineer", "Platform Engineer", "Cloud Engineer",
        "iOS Engineer", "Android Engineer", "Mobile Engineer",
    ]
    
    for title in job_titles:
        if title.lower() in text_lower:
            return title
    
    return "Software Engineer"


def extract_position_type_nlp(text: str) -> str:
    """Extract position type using regex."""
    text_lower = text.lower()
    
    if re.search(r'\bintern(ship)?\b', text_lower):
        return "Internship"
    if re.search(r'\bcontract\b|\bcontractor\b', text_lower):
        return "Contract"
    if re.search(r'\bpart[- ]?time\b', text_lower):
        return "Part-time"
    if re.search(r'\bfull[- ]?time\b', text_lower):
        return "Full-time"
    if re.search(r'\bfreelance\b', text_lower):
        return "Freelance"
    
    # Default to Full-time for most job postings
    return "Full-time"


def extract_experience_nlp(text: str) -> str:
    """Extract years of experience using regex."""
    patterns = [
        r'(\d+)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:experience|exp)',
        r'(?:minimum|at least)\s+(\d+)\s*(?:years?|yrs?)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return f"{match.group(1)}+ years"
    
    if re.search(r'recent graduate|entry.level|new grad', text, re.IGNORECASE):
        return "Entry Level / New Grad"
    
    return "Not specified"


def job_parser_agent(state: AgentState) -> AgentState:
    """
    Hybrid job parser:
    1. Extract skills using NLP (fast, from known database)
    2. Extract job title, position type, experience using LLM (accurate, single call)
    """
    try:
        job_description = state['job_description']
        
        # Step 1: Extract skills using NLP (fast)
        skills = extract_skills(job_description)
        state['job_skills'] = skills
        
        # Step 2: Extract job info using LLM (hybrid approach)
        llm_result = extract_job_title_with_llm(job_description)
        
        if llm_result["title"]:
            state['job_title'] = llm_result["title"]
            state['position_type'] = llm_result.get("position_type") or extract_position_type_nlp(job_description)
            state['job_experience_required'] = llm_result.get("experience") or extract_experience_nlp(job_description)
        else:
            # Fallback to NLP extraction
            state['job_title'] = extract_job_title_nlp(job_description)
            state['position_type'] = extract_position_type_nlp(job_description)
            state['job_experience_required'] = extract_experience_nlp(job_description)
        
        state['job_requirements'] = []
        
        print(f"DEBUG job_parser: title='{state['job_title']}', type='{state['position_type']}', exp='{state['job_experience_required']}', skills={len(skills)}")
        state['messages'].append("✅ Job description parsed successfully")
        state['current_step'] = "job_parsed"
        
    except Exception as e:
        state['job_title'] = "Software Engineer"
        state['position_type'] = "Full-time"
        state['job_skills'] = []
        state['job_requirements'] = []
        state['job_experience_required'] = "Not specified"
        state['error'] = f"Job parsing failed: {str(e)}"
        state['messages'].append(f"❌ Job parsing error: {str(e)}")
    
    return state
