from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from graph.state import AgentState
from config import config

def career_advisor_agent(state: AgentState) -> AgentState:
    """
    Agent responsible for providing career advice and improvement suggestions
    """
    try:
        # If already combined with ATS optimizer, skip LLM call
        if config.COMBINE_ADVICE_CALLS and state.get('career_advice'):
            # Career advice already populated by ATS optimizer
            pass
        else:
            llm = ChatOpenAI(model=config.MODEL_NAME, temperature=0.5)
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a professional career advisor. Provide personalized, actionable career development advice."""),
                ("human", """Based on this analysis, provide career development advice:
                
Job Title: {job_title}
Match Score: {match_score}%
Strengths: {strengths}
Areas for Improvement: {weaknesses}

Provide 5 specific career development recommendations as a simple list.""")
            ])
            
            chain = prompt | llm
            
            response = chain.invoke({
                "job_title": state.get('job_title', 'the position'),
                "match_score": state['match_score'],
                "strengths": ", ".join(state['strengths'][:5]),
                "weaknesses": ", ".join(state['weaknesses'][:5]),
            })
            
            # Parse recommendations
            lines = [line.strip().lstrip("- ").lstrip("•").strip() for line in response.content.split("\n") if line.strip()]
            state['career_advice'] = [l for l in lines if len(l) > 10][:7]
        
        # Generate improvement suggestions based on score
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
        if not state.get('career_advice'):
            state['career_advice'] = [
                "Continue developing your technical skills",
                "Build projects showcasing missing skills",
                "Network with professionals in your target role",
                "Keep your resume updated with recent achievements"
            ]
        state['improvement_suggestions'] = []
        state['messages'].append(f"⚠️ Using default career advice: {str(e)}")
    
    return state