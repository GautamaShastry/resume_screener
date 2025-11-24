from langgraph.graph import StateGraph, END
from graph.state import AgentState
from agents.resume_parser import resume_parser_agent
from agents.job_parser import job_parser_agent
from agents.matcher import matcher_agent
from agents.ats_optimizer import ats_optimizer_agent
from agents.career_advisor import career_advisor_agent
from agents.report_generator import report_generator_agent  # New import

def create_workflow():
    """Create the LangGraph workflow for resume analysis"""
    
    workflow = StateGraph(AgentState)
    
    # Add nodes (agents)
    workflow.add_node("resume_parser", resume_parser_agent)
    workflow.add_node("job_parser", job_parser_agent)
    workflow.add_node("matcher", matcher_agent)
    workflow.add_node("ats_optimizer", ats_optimizer_agent)
    workflow.add_node("career_advisor", career_advisor_agent)
    workflow.add_node("report_generator", report_generator_agent)  # New agent
    
    # Define the workflow edges
    workflow.set_entry_point("resume_parser")
    
    workflow.add_edge("resume_parser", "job_parser")
    workflow.add_edge("job_parser", "matcher")
    workflow.add_edge("matcher", "ats_optimizer")
    workflow.add_edge("ats_optimizer", "career_advisor")
    workflow.add_edge("career_advisor", "report_generator")  # New edge
    workflow.add_edge("report_generator", END)
    
    # Compile the graph
    app = workflow.compile()
    
    return app

# Create the workflow instance
resume_analyzer_graph = create_workflow()