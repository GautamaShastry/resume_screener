"""
Resume Coach Agent - Provides specific, tailored resume improvement suggestions.
"""

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from graph.state import AgentState
from config import config


def resume_coach_agent(state: AgentState) -> AgentState:
    """
    Agent that provides specific, actionable resume tailoring suggestions.
    Maps candidate experience to job requirements with specific edits.
    """
    try:
        llm = ChatOpenAI(model=config.MODEL_NAME, temperature=0.4)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert resume coach. Analyze the resume against the job description
            and provide SPECIFIC, ACTIONABLE suggestions to tailor the resume.
            Reference specific sections and suggest exact wording changes."""),
            ("human", """Job Title: {job_title}
Job Requirements: {job_requirements}
Required Skills: {job_skills}

Resume Text (excerpt):
{resume_text}

Candidate's Current Skills: {resume_skills}
Missing Skills: {missing_skills}
Match Score: {match_score}%

Company Tech Stack: {company_tech}

Provide 5 specific resume tailoring suggestions. For each:
1. Which section/bullet to modify
2. What to add or change
3. Why this helps

Format:
SUGGESTION 1:
SECTION: [e.g., "Experience bullet 2" or "Skills section"]
CHANGE: [Specific text to add/modify]
REASON: [Why this improves the match]

SUGGESTION 2:
...and so on""")
        ])
        
        company_intel = state.get('company_intel', {})
        company_tech = ', '.join(company_intel.get('recent_tech', []))
        
        response = llm.invoke(prompt.format(
            job_title=state.get('job_title', 'Position'),
            job_requirements=', '.join(state.get('job_requirements', [])[:5]),
            job_skills=', '.join(state.get('job_skills', [])[:15]),
            resume_text=state.get('resume_text', '')[:2000],
            resume_skills=', '.join(state.get('resume_skills', [])[:15]),
            missing_skills=', '.join(state.get('missing_skills', [])[:10]),
            match_score=state.get('match_score', 0),
            company_tech=company_tech or 'Not specified'
        ))
        
        # Parse suggestions
        suggestions = _parse_suggestions(response.content)
        state['tailored_resume_suggestions'] = suggestions
        state['messages'].append(f"✅ Generated {len(suggestions)} resume suggestions")
        
    except Exception as e:
        state['tailored_resume_suggestions'] = [
            {
                "section": "Skills Section",
                "change": f"Add missing skills: {', '.join(state.get('missing_skills', [])[:3])}",
                "reason": "These skills are explicitly mentioned in the job description"
            }
        ]
        state['messages'].append(f"⚠️ Resume coach error: {str(e)}")
    
    return state


def _parse_suggestions(content: str) -> list:
    """Parse resume suggestions from LLM response."""
    suggestions = []
    current = {}
    
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        if 'SUGGESTION' in line.upper() and ':' not in line[11:]:
            if current.get('section'):
                suggestions.append(current)
            current = {}
        elif line.upper().startswith('SECTION:'):
            current['section'] = line.split(':', 1)[1].strip()
        elif line.upper().startswith('CHANGE:'):
            current['change'] = line.split(':', 1)[1].strip()
        elif line.upper().startswith('REASON:'):
            current['reason'] = line.split(':', 1)[1].strip()
    
    if current.get('section'):
        suggestions.append(current)
    
    return suggestions[:5]
