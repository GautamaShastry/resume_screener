from graph.state import AgentState
from tools.matching_tools import matching_tools
from config import config

def matcher_agent(state: AgentState) -> AgentState:
    """
    Agent responsible for matching resume against job requirements
    """
    try:
        resume_text = state['resume_text']
        job_description = state['job_description']
        resume_skills = state['resume_skills']
        job_skills = state['job_skills']
        
        # Step 1: Calculate overall similarity
        overall_similarity = matching_tools.calculate_similarity(resume_text, job_description)
        
        # Step 2: Calculate skill-based matching
        matched_skills, missing_skills, skill_match_percentage = matching_tools.calculate_skill_match(
            resume_skills, job_skills
        )
        
        # Step 3: Calculate weighted match score
        # 60% weight on overall similarity, 40% on skill matching
        final_score = (overall_similarity * 0.6) + (skill_match_percentage * 0.4)
        
        # Step 4: Identify strengths and weaknesses
        strengths = matching_tools.find_strengths(resume_skills, job_skills)
        weaknesses = matching_tools.find_weaknesses(resume_skills, job_skills)
        
        # Update state
        state['match_score'] = round(final_score, 2)
        state['matched_skills'] = matched_skills
        state['missing_skills'] = missing_skills
        state['strengths'] = strengths
        state['weaknesses'] = weaknesses
        
        state['messages'].append(f"✅ Match analysis complete: {state['match_score']}% match")
        state['current_step'] = "matched"
        
    except Exception as e:
        state['error'] = f"Matching failed: {str(e)}"
        state['messages'].append(f"❌ Matching error: {str(e)}")
    
    return state