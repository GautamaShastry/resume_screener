"""
Investigator Agent - Researches company information, tech stack, and engineering culture.
Runs in parallel with other agents after job parsing.
"""

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from graph.state import AgentState
from tools.web_scraper import web_scraper
from tools.cache import cache, company_cache_key
from config import config


def investigator_agent(state: AgentState) -> AgentState:
    """
    Agent that researches company information for interview preparation.
    Searches for engineering blogs, tech stack, and recent news.
    """
    try:
        company_name = state.get('company_name') or state.get('job_title', '').split(' at ')[-1]
        
        if not company_name or company_name == state.get('job_title'):
            # Try to extract from job description
            job_desc = state.get('job_description', '')
            company_name = _extract_company_name(job_desc)
        
        # Check cache first for company intel
        cache_key = company_cache_key(company_name)
        cached_intel = cache.get(cache_key)
        if cached_intel:
            print(f"🎯 Company Intel Cache HIT: {company_name}")
            state['company_intel'] = cached_intel
            state['messages'].append(f"✅ Company intel loaded from cache for {company_name}")
            return state
        
        print(f"❌ Company Intel Cache MISS: {company_name}")
        search_results = web_scraper.search_company_info(company_name)
        
        # Extract tech from engineering blog if found, using job skills as keywords
        job_skills = state.get('job_skills', [])
        tech_found = []
        for blog in search_results.get('engineering_blog', []):
            if blog.get('url') and 'error' not in blog:
                tech = web_scraper.extract_tech_from_url(blog['url'], job_keywords=job_skills)
                tech_found.extend(tech)
        
        # Use LLM to synthesize company intel
        llm = ChatOpenAI(model=config.MODEL_NAME, temperature=config.TEMPERATURE)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a company research analyst helping candidates prepare for interviews.
            Analyze the search results and provide actionable intelligence."""),
            ("human", """Company: {company_name}

Search Results:
Engineering Blog: {eng_blog}
Tech Stack Info: {tech_info}
Technologies Found: {tech_found}

Job Skills Required: {job_skills}
Candidate Skills: {resume_skills}

Provide company intelligence in this format:
RECENT_TECH: List 3-5 specific technologies they use or recently adopted
TALKING_POINTS: List 3 specific things candidate should mention in interview
CULTURE_NOTES: 1-2 sentences about engineering culture if found""")
        ])
        
        response = llm.invoke(prompt.format(
            company_name=company_name,
            eng_blog=str(search_results.get('engineering_blog', []))[:500],
            tech_info=str(search_results.get('tech_stack', []))[:500],
            tech_found=', '.join(list(set(tech_found))[:10]),
            job_skills=', '.join(state.get('job_skills', [])[:10]),
            resume_skills=', '.join(state.get('resume_skills', [])[:10])
        ))
        
        # Parse response
        content = response.content
        company_intel = {
            "company_name": company_name,
            "recent_tech": _parse_section(content, "RECENT_TECH"),
            "talking_points": _parse_section(content, "TALKING_POINTS"),
            "culture_notes": _parse_section(content, "CULTURE_NOTES"),
            "raw_search_results": search_results
        }
        
        state['company_intel'] = company_intel
        
        # Cache company intel for 24 hours (company info doesn't change often)
        cache.set(cache_key, company_intel, ttl=86400)
        
        state['messages'].append(f"✅ Company intel gathered for {company_name}")
        
    except Exception as e:
        state['company_intel'] = {
            "company_name": company_name if 'company_name' in dir() else "Unknown",
            "recent_tech": [],
            "talking_points": ["Research the company website before interview"],
            "culture_notes": "Unable to gather company intel",
            "error": str(e)
        }
        state['messages'].append(f"⚠️ Investigator error: {str(e)}")
    
    return state


def _extract_company_name(text: str) -> str:
    """Extract company name from job description text."""
    # Common patterns
    import re
    patterns = [
        r'(?:at|@)\s+([A-Z][A-Za-z0-9\s&]+?)(?:\s+is|\s+we|\.|,)',
        r'([A-Z][A-Za-z0-9]+)\s+is\s+(?:looking|hiring|seeking)',
        r'About\s+([A-Z][A-Za-z0-9\s&]+?)(?:\n|:)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    
    return ""


def _parse_section(content: str, section: str) -> list:
    """Parse a section from LLM response."""
    lines = []
    in_section = False
    
    for line in content.split('\n'):
        if section in line.upper():
            in_section = True
            continue
        if in_section:
            if any(s in line.upper() for s in ['RECENT_TECH', 'TALKING_POINTS', 'CULTURE_NOTES'] if s != section):
                break
            cleaned = line.strip().lstrip('- •*').strip()
            if cleaned:
                lines.append(cleaned)
    
    return lines[:5]
