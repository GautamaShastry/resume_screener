from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from graph.state import AgentState
from config import config

def career_advisor_agent(state: AgentState) -> AgentState:
    """
    Agent responsible for providing career advice and improvement suggestions
    """
    try:
        llm = ChatOpenAI(model=config.MODEL_NAME, temperature=0.7)  # Higher temperature for creative advice
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a professional career advisor with expertise in tech careers. 
            Provide personalized, actionable career development advice."""),
            ("human", """Based on this analysis, provide career development advice:
            
            Job Title: {job_title}
            Match Score: {match_score}%
            Candidate's Strengths: {strengths}
            Areas for Improvement: {weaknesses}
            Experience: {experience_count} roles
            
            Provide 5-7 specific career development recommendations in a Python list format.
            Focus on:
            1. Skills to develop based on gaps
            2. Certifications or courses to pursue
            3. Experience to gain
            4. Networking opportunities
            5. Career progression path
            
            Return ONLY a Python list of strings.
            """)
        ])
        
        chain = prompt | llm
        
        response = chain.invoke({
            "job_title": state.get('job_title', 'the position'),
            "match_score": state['match_score'],
            "strengths": ", ".join(state['strengths'][:5]),
            "weaknesses": ", ".join(state['weaknesses'][:5]),
            "experience_count": len(state.get('resume_experience', []))
        })
        
        # Parse the response
        advice = eval(response.content) if isinstance(response.content, str) else []
        
        state['career_advice'] = advice
        
        # Generate improvement suggestions
        improvement_suggestions = []
        
        if state['match_score'] < config.MIN_MATCH_SCORE:
            improvement_suggestions.append("Consider gaining experience in missing technical skills")
            improvement_suggestions.append("Take online courses or certifications in required areas")
        
        if state['missing_skills']:
            top_missing = state['missing_skills'][:3]
            improvement_suggestions.append(f"Priority skills to learn: {', '.join(top_missing)}")
        
        if state['match_score'] >= config.HIGH_MATCH_SCORE:
            improvement_suggestions.append("You're a strong candidate! Focus on interview preparation")
        
        state['improvement_suggestions'] = improvement_suggestions
        state['messages'].append("✅ Career advice generated")
        state['current_step'] = "complete"
        
    except Exception as e:
        state['career_advice'] = [
            "Continue developing your technical skills",
            "Build projects showcasing missing skills",
            "Network with professionals in your target role",
            "Keep your resume updated with recent achievements"
        ]
        state['improvement_suggestions'] = []
        state['messages'].append(f"⚠️ Using default career advice: {str(e)}")
    
    return state