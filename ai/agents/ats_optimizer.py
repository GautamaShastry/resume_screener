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
        # If combining with career advisor, do both in one call
        if config.COMBINE_ADVICE_CALLS:
            llm = ChatOpenAI(model=config.MODEL_NAME, temperature=config.TEMPERATURE)
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert career consultant and ATS specialist. 
                Provide specific, actionable recommendations."""),
                ("human", """Analyze this resume-job match:
                
Match Score: {match_score}%
Matched Skills: {matched_skills}
Missing Skills: {missing_skills}
Job Title: {job_title}

Provide your response in this EXACT format:
ATS_RECOMMENDATIONS:
- recommendation 1
- recommendation 2
- recommendation 3
- recommendation 4
- recommendation 5

CAREER_ADVICE:
- advice 1
- advice 2
- advice 3
- advice 4
- advice 5

Focus on actionable, specific suggestions.""")
            ])
            
            chain = prompt | llm
            
            response = chain.invoke({
                "match_score": state['match_score'],
                "matched_skills": ", ".join(state['matched_skills'][:10]),
                "missing_skills": ", ".join(state['missing_skills'][:10]),
                "job_title": state.get('job_title', 'the position')
            })
            
            # Parse the combined response
            content = response.content
            ats_recs = []
            career_advice = []
            
            if "ATS_RECOMMENDATIONS:" in content:
                ats_section = content.split("ATS_RECOMMENDATIONS:")[1]
                if "CAREER_ADVICE:" in ats_section:
                    ats_section = ats_section.split("CAREER_ADVICE:")[0]
                ats_recs = [line.strip().lstrip("- ") for line in ats_section.strip().split("\n") if line.strip() and line.strip() != "-"]
            
            if "CAREER_ADVICE:" in content:
                career_section = content.split("CAREER_ADVICE:")[1]
                career_advice = [line.strip().lstrip("- ") for line in career_section.strip().split("\n") if line.strip() and line.strip() != "-"]
            
            state['ats_recommendations'] = ats_recs[:7] if ats_recs else get_default_ats_recommendations()
            state['career_advice'] = career_advice[:7] if career_advice else get_default_career_advice()
            
        else:
            # Original separate call
            llm = ChatOpenAI(model=config.MODEL_NAME, temperature=config.TEMPERATURE)
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert ATS (Applicant Tracking System) consultant. 
                Provide specific, actionable recommendations to optimize resumes for ATS systems."""),
                ("human", """Analyze this resume-job match and provide ATS optimization recommendations:
                
                Match Score: {match_score}%
                Matched Skills: {matched_skills}
                Missing Skills: {missing_skills}
                
                Provide 5-7 specific ATS optimization recommendations as a simple list.
                """)
            ])
            
            chain = prompt | llm
            
            response = chain.invoke({
                "match_score": state['match_score'],
                "matched_skills": ", ".join(state['matched_skills'][:10]),
                "missing_skills": ", ".join(state['missing_skills'][:10]),
            })
            
            # Parse recommendations from response
            lines = [line.strip().lstrip("- ").lstrip("•").strip() for line in response.content.split("\n") if line.strip()]
            state['ats_recommendations'] = [l for l in lines if len(l) > 10][:7]
        
        state['messages'].append("✅ ATS optimization recommendations generated")
        state['current_step'] = "ats_optimized"
        
    except Exception as e:
        state['ats_recommendations'] = get_default_ats_recommendations()
        state['messages'].append(f"⚠️ Using default ATS recommendations: {str(e)}")
    
    return state


def get_default_ats_recommendations():
    return [
        "Ensure keywords from job description are present in your resume",
        "Use standard section headers (Experience, Education, Skills)",
        "Include measurable achievements with numbers",
        "Match job title keywords in your experience section",
        "Use industry-standard terminology"
    ]


def get_default_career_advice():
    return [
        "Continue developing your technical skills",
        "Build projects showcasing missing skills",
        "Network with professionals in your target role",
        "Keep your resume updated with recent achievements"
    ]