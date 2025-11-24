from typing import Dict, List
from datetime import datetime
import io
import base64
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend

class ReportGenerator:
    """Generate professional PDF reports for resume analysis"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#1e3a8a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section Header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=HexColor('#2563eb'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Body text
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        ))
        
        # Bullet points
        self.styles.add(ParagraphStyle(
            name='BulletPoint',
            parent=self.styles['BodyText'],
            fontSize=10,
            leftIndent=20,
            spaceAfter=6
        ))
    
    def _create_match_score_chart(self, match_score: float) -> str:
        """Create a gauge chart for match score"""
        fig, ax = plt.subplots(figsize=(6, 3))
        
        # Create gauge chart
        categories = ['Poor', 'Fair', 'Good', 'Excellent']
        colors_list = ['#ef4444', '#f59e0b', '#10b981', '#059669']
        
        # Determine which category the score falls into
        if match_score < 50:
            color_idx = 0
        elif match_score < 70:
            color_idx = 1
        elif match_score < 85:
            color_idx = 2
        else:
            color_idx = 3
        
        # Create horizontal bar
        ax.barh(0, match_score, height=0.5, color=colors_list[color_idx], alpha=0.8)
        ax.set_xlim(0, 100)
        ax.set_ylim(-0.5, 0.5)
        ax.set_xlabel('Match Score (%)', fontsize=12, fontweight='bold')
        ax.set_title(f'Overall Match Score: {match_score}%', fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        
        # Remove y-axis
        ax.set_yticks([])
        
        # Add vertical lines for categories
        ax.axvline(x=50, color='gray', linestyle='--', alpha=0.5)
        ax.axvline(x=70, color='gray', linestyle='--', alpha=0.5)
        ax.axvline(x=85, color='gray', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        
        # Save to bytes
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer
    
    def _create_skills_chart(self, matched_skills: List[str], missing_skills: List[str]) -> str:
        """Create a pie chart for skills distribution"""
        fig, ax = plt.subplots(figsize=(6, 4))
        
        matched_count = len(matched_skills)
        missing_count = len(missing_skills)
        
        if matched_count == 0 and missing_count == 0:
            matched_count = 1  # Avoid empty chart
        
        sizes = [matched_count, missing_count]
        labels = [f'Matched\n({matched_count})', f'Missing\n({missing_count})']
        colors_list = ['#10b981', '#ef4444']
        explode = (0.05, 0)
        
        ax.pie(sizes, explode=explode, labels=labels, colors=colors_list,
               autopct='%1.1f%%', shadow=True, startangle=90)
        ax.set_title('Skills Match Distribution', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        # Save to bytes
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer
    
    def generate_pdf_report(self, analysis_data: Dict) -> io.BytesIO:
        """Generate a comprehensive PDF report"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Title
        title = Paragraph("Resume Analysis Report", self.styles['CustomTitle'])
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Date and metadata
        date_str = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        metadata = Paragraph(f"<i>Generated on: {date_str}</i>", self.styles['CustomBody'])
        elements.append(metadata)
        elements.append(Spacer(1, 20))
        
        # Executive Summary
        elements.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        match_score = analysis_data.get('match_score', 0)
        job_title = analysis_data.get('job_title', 'Target Position')
        
        summary_text = f"""
        This comprehensive analysis evaluates the candidate's resume against the requirements 
        for the <b>{job_title}</b> position. The overall match score of <b>{match_score}%</b> 
        indicates a <b>{"strong" if match_score >= 75 else "moderate" if match_score >= 60 else "developing"}</b> 
        alignment with the job requirements.
        """
        elements.append(Paragraph(summary_text, self.styles['CustomBody']))
        elements.append(Spacer(1, 20))
        
        # Match Score Chart
        try:
            match_chart = self._create_match_score_chart(match_score)
            img = Image(match_chart, width=5*inch, height=2.5*inch)
            elements.append(img)
            elements.append(Spacer(1, 20))
        except Exception as e:
            print(f"Error creating match score chart: {e}")
        
        # Key Metrics Table
        elements.append(Paragraph("Key Metrics", self.styles['SectionHeader']))
        
        metrics_data = [
            ['Metric', 'Value'],
            ['Overall Match Score', f"{match_score}%"],
            ['Skills Matched', str(len(analysis_data.get('matched_skills', [])))],
            ['Skills Gap', str(len(analysis_data.get('missing_skills', [])))],
            ['Key Strengths', str(len(analysis_data.get('strengths', [])))],
        ]
        
        metrics_table = Table(metrics_data, colWidths=[3*inch, 2*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
        ]))
        elements.append(metrics_table)
        elements.append(Spacer(1, 20))
        
        # Skills Analysis Chart
        try:
            skills_chart = self._create_skills_chart(
                analysis_data.get('matched_skills', []),
                analysis_data.get('missing_skills', [])
            )
            img = Image(skills_chart, width=4*inch, height=3*inch)
            elements.append(img)
            elements.append(Spacer(1, 20))
        except Exception as e:
            print(f"Error creating skills chart: {e}")
        
        # Strengths Section
        elements.append(Paragraph("Key Strengths", self.styles['SectionHeader']))
        strengths = analysis_data.get('strengths', [])[:10]
        if strengths:
            for strength in strengths:
                bullet = Paragraph(f"• <b>{strength}</b>", self.styles['BulletPoint'])
                elements.append(bullet)
        else:
            elements.append(Paragraph("No specific strengths identified.", self.styles['CustomBody']))
        elements.append(Spacer(1, 15))
        
        # Areas for Improvement Section
        elements.append(Paragraph("Areas for Improvement", self.styles['SectionHeader']))
        weaknesses = analysis_data.get('missing_skills', [])[:10]
        if weaknesses:
            for weakness in weaknesses:
                bullet = Paragraph(f"• {weakness}", self.styles['BulletPoint'])
                elements.append(bullet)
        else:
            elements.append(Paragraph("No significant gaps identified.", self.styles['CustomBody']))
        elements.append(Spacer(1, 15))
        
        # Page Break
        elements.append(PageBreak())
        
        # ATS Optimization Recommendations
        elements.append(Paragraph("ATS Optimization Recommendations", self.styles['SectionHeader']))
        ats_recommendations = analysis_data.get('ats_recommendations', [])
        if ats_recommendations:
            for i, rec in enumerate(ats_recommendations, 1):
                rec_text = Paragraph(f"<b>{i}.</b> {rec}", self.styles['CustomBody'])
                elements.append(rec_text)
                elements.append(Spacer(1, 8))
        else:
            elements.append(Paragraph("No specific ATS recommendations available.", self.styles['CustomBody']))
        elements.append(Spacer(1, 15))
        
        # Career Development Advice
        elements.append(Paragraph("Career Development Recommendations", self.styles['SectionHeader']))
        career_advice = analysis_data.get('career_advice', [])
        if career_advice:
            for i, advice in enumerate(career_advice, 1):
                advice_text = Paragraph(f"<b>{i}.</b> {advice}", self.styles['CustomBody'])
                elements.append(advice_text)
                elements.append(Spacer(1, 8))
        else:
            elements.append(Paragraph("No specific career advice available.", self.styles['CustomBody']))
        elements.append(Spacer(1, 15))
        
        # Improvement Suggestions
        improvement_suggestions = analysis_data.get('improvement_suggestions', [])
        if improvement_suggestions:
            elements.append(Paragraph("Immediate Action Items", self.styles['SectionHeader']))
            for i, suggestion in enumerate(improvement_suggestions, 1):
                suggestion_text = Paragraph(f"<b>{i}.</b> {suggestion}", self.styles['CustomBody'])
                elements.append(suggestion_text)
                elements.append(Spacer(1, 8))
            elements.append(Spacer(1, 15))
        
        # Conclusion
        elements.append(Paragraph("Conclusion", self.styles['SectionHeader']))
        
        if match_score >= 80:
            conclusion = """
            <b>Excellent Match!</b> Your profile demonstrates strong alignment with the job requirements. 
            Focus on highlighting your matched skills during interviews and continue building on your strengths.
            """
        elif match_score >= 60:
            conclusion = """
            <b>Good Potential!</b> Your profile shows promising alignment with several key requirements. 
            Address the identified skill gaps through targeted learning and projects to strengthen your candidacy.
            """
        else:
            conclusion = """
            <b>Development Opportunity!</b> While there are notable gaps, this analysis provides a clear roadmap 
            for skill development. Focus on acquiring the missing skills through courses, certifications, and practical projects.
            """
        
        elements.append(Paragraph(conclusion, self.styles['CustomBody']))
        elements.append(Spacer(1, 20))
        
        # Footer note
        footer_note = Paragraph(
            "<i>This report was generated by an AI-powered resume analysis system. "
            "Recommendations should be considered as guidance and adapted to your specific situation.</i>",
            self.styles['CustomBody']
        )
        elements.append(footer_note)
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def generate_html_report(self, analysis_data: Dict) -> str:
        """Generate a comprehensive HTML report"""
        
        match_score = analysis_data.get('match_score', 0)
        job_title = analysis_data.get('job_title', 'Target Position')
        date_str = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        
        # Determine match level
        if match_score >= 80:
            match_level = "Excellent"
            match_color = "#059669"
        elif match_score >= 60:
            match_level = "Good"
            match_color = "#10b981"
        elif match_score >= 40:
            match_level = "Fair"
            match_color = "#f59e0b"
        else:
            match_level = "Developing"
            match_color = "#ef4444"
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Resume Analysis Report</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 20px;
                }}
                
                .container {{
                    max-width: 1000px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px;
                    text-align: center;
                }}
                
                .header h1 {{
                    font-size: 2.5em;
                    margin-bottom: 10px;
                }}
                
                .header p {{
                    font-size: 1em;
                    opacity: 0.9;
                }}
                
                .content {{
                    padding: 40px;
                }}
                
                .score-section {{
                    text-align: center;
                    padding: 30px;
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    border-radius: 10px;
                    margin-bottom: 30px;
                }}
                
                .score-circle {{
                    width: 200px;
                    height: 200px;
                    margin: 0 auto 20px;
                    border-radius: 50%;
                    background: conic-gradient(
                        {match_color} {match_score * 3.6}deg,
                        #e5e7eb {match_score * 3.6}deg
                    );
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    position: relative;
                }}
                
                .score-inner {{
                    width: 160px;
                    height: 160px;
                    background: white;
                    border-radius: 50%;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                }}
                
                .score-value {{
                    font-size: 3em;
                    font-weight: bold;
                    color: {match_color};
                }}
                
                .score-label {{
                    font-size: 1.2em;
                    color: #666;
                    margin-top: 5px;
                }}
                
                .section {{
                    margin-bottom: 30px;
                }}
                
                .section-title {{
                    font-size: 1.8em;
                    color: #667eea;
                    margin-bottom: 15px;
                    padding-bottom: 10px;
                    border-bottom: 3px solid #667eea;
                }}
                
                .metrics-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                
                .metric-card {{
                    background: #f9fafb;
                    padding: 20px;
                    border-radius: 8px;
                    border-left: 4px solid #667eea;
                }}
                
                .metric-label {{
                    font-size: 0.9em;
                    color: #666;
                    margin-bottom: 5px;
                }}
                
                .metric-value {{
                    font-size: 1.8em;
                    font-weight: bold;
                    color: #333;
                }}
                
                .skills-container {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 10px;
                    margin-top: 15px;
                }}
                
                .skill-tag {{
                    background: #667eea;
                    color: white;
                    padding: 8px 15px;
                    border-radius: 20px;
                    font-size: 0.9em;
                }}
                
                .skill-tag.missing {{
                    background: #ef4444;
                }}
                
                .recommendation-list {{
                    list-style: none;
                }}
                
                .recommendation-item {{
                    background: #f9fafb;
                    padding: 15px;
                    margin-bottom: 10px;
                    border-radius: 8px;
                    border-left: 4px solid #10b981;
                }}
                
                .recommendation-item:before {{
                    content: "✓";
                    color: #10b981;
                    font-weight: bold;
                    margin-right: 10px;
                }}
                
                .advice-list {{
                    list-style: none;
                }}
                
                .advice-item {{
                    background: #fffbeb;
                    padding: 15px;
                    margin-bottom: 10px;
                    border-radius: 8px;
                    border-left: 4px solid #f59e0b;
                }}
                
                .advice-item:before {{
                    content: "💡";
                    margin-right: 10px;
                }}
                
                .conclusion {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    margin-top: 30px;
                }}
                
                .footer {{
                    text-align: center;
                    padding: 20px;
                    background: #f9fafb;
                    color: #666;
                    font-size: 0.9em;
                }}
                
                @media print {{
                    body {{
                        background: white;
                        padding: 0;
                    }}
                    .container {{
                        box-shadow: none;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Resume Analysis Report</h1>
                    <p>Generated on {date_str}</p>
                    <p>Position: <strong>{job_title}</strong></p>
                </div>
                
                <div class="content">
                    <!-- Score Section -->
                    <div class="score-section">
                        <div class="score-circle">
                            <div class="score-inner">
                                <div class="score-value">{match_score}%</div>
                                <div class="score-label">{match_level}</div>
                            </div>
                        </div>
                        <h2 style="color: {match_color};">Overall Match Score</h2>
                    </div>
                    
                    <!-- Key Metrics -->
                    <div class="section">
                        <h2 class="section-title">Key Metrics</h2>
                        <div class="metrics-grid">
                            <div class="metric-card">
                                <div class="metric-label">Skills Matched</div>
                                <div class="metric-value">{len(analysis_data.get('matched_skills', []))}</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-label">Skills Gap</div>
                                <div class="metric-value">{len(analysis_data.get('missing_skills', []))}</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-label">Key Strengths</div>
                                <div class="metric-value">{len(analysis_data.get('strengths', []))}</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-label">Match Level</div>
                                <div class="metric-value" style="font-size: 1.2em;">{match_level}</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Matched Skills -->
                    <div class="section">
                        <h2 class="section-title">✅ Matched Skills</h2>
                        <div class="skills-container">
        """
        
        # Add matched skills
        matched_skills = analysis_data.get('matched_skills', [])[:15]
        for skill in matched_skills:
            html += f'<span class="skill-tag">{skill}</span>\n'
        
        html += """
                        </div>
                    </div>
                    
                    <!-- Missing Skills -->
                    <div class="section">
                        <h2 class="section-title">❌ Skills to Develop</h2>
                        <div class="skills-container">
        """
        
        # Add missing skills
        missing_skills = analysis_data.get('missing_skills', [])[:15]
        for skill in missing_skills:
            html += f'<span class="skill-tag missing">{skill}</span>\n'
        
        html += """
                        </div>
                    </div>
                    
                    <!-- ATS Recommendations -->
                    <div class="section">
                        <h2 class="section-title">🎯 ATS Optimization Recommendations</h2>
                        <ul class="recommendation-list">
        """
        
        # Add ATS recommendations
        ats_recommendations = analysis_data.get('ats_recommendations', [])
        for rec in ats_recommendations:
            html += f'<li class="recommendation-item">{rec}</li>\n'
        
        html += """
                        </ul>
                    </div>
                    
                    <!-- Career Advice -->
                    <div class="section">
                        <h2 class="section-title">💼 Career Development Recommendations</h2>
                        <ul class="advice-list">
        """
        
        # Add career advice
        career_advice = analysis_data.get('career_advice', [])
        for advice in career_advice:
            html += f'<li class="advice-item">{advice}</li>\n'
        
        html += """
                        </ul>
                    </div>
                    
                    <!-- Conclusion -->
                    <div class="conclusion">
                        <h2 style="margin-bottom: 15px;">Conclusion</h2>
        """
        
        if match_score >= 80:
            html += """
                        <p><strong>Excellent Match!</strong> Your profile demonstrates strong alignment with the job requirements. 
                        Focus on highlighting your matched skills during interviews and continue building on your strengths.</p>
            """
        elif match_score >= 60:
            html += """
                        <p><strong>Good Potential!</strong> Your profile shows promising alignment with several key requirements. 
                        Address the identified skill gaps through targeted learning and projects to strengthen your candidacy.</p>
            """
        else:
            html += """
                        <p><strong>Development Opportunity!</strong> While there are notable gaps, this analysis provides a clear roadmap 
                        for skill development. Focus on acquiring the missing skills through courses, certifications, and practical projects.</p>
            """
        
        html += """
                    </div>
                </div>
                
                <div class="footer">
                    <p>This report was generated by an AI-powered resume analysis system.</p>
                    <p>Recommendations should be considered as guidance and adapted to your specific situation.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html

# Global instance
report_generator = ReportGenerator()