from graph.state import AgentState
from tools.report_generator import report_generator
from config import config

def report_generator_agent(state: AgentState) -> AgentState:
    """
    Agent responsible for generating comprehensive analysis reports
    """
    # Skip report generation if configured for speed
    if config.SKIP_REPORTS:
        state['pdf_report'] = None
        state['html_report'] = None
        state['messages'].append("⏭️ Report generation skipped (speed mode)")
        state['current_step'] = "reports_skipped"
        return state
    
    try:
        analysis_data = {
            'match_score': state['match_score'],
            'job_title': state.get('job_title', 'Target Position'),
            'matched_skills': state['matched_skills'],
            'missing_skills': state['missing_skills'],
            'strengths': state['strengths'],
            'weaknesses': state['weaknesses'],
            'ats_recommendations': state.get('ats_recommendations', []),
            'career_advice': state.get('career_advice', []),
            'improvement_suggestions': state.get('improvement_suggestions', [])
        }
        
        # Generate PDF report
        pdf_buffer = report_generator.generate_pdf_report(analysis_data)
        state['pdf_report'] = pdf_buffer.getvalue()
        
        # Generate HTML report
        html_report = report_generator.generate_html_report(analysis_data)
        state['html_report'] = html_report
        
        state['messages'].append("✅ Reports generated successfully")
        state['current_step'] = "reports_generated"
        
    except Exception as e:
        state['error'] = f"Report generation failed: {str(e)}"
        state['messages'].append(f"⚠️ Report generation error: {str(e)}")
    
    return state