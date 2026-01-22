# 📄 AI-Powered Resume Analyzer

An intelligent resume screening platform powered by **LangGraph multi-agent AI** and **OpenAI GPT-4**. Analyzes resumes against job descriptions providing match scores, ATS optimization tips, career advice, and professional reports.

## ✨ Features

- **Multi-Agent AI Analysis** - 6 specialized agents working together
- **Match Scoring** - Semantic similarity (60%) + Skill matching (40%)
- **ATS Optimization** - Get recommendations to pass applicant tracking systems
- **Career Guidance** - Personalized development advice
- **Professional Reports** - Download PDF/HTML reports with charts
- **Secure Authentication** - JWT + OTP email verification
- **Match History** - Track all your analyses

## 🏗️ Architecture
```
┌─────────────────┐
│  React Frontend │  ←→  Spring Boot API  ←→  Flask AI Service
│  (Port 5173)    │      (Port 8001)          (Port 6000)
└─────────────────┘              ↓
                          PostgreSQL DB
```

**Multi-Agent Workflow:**
```
Resume + Job Description
  ↓
Resume Parser → Job Parser → Matcher → ATS Optimizer → Career Advisor → Report Generator
  ↓
Results + Reports
```

## 🛠️ Tech Stack

| Component | Technologies |
|-----------|-------------|
| **Frontend** | React 18, Vite, Tailwind CSS, Chart.js |
| **Backend** | Spring Boot 3, Spring Security, PostgreSQL, JWT |
| **AI Service** | Flask, LangChain, LangGraph, GPT-4, Sentence Transformers, spaCy |

## 🚀 Quick Start

### Prerequisites
- Node.js 16+, Java 17+, Python 3.10+
- PostgreSQL database
- OpenAI API key

### 1. Database Setup
```sql
CREATE DATABASE resume_db;
```

### 2. Backend (Spring Boot)
```bash
cd resume-analyzer
# Edit src/main/resources/application.properties
# Configure: database URL, username, password, JWT secret, email settings
mvn spring-boot:run
```
Runs on: `http://localhost:8001`

### 3. AI Service (Flask)
```bash
cd ai
echo "OPENAI_API_KEY=your_key_here" > .env
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python app.py
```
Runs on: `http://localhost:6000`

### 4. Frontend (React)
```bash
cd frontend
npm install
npm run dev
```
Runs on: `http://localhost:5173`

## 📡 API Workflow

1. **Signup/Login** → Get JWT token + OTP verification
2. **Upload Resume** → PDF/DOCX file
3. **Add Job Description** → Target position details
4. **Analyze** → AI processes in 10-30 seconds
5. **View Results** → Match score, skills, recommendations
6. **Download Reports** → PDF/HTML with charts

## 📚 Documentation

- [Frontend README](./frontend/README.md) - React components and UI
- [Backend README](./resume-analyzer/README.md) - Spring Boot API
- [AI Service README](./ai/README.md) - Multi-agent workflow

## 📊 Matching Algorithm
```python
# Weighted scoring system
semantic_similarity = cosine_similarity(resume, job_description)
skill_match = matched_skills / total_required_skills

final_score = (semantic_similarity × 0.6) + (skill_match × 0.4)
```

**Score Interpretation:**
- 80-100% → Excellent match
- 60-79% → Good match
- 40-59% → Fair match
- 0-39% → Poor match

## 🚀 Deployment

**Frontend:** Vercel, Netlify  
**Backend:** Render.com, Heroku  
**AI Service:** Render.com, AWS EC2  
**Database:** Render PostgreSQL, AWS RDS

## 👨‍💻 Author

**Gautama Shastry**  
📧 gautamashastry@gmail.com  
🌐 [gautamportfolio.com](https://gautamportfolio.com)

Open to Contributions. If you find any issues, please create a new issue.

## 📄 License

MIT License
