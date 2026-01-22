from flask import Flask, request, jsonify, send_file, make_response
from werkzeug.utils import secure_filename
import os
import io
import base64

from graph.workflow import resume_analyzer_graph
from graph.state import AgentState

app = Flask(__name__)

# Configure upload settings
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Store results temporarily (in production, use Redis or a database)
analysis_cache = {}

# Preload models at startup for faster first request
print("🔄 Preloading models...")
try:
    from tools.matching_tools import matching_tools
    from tools.nlp_tools import nlp  # This loads spaCy
    # Warm up the sentence transformer
    _ = matching_tools.calculate_similarity("test", "test")
    print("✅ Models preloaded successfully")
except Exception as e:
    print(f"⚠️ Model preload warning: {e}")

@app.route('/api/analyze', methods=['POST'])
def analyze_resume():
    try:
        # Validate request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        if 'jobDescriptionText' not in request.form:
            return jsonify({'error': 'No job description provided'}), 400
        
        file = request.files['file']
        job_description = request.form.get('jobDescriptionText', '')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read file content
        filename = secure_filename(file.filename)
        file_content = file.read()
        
        # Initialize state with all fields including new enhanced features
        initial_state: AgentState = {
            "resume_file": file_content,
            "resume_filename": filename,
            "job_description": job_description,
            "job_url": request.form.get('jobUrl', None),
            "company_name": request.form.get('companyName', None),
            "resume_text": "",
            "resume_sections": {},
            "resume_skills": [],
            "resume_experience": [],
            "resume_education": [],
            "job_title": "",
            "position_type": "",
            "job_requirements": [],
            "job_skills": [],
            "job_experience_required": "",
            "match_score": 0.0,
            "matched_skills": [],
            "missing_skills": [],
            "strengths": [],
            "weaknesses": [],
            "ats_recommendations": [],
            "career_advice": [],
            "improvement_suggestions": [],
            # New enhanced features
            "company_intel": {},
            "interview_questions": [],
            "tailored_resume_suggestions": [],
            # Reports
            "pdf_report": None,
            "html_report": None,
            "messages": [],
            "current_step": "initialized",
            "error": None
        }
        
        # Run the agent workflow
        result = resume_analyzer_graph.invoke(initial_state)
        
        # Check for errors
        if result.get('error'):
            return jsonify({'error': result['error']}), 500
        
        # Generate a unique ID for this analysis
        import uuid
        analysis_id = str(uuid.uuid4())
        
        # Cache the result (including reports)
        analysis_cache[analysis_id] = result
        
        # Prepare response with all features
        response = {
            "analysisId": analysis_id,
            "matchScore": result['match_score'],
            "accuracy": result['match_score'],
            "skills": ", ".join(result['matched_skills'][:10]) if result['matched_skills'] else "N/A",
            "strengths": ", ".join(result['strengths'][:10]) if result['strengths'] else "N/A",
            "weaknesses": ", ".join(result['missing_skills'][:10]) if result['missing_skills'] else "N/A",
            "atsRecommendations": result.get('ats_recommendations', []),
            "careerAdvice": result.get('career_advice', []),
            "improvementSuggestions": result.get('improvement_suggestions', []),
            "jobTitle": result.get('job_title', 'Software Engineer'),
            "positionType": result.get('position_type', 'Full-time'),
            "experienceRequired": result.get('job_experience_required', 'Not specified'),
            "messages": result.get('messages', []),
            "hasReports": result.get('pdf_report') is not None,
            # New enhanced features
            "companyIntel": result.get('company_intel', {}),
            "interviewQuestions": result.get('interview_questions', []),
            "tailoredResumeSuggestions": result.get('tailored_resume_suggestions', [])
        }
        
        print(f"DEBUG app.py: jobTitle='{response['jobTitle']}', exp='{response['experienceRequired']}'")
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/report/pdf/<analysis_id>', methods=['GET'])
def download_pdf_report(analysis_id):
    """Download PDF report for a specific analysis"""
    try:
        if analysis_id not in analysis_cache:
            return jsonify({'error': 'Analysis not found'}), 404
        
        result = analysis_cache[analysis_id]
        pdf_data = result.get('pdf_report')
        
        if not pdf_data:
            return jsonify({'error': 'PDF report not available'}), 404
        
        # Create a BytesIO object from the PDF data
        pdf_buffer = io.BytesIO(pdf_data)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'resume_analysis_report_{analysis_id[:8]}.pdf'
        )
        
    except Exception as e:
        return jsonify({'error': f'Failed to download PDF: {str(e)}'}), 500

