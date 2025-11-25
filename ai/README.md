# 🤖 AI Service - Multi-Agent Resume Analyzer

Flask microservice using **LangGraph** to orchestrate 6 specialized AI agents powered by **OpenAI GPT-4** for comprehensive resume analysis.

## 📁 Project Structure
```
ai/
├── agents/
│   ├── resume_parser.py      # Extract text, sections, skills
│   ├── job_parser.py          # Parse job requirements
│   ├── matcher.py             # Calculate match scores
│   ├── ats_optimizer.py       # ATS recommendations
│   ├── career_advisor.py      # Career guidance
│   └── report_generator.py    # PDF/HTML generation
├── graph/
│   ├── state.py               # Shared agent state
│   └── workflow.py            # LangGraph workflow
├── tools/
│   ├── text_extraction.py     # PDF/DOCX parsing
│   ├── nlp_tools.py           # spaCy NLP utilities
│   ├── matching_tools.py      # Similarity calculation
│   └── report_generator.py    # Report creation
├── app.py                     # Flask application
├── config.py                  # Configuration
├── requirements.txt
└── Dockerfile
```

## 🛠️ Tech Stack

- **Flask 3.0.0** - Web framework
- **LangChain 0.1.0** - LLM orchestration
- **LangGraph 0.0.20** - Multi-agent workflow
- **OpenAI GPT-4** - Language model (gpt-4.1-nano)
- **Sentence Transformers 2.2.2** - Semantic similarity (all-MiniLM-L6-v2)
- **spaCy 3.7.2** - NLP processing
- **PyMuPDF 1.23.8** - PDF text extraction
- **ReportLab 4.0.7** - PDF generation
- **Matplotlib 3.8.2** - Chart generation

## 🚀 Setup
```bash
cd ai

# Create .env file with OpenAI API key
echo "OPENAI_API_KEY=your_openai_api_key" > .env

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Run the service
python app.py
```

Service runs on: `http://localhost:6000`

## 📡 API Endpoints

### 1. Analyze Resume
**POST** `/api/analyze`

**Request:** `multipart/form-data`
- `file` - Resume file (PDF or DOCX)
- `jobDescriptionText` - Job description text

**Response:**
```json
{
  "analysisId": "uuid-string",
  "matchScore": 87.45,
  "skills": "python, java, spring boot",
  "strengths": "python, java, algorithms",
  "weaknesses": "docker, kubernetes, aws",
  "atsRecommendations": [
    "Add keywords: Docker, Kubernetes to skills section",
    "Include years of experience in job titles"
  ],
  "careerAdvice": [
    "Consider AWS certification",
    "Build DevOps projects"
  ],
  "jobTitle": "Senior Software Engineer",
  "hasReports": true
}
```

### 2. Download PDF Report
**GET** `/api/report/pdf/<analysis_id>`

Returns: PDF file with charts and comprehensive analysis

### 3. View HTML Report
**GET** `/api/report/html/<analysis_id>`

Returns: Interactive HTML report

### 4. Health Check
**GET** `/health`

Returns: `{"status": "healthy", "service": "Resume Analyzer AI"}`

## 🤖 Multi-Agent Workflow
```
1. Resume Parser Agent
   ├─ Extracts text from PDF/DOCX
   ├─ Identifies sections (Experience, Education, Skills)
   └─ Extracts technical skills using spaCy + GPT-4

2. Job Parser Agent
   ├─ Extracts job title and requirements
   ├─ Identifies required skills
   └─ Determines experience level

3. Matcher Agent
   ├─ Calculates semantic similarity (60% weight)
   ├─ Performs skill matching (40% weight)
   └─ Identifies strengths and weaknesses

4. ATS Optimizer Agent
   └─ Generates 5-7 ATS optimization recommendations

5. Career Advisor Agent
   └─ Provides 5-7 career development suggestions

6. Report Generator Agent
   ├─ Creates PDF report with charts
   └─ Generates interactive HTML report
```

## 🔧 Configuration

Edit `config.py`:
```python
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-4.1-nano"
TEMPERATURE = 0.3
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
SPACY_MODEL = "en_core_web_sm"
MIN_MATCH_SCORE = 60.0
HIGH_MATCH_SCORE = 80.0
```

## 📊 Matching Algorithm
```python
# Calculate semantic similarity
embedding1 = model.encode(resume_text)
embedding2 = model.encode(job_description)
semantic_similarity = cosine_similarity(embedding1, embedding2) * 100

# Calculate skill match
matched_skills = resume_skills ∩ job_skills
skill_match = (len(matched_skills) / len(job_skills)) * 100

# Weighted final score
final_score = (semantic_similarity * 0.6) + (skill_match * 0.4)
```

## 🐳 Docker Deployment
```bash
# Build image
docker build -t resume-analyzer-ai .

# Run container
docker run -p 6000:6000 -e OPENAI_API_KEY=your_key resume-analyzer-ai
```

## 🐛 Troubleshooting

**Issue:** "OpenAI API key not found"  
**Solution:** Set environment variable: `export OPENAI_API_KEY=your_key`

**Issue:** "spaCy model not found"  
**Solution:** Run `python -m spacy download en_core_web_sm`

**Issue:** "Module not found errors"  
**Solution:** Run `pip install -r requirements.txt`