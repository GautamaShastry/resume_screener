"""
Optimized LangGraph workflow for resume analysis.
Uses parallel execution and conditional features for low latency.

Architecture:
┌─────────────────────────────────────────────────────────────────┐
│                    PARALLEL PHASE 1                              │
│  ┌──────────────┐    ┌──────────────┐                           │
│  │Resume Parser │    │  Job Parser  │  (run simultaneously)     │
│  └──────────────┘    └──────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         MATCHER                                  │
│              (needs both resume + job data)                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PARALLEL PHASE 2                              │
│  ┌─────────────┐ ┌──────────────┐ ┌─────────────┐ ┌───────────┐│
│  │ATS+Career   │ │ Investigator │ │Interview    │ │Resume     ││
│  │Advisor      │ │ (if company) │ │Prep         │ │Coach      ││
│  └─────────────┘ └──────────────┘ └─────────────┘ └───────────┘│
│                  (all run simultaneously)                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    REPORT GENERATOR                              │
│                    (optional, skipped for speed)                 │
└─────────────────────────────────────────────────────────────────┘
"""

from langgraph.graph import StateGraph, END
from graph.state import AgentState
from agents.resume_parser import resume_parser_agent
from agents.job_parser import job_parser_agent
from agents.matcher import matcher_agent
from agents.ats_optimizer import ats_optimizer_agent
from agents.career_advisor import career_advisor_agent
from agents.report_generator import report_generator_agent
from agents.investigator import investigator_agent
from agents.interview_prep import interview_prep_agent
from agents.resume_coach import resume_coach_agent
from config import config
from concurrent.futures import ThreadPoolExecutor, as_completed
import copy
import time


def parallel_parse(state: AgentState) -> AgentState:
    """
    PHASE 1: Parse resume and job description in parallel.
    Saves ~3-5 seconds by running both parsers simultaneously.
    """
    start = time.time()
    
    # Run parsers sequentially for now to debug the issue
    # Resume parsing
    state = resume_parser_agent(state)
    
    # Job parsing  
    state = job_parser_agent(state)
    
    print(f"DEBUG parallel_parse: job_title after parsing = '{state.get('job_title', 'NOT SET')}'")
    
    elapsed = time.time() - start
    state['messages'].append(f"✅ Parsing complete ({elapsed:.1f}s)")
    return state


def parallel_enhance(state: AgentState) -> AgentState:
    """
    PHASE 2: Run all enhancement agents in parallel.
    - ATS + Career Advisor (combined)
    - Investigator (if company name provided)
    - Interview Prep
    - Resume Coach
    
    Saves ~15-20 seconds by running 4 agents simultaneously instead of sequentially.
    """
    start = time.time()
    
    company_name = state.get('company_name')
    results = {}
    
    def run_agent(name, agent_func, agent_state):
        try:
            result = agent_func(copy.deepcopy(agent_state))
            return name, result
        except Exception as e:
            return name, {"error": str(e)}
    
    # Determine which agents to run
    agents_to_run = [
        ("ats_career", lambda s: career_advisor_agent(ats_optimizer_agent(s)), state),
        ("interview_prep", interview_prep_agent, state),
        ("resume_coach", resume_coach_agent, state),
    ]
    
    # Only run investigator if company name is provided
    if company_name:
        agents_to_run.append(("investigator", investigator_agent, state))
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(run_agent, name, func, s) 
            for name, func, s in agents_to_run
        ]
        
        for future in as_completed(futures):
            name, result = future.result()
            results[name] = result
    
    # Merge ATS + Career results
    if "ats_career" in results and isinstance(results["ats_career"], dict):
        r = results["ats_career"]
        state['ats_recommendations'] = r.get('ats_recommendations', [])
        state['career_advice'] = r.get('career_advice', [])
        state['improvement_suggestions'] = r.get('improvement_suggestions', [])
    
    # Merge investigator results
    if "investigator" in results and isinstance(results["investigator"], dict):
        state['company_intel'] = results["investigator"].get('company_intel', {})
    else:
        state['company_intel'] = {}
    
    # Merge interview prep results
    if "interview_prep" in results and isinstance(results["interview_prep"], dict):
        state['interview_questions'] = results["interview_prep"].get('interview_questions', [])
    else:
        state['interview_questions'] = []
    
    # Merge resume coach results
    if "resume_coach" in results and isinstance(results["resume_coach"], dict):
        state['tailored_resume_suggestions'] = results["resume_coach"].get('tailored_resume_suggestions', [])
    else:
        state['tailored_resume_suggestions'] = []
    
    elapsed = time.time() - start
    agents_run = len(agents_to_run)
    state['messages'].append(f"✅ Parallel enhancement complete ({agents_run} agents in {elapsed:.1f}s)")
    return state


def create_workflow():
    """
    Create the optimized LangGraph workflow.
    
    Total steps: 4 (down from 9)
    Expected latency: ~15-20s (down from ~35s)
    """
    
    workflow = StateGraph(AgentState)
    
    # Phase 1: Parallel parsing (resume + job simultaneously)
    workflow.add_node("parallel_parse", parallel_parse)
    
    # Matcher (needs both parsed results)
    workflow.add_node("matcher", matcher_agent)
    
    # Phase 2: Parallel enhancement (all advice agents simultaneously)
    workflow.add_node("parallel_enhance", parallel_enhance)
    
    # Report generator (optional)
    workflow.add_node("report_generator", report_generator_agent)
    
    # Define edges
    workflow.set_entry_point("parallel_parse")
    workflow.add_edge("parallel_parse", "matcher")
    workflow.add_edge("matcher", "parallel_enhance")
    workflow.add_edge("parallel_enhance", "report_generator")
    workflow.add_edge("report_generator", END)
    
    return workflow.compile()


# Create the workflow instance
resume_analyzer_graph = create_workflow()
