"""
Interview Prep Agent - Generates likely interview questions based on JD and resume gaps
"""
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from graph.state import AgentState
from config import config


def interview_prep_agent(state: AgentState) -> AgentState:
    """
    Agent that generates likely interview questions based on:
    - Job requirements
    - Resume gaps (missing skills)
    - Company tech stack
    """
    try:
        job_title = state.get("job_title", "Software Engineer")
        job_skills = state.get("job_skills", [])
        missing_skills = state.get("missing_skills", [])
        matched_skills = state.get("matched_skills", [])
        company_intel = state.get("company_intel", {})
        tech_stack = company_intel.get("tech_stack", [])

        llm = ChatOpenAI(model=config.MODEL_NAME, temperature=0.5)

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a technical interview coach. Generate specific, 
            likely interview questions based on the job requirements and candidate profile.
            Focus on questions that test the required skills."""),
            ("human", """Job Title: {job_title}
Required Skills: {job_skills}
Candidate's Strong Skills: {matched_skills}
Candidate's Gaps: {missing_skills}
Company Tech Stack: {tech_stack}

Generate exactly 5 technical interview questions they will likely ask.
For each question provide:
1. The question itself
2. Why they'll ask it (based on JD)
3. A tip for answering

Format EXACTLY as:
Q1: [Question]
WHY: [Reason based on JD]
TIP: [How to answer]

Q2: [on]
TIP: : [ReasWHYQuestion]
