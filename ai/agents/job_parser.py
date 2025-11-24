from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List

from graph.state import AgentState
from tools.nlp_tools import extract_skills, extract_keywords
from config import config

class JobParserOutput(BaseModel):
    job_title: str = Field(description="The job title")
    required_skills: List[str] = Field(description="List of required technical skills")
    required_experience: str = Field(description="Required years of experience")
    key_requirements: List[str] = Field(description="Key job requirements")
    nice_to_have: List[str] = Field(description="Nice-to-have qualifications")

def job_parser_agent(state: AgentState) -> AgentState:
    """
    Agent responsible for parsing and extracting requirements from job description
    """
    try:
        job_description = state['job_description']
        
        # Step 1: Extract skills using NLP
        skills = extract_skills(job_description)
        
        # Step 2: Use LLM for enhanced parsing
        llm = ChatOpenAI(model=config.MODEL_NAME, temperature=config.TEMPERATURE)
        
        parser = PydanticOutputParser(pydantic_object=JobParserOutput)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert at analyzing job descriptions and extracting key requirements."),
            ("human", """Analyze the following job description and extract:
            1. The job title
            2. All required technical skills
            3. Required years of experience
            4. Key requirements and responsibilities
            5. Nice-to-have qualifications
            
            Job Description:
            {job_description}
            
            {format_instructions}
            """)
        ])
        
        chain = prompt | llm | parser
        
        try:
            result = chain.invoke({
                "job_description": job_description[:4000],  # Limit token count
                "format_instructions": parser.get_format_instructions()
            })
            
            # Combine NLP-extracted skills with LLM-extracted skills
            all_skills = list(set(skills + result.required_skills))
            
            state['job_title'] = result.job_title
            state['job_skills'] = all_skills
            state['job_requirements'] = result.key_requirements
            state['job_experience_required'] = result.required_experience
            
        except Exception as e:
            # Fallback to NLP-only extraction
            state['job_skills'] = skills
            state['job_requirements'] = []
            state['job_experience_required'] = "Not specified"
        
        state['messages'].append("✅ Job description parsed successfully")
        state['current_step'] = "job_parsed"
        
    except Exception as e:
        state['error'] = f"Job description parsing failed: {str(e)}"
        state['messages'].append(f"❌ Job parsing error: {str(e)}")
    
    return state