@app.route('/api/report/html/<analysis_id>', methods=['GET'])
def get_html_report(analysis_id):
    """View HTML report for a specific analysis"""
    try:
        if analysis_id not in analysis_cache:
            return jsonify({"error": "Analysis not found"}), 404
        
        result = analysis_cache[analysis_id]
        
        # Extract data from cached result
        match_score = result.get('match_score', 0)
        matched_skills = result.get('matched_skills', [])
        missing_skills = result.get('missing_skills', [])
        strengths = result.get('strengths', [])
        weaknesses = result.get('weaknesses', [])
        ats_recommendations = result.get('ats_recommendations', [])
        career_advice = result.get('career_advice', [])
        job_title = result.get('job_title', 'Position')
        
        # Format skills as comma-separated strings
        matched_skills_str = ", ".join(matched_skills[:15]) if matched_skills else "No matched skills identified"
        missing_skills_str = ", ".join(missing_skills[:15]) if missing_skills else "No missing skills identified"
        
        # Generate HTML WITHOUT emojis
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resume Analysis Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
            background: #f5f5f5;
            line-height: 1.6;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2563eb;
            border-bottom: 3px solid #2563eb;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        h2 {{
            color: #1e40af;
            margin-top: 30px;
            margin-bottom: 15px;
        }}
        .score {{
            font-size: 48px;
            font-weight: bold;
            color: #10b981;
            text-align: center;
            margin: 30px 0;
            padding: 20px;
            background: #f0fdf4;
            border-radius: 10px;
        }}
        .job-title {{
            text-align: center;
            font-size: 20px;
            color: #6b7280;
            margin-bottom: 20px;
        }}
        .section {{
            margin: 25px 0;
            padding: 20px;
            background: #f9fafb;
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
        }}
        .strengths {{
            border-left-color: #10b981;
            background: #f0fdf4;
        }}
        .weaknesses {{
            border-left-color: #ef4444;
            background: #fef2f2;
        }}
        .section h2 {{
            margin-top: 0;
        }}
        ul {{
            line-height: 1.8;
            padding-left: 20px;
        }}
        ul li {{
            margin-bottom: 8px;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e5e7eb;
            text-align: center;
            color: #6b7280;
            font-size: 14px;
        }}
        .conclusion {{
            background: #eff6ff;
            padding: 20px;
            border-radius: 8px;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Resume Analysis Report</h1>
        
        <div class="job-title">Position: <strong>{job_title}</strong></div>
        
        <div class="score">Match Score: {match_score:.1f}%</div>
        
        <div class="section strengths">
            <h2>Matched Skills</h2>
            <p>{matched_skills_str}</p>
        </div>
        
        <div class="section weaknesses">
            <h2>Skills to Develop</h2>
            <p>{missing_skills_str}</p>
        </div>
        
        <div class="section">
            <h2>ATS Optimization Recommendations</h2>
            <ul>
                {''.join(f'<li>{rec}</li>' for rec in ats_recommendations) if ats_recommendations else '<li>No specific recommendations available</li>'}
            </ul>
        </div>
        
        <div class="section">
            <h2>Career Development Recommendations</h2>
            <ul>
                {''.join(f'<li>{advice}</li>' for advice in career_advice) if career_advice else '<li>No specific advice available</li>'}
            </ul>
        </div>
        
        <div class="conclusion">
            <h2>Conclusion</h2>
            <p><strong>Development Opportunity!</strong> While there are notable gaps, this analysis provides a clear roadmap for skill development. Focus on acquiring the missing skills through courses, certifications, and practical projects.</p>
        </div>
        
        <div class="footer">
            <p>This report was generated by an AI-powered resume analysis system.</p>
            <p>Recommendations should be considered as guidance and adapted to your specific situation.</p>
            <p><small>Analysis ID: {analysis_id[:8]}</small></p>
        </div>
    </div>
</body>
</html>"""
        
        # Return with proper content type
        response = make_response(html_content)
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        return response
        
    except Exception as e:
        error_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Error</title>
</head>
<body>
    <h1>Error Loading Report</h1>
    <p>{str(e)}</p>
</body>
</html>"""
        return make_response(error_html, 500)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Resume Analyzer AI'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000, debug=False, threaded=True)