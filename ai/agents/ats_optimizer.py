from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from typing import List

from graph.state import AgentState
from config import config

def ats_optimizer_agent(state: AgentState) -> AgentState:
    """
    Agent responsible for providing ATS optimization recommendations
    """
    try:
        llm = ChatOpenAI(model=config.MODEL_NAME, temperature=config.TEMPERATURE)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert ATS (Applicant Tracking System) consultant. 
            Provide specific, actionable recommendations to optimize resumes for ATS systems."""),
            ("human", """Analyze this resume-job match and provide ATS optimization recommendations:
            
            Match Score: {match_score}%
            Matched Skills: {matched_skills}
            Missing Skills: {missing_skills}
            
            Resume Sections Available:
            {resume_sections}
            
            Job Requirements:
            {job_requirements}
            
            Provide 5-7 specific ATS optimization recommendations in a Python list format.
            Focus on:
            1. Keyword optimization
            2. Formatting improvements
            3. Section enhancements
            4. Missing keywords to add
            5. ATS-friendly formatting tips
            
            Return ONLY a Python list of strings, e.g.:
            ["Add keywords: Python, Docker to skills section", "Include years of experience in job titles"]
            """)
        ])
        
        chain = prompt | llm
        
        response = chain.invoke({
            "match_score": state['match_score'],
            "matched_skills": ", ".join(state['matched_skills'][:10]),
            "missing_skills": ", ".join(state['missing_skills'][:10]),
            "resume_sections": ", ".join(state['resume_sections'].keys()),
            "job_requirements": ", ".join(state.get('job_requirements', [])[:5])
        })
        
        # Parse the response
        recommendations = eval(response.content) if isinstance(response.content, str) else []
        
        state['ats_recommendations'] = recommendations
        state['messages'].append("✅ ATS optimization recommendations generated")
        state['current_step'] = "ats_optimized"
        
    except Exception as e:
        state['ats_recommendations'] = [
            "Ensure keywords from job description are present in your resume",
            "Use standard section headers (Experience, Education, Skills)",
            "Include measurable achievements with numbers",
            "Match job title keywords in your experience section",
            "Use industry-standard terminology"
        ]
        state['messages'].append(f"⚠️ Using default ATS recommendations: {str(e)}")
    
    return state