from sentence_transformers import SentenceTransformer, util
import torch
from typing import List, Tuple

class MatchingTools:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts"""
        embedding1 = self.model.encode(text1, convert_to_tensor=True)
        embedding2 = self.model.encode(text2, convert_to_tensor=True)
        similarity = util.cos_sim(embedding1, embedding2).item()
        return round(similarity * 100, 2)
    
    def calculate_skill_match(self, resume_skills: List[str], job_skills: List[str]) -> Tuple[List[str], List[str], float]:
        """Calculate skill matching"""
        resume_skills_set = set(s.lower() for s in resume_skills)
        job_skills_set = set(s.lower() for s in job_skills)
        
        matched = list(resume_skills_set.intersection(job_skills_set))
        missing = list(job_skills_set.difference(resume_skills_set))
        
        if not job_skills_set:
            match_percentage = 0.0
        else:
            match_percentage = (len(matched) / len(job_skills_set)) * 100
        
        return matched, missing, round(match_percentage, 2)
    
    def find_strengths(self, resume_skills: List[str], job_skills: List[str]) -> List[str]:
        """Identify key strengths"""
        resume_skills_set = set(s.lower() for s in resume_skills)
        job_skills_set = set(s.lower() for s in job_skills)
        
        strengths = resume_skills_set.intersection(job_skills_set)
        return list(strengths)[:10]  # Top 10 strengths
    
    def find_weaknesses(self, resume_skills: List[str], job_skills: List[str]) -> List[str]:
        """Identify areas for improvement"""
        resume_skills_set = set(s.lower() for s in resume_skills)
        job_skills_set = set(s.lower() for s in job_skills)
        
        weaknesses = job_skills_set.difference(resume_skills_set)
        return list(weaknesses)[:10]  # Top 10 weaknesses

matching_tools = MatchingTools()