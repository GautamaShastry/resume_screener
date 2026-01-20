"""
Interview Prep Agent - Generates likely interview questions based on JD and resume gaps.
"""

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from graph.state import AgentState
from config import config


def interview_prep_agent(state: AgentState) -> AgentState:
    """
    Agent that generates likely interview questions and preparation tips.
    Based on job requirements, missing skills, and company context.
    """
    try:
        llm = ChatOpenAI(model=config.MODEL_NAME, temperature=0.5)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a senior technical interviewer. Generate realistic interview questions 
            that this candidate will likely face based on the job requirements and their background.
            Focus on areas where they need to demonstrate competence."""),
            ("human", """Job Title: {job_title}
Required Skills: {job_skills}
Candidate's Skills: {resume_skills}
Missing Skills: {missing_skills}
Match Score: {match_score}%

Company Tech (if known): {company_tech}

Generate 5 specific technical interview questions they will likely be asked.
For each question provide:
1. The question
2. Why they'll ask this (based on JD)
3. A tip for answering

Format:
Q1: [Question]
WHY: [Reason]
TIP: [Advice]

Q2: [Question]
WHY: [Reason]
TIP: [Advice]

... and so on for Q3, Q4, Q5""")
        ])
        
        company_intel = state.get('company_intel', {})
        company_tech = ', '.join(company_intel.get('recent_tech', []))
        
        response = llm.invoke(prompt.format(
            job_title=state.get('job_title', 'Software Engineer'),
            job_skills=', '.join(state.get('job_skills', [])[:15]),
            resume_skills=', '.join(state.get('resume_skills', [])[:15]),
            missing_skills=', '.join(state.get('missing_skills', [])[:10]),
            match_score=state.get('match_score', 0),
            company_tech=company_tech or 'Not available'
        ))
        
        # Parse questions
        questions = _parse_questions(response.content)
        state['interview_questions'] = questions
        state['messages'].append(f"✅ Generated {len(questions)} interview questions")
        
    except Exception as e:
        state['interview_questions'] = [
            {
                "question": "Tell me about a challenging project you worked on.",
                "why": "Standard behavioral question",
                "tip": "Use STAR method: Situation, Task, Action, Result"
            },
            {
                "question": "How do you approach debugging a complex issue?",
                "why": "Tests problem-solving skills",
                "tip": "Walk through your systematic approach"
            }
        ]
        state['messages'].append(f"⚠️ Interview prep error: {str(e)}")
    
    return state


def _parse_questions(content: str) -> list:
    """Parse interview questions from LLM response."""
    questions = []
    current_q = {}
    
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('Q') and ':' in line:
            if current_q.get('question'):
                questions.append(current_q)
            current_q = {"question": line.split(':', 1)[1].strip()}
        elif line.upper().startswith('WHY:'):
            current_q['why'] = line.split(':', 1)[1].strip()
        elif line.upper().startswith('TIP:'):
            current_q['tip'] = line.split(':', 1)[1].strip()
    
    if current_q.get('question'):
        questions.append(current_q)
    
    return questions[:5]
