"""
Investigator Agent - Researches company information, tech stack, and recent news
"""
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from graph.state import AgentState
from tools.web_scraper import web_scraper
from config import config


def investigator_agent(state: AgentState) -> AgentState:
    """
    Agent that researches company information to provide intel for interviews.
    Finds: engineering blog posts, tech stack, recent news, culture insights.
    """
    try:
        company_name = state.get("company_name", "")
        job_title = state.get("job_title", "")
        job_description = state.get("job_description", "")

        # Initialize company intel
        company_intel = {
            "company_name": company_name,
            "tech_stack": [],
            "blog_posts": [],
            "talking_points": [],
            "culture_insights": "",
        }

        # Step 1: Get company info from web scraper
        if company_name:
            scraped_info = web_scraper.search_company_info(company_name)
            company_intel["tech_stack"] = scraped_info.get("tech_stack", [])
            company_intel["blog_posts"] = scraped_info.get("blog_posts", [])
            company_intel["engineering_blog_url"] = scraped_info.get(
                "engineering_blog_url", ""
            )

        # Step 2: Use LLM to generate talking points based on JD and company
        llm = ChatOpenAI(model=config.MODEL_NAME, temperature=0.5)

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a career research specialist. Analyze the company and job 
            to provide specific talking points for the interview."""),
            ("human", """Company: {company_name}
Job Title: {job_title}
Known Tech Stack: {tech_stack}
Job Description Summary: {job_desc}

Generate:
1. 3-5 specific talking points about the company's technology choices
2. How the candidate should position their experience for this company
3. Any cultural insights based on the job description

Format as:
TALKING_POINTS:
- point 1
- point 2
- point 3

POSITIONING:
- advice 1
- advice 2

CULTURE:
Brief culture insight based on JD tone and requirements.""")
        ])

        chain = prompt | llm

        response = chain.invoke({
            "company_name": company_name or "Unknown Company",
            "job_title": job_title,
            "tech_stack": ", ".join(company_intel["tech_stack"]) or "Not available",
            "job_desc": job_description[:2000],
        })

        # Parse response
        content = response.content
        talking_points = []
        positioning = []
        culture = ""

        if "TALKING_POINTS:" in content:
            tp_section = content.split("TALKING_POINTS:")[1]
            if "POSITIONING:" in tp_section:
                tp_section = tp_section.split("POSITIONING:")[0]
            talking_points = [
                line.strip().lstrip("- ")
                for line in tp_section.strip().split("\n")
                if line.strip() and line.strip() != "-"
            ]

        if "POSITIONING:" in content:
            pos_section = content.split("POSITIONING:")[1]
            if "CULTURE:" in pos_section:
                pos_section = pos_section.split("CULTURE:")[0]
            positioning = [
                line.strip().lstrip("- ")
                for line in pos_section.strip().split("\n")
                if line.strip() and line.strip() != "-"
            ]

        if "CULTURE:" in content:
            culture = content.split("CULTURE:")[1].strip()

        company_intel["talking_points"] = talking_points[:5]
        company_intel["positioning"] = positioning[:3]
        company_intel["culture_insights"] = culture[:500]

        state["company_intel"] = company_intel
        state["messages"].append("✅ Company research completed")
        state["current_step"] = "investigated"

    except Exception as e:
        state["company_intel"] = {
            "company_name": state.get("company_name", ""),
            "tech_stack": [],
            "blog_posts": [],
            "talking_points": ["Research the company's engineering blog before interview"],
            "culture_insights": "Review the job description for culture cues",
            "error": str(e),
        }
        state["messages"].append(f"⚠️ Company research partial: {str(e)}")

    return state
