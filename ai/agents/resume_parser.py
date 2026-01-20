from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Dict
import json

from graph.state import AgentState
from tools.text_extraction import extract_text_from_file
from tools.nlp_tools import extract_skills, extract_sections, extract_experience, extract_education
from config import config

class ResumeParserOutput(BaseModel):
    skills: List[str] = Field(description="List of technical skills found in resume")
    summary: str = Field(description="Professional summary or objective")
    key_highlights: List[str] = Field(description="Key achievements and highlights")

def resume_parser_agent(state: AgentState) -> AgentState:
    """
    Agent responsible for parsing and extracting structured information from resume
    """
    try:
        # Step 1: Extract text from file
        resume_text = extract_text_from_file(state['resume_file'], state['resume_filename'])
        state['resume_text'] = resume_text
        
        # Step 2: Extract sections
        sections = extract_sections(resume_text)
        state['resume_sections'] = sections
        
        # Step 3: Extract skills using NLP
        skills = extract_skills(resume_text)
        
        # Step 4: Extract experience and education
        experience = extract_experience(sections.get('experience', ''))
        education = extract_education(sections.get('education', ''))
        
        # Step 5: Use LLM for enhanced parsing (only if not skipping)
        if not config.SKIP_LLM_PARSING:
            llm = ChatOpenAI(model=config.MODEL_NAME, temperature=config.TEMPERATURE)
            
            parser = PydanticOutputParser(pydantic_object=ResumeParserOutput)
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert resume parser. Extract structured information from the resume.
                
IMPORTANT: For technical skills, ONLY extract:
- Programming languages (Python, Java, JavaScript, etc.)
- Frameworks & libraries (React, Django, Spring Boot, etc.)
- Databases (MySQL, MongoDB, PostgreSQL, etc.)
- Cloud platforms (AWS, Azure, GCP, etc.)
- DevOps tools (Docker, Kubernetes, Jenkins, etc.)
- Other technical tools (Git, Jira, etc.)

DO NOT include soft skills (communication, teamwork, patience, leadership) or generic terms (experience, knowledge, ability) or platform names (Udemy, Coursera, LinkedIn)."""),
                ("human", """Parse the following resume and extract:
                1. All TECHNICAL skills only (programming languages, frameworks, tools, databases, cloud platforms)
                2. A concise professional summary
                3. Key achievements and highlights
                
                Resume:
                {resume_text}
                
                {format_instructions}
                """)
            ])
            
            chain = prompt | llm | parser
            
            try:
                result = chain.invoke({
                    "resume_text": resume_text[:4000],  # Limit token count
                    "format_instructions": parser.get_format_instructions()
                })
                
                # Combine NLP-extracted skills with LLM-extracted skills
                all_skills = list(set(skills + result.skills))
                state['resume_skills'] = all_skills
                
            except Exception as e:
                # Fallback to NLP-only extraction
                state['resume_skills'] = skills
        else:
            # Fast path: NLP-only extraction
            state['resume_skills'] = skills
        
        state['resume_experience'] = experience
        state['resume_education'] = education
        
        state['messages'].append("✅ Resume parsed successfully")
        state['current_step'] = "resume_parsed"
        
    except Exception as e:
        state['error'] = f"Resume parsing failed: {str(e)}"
        state['messages'].append(f"❌ Resume parsing error: {str(e)}")
    
    return state