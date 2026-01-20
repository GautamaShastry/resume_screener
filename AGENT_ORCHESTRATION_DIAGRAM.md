# AI Resume Analyzer - Agent Orchestration Visualization

## 1. High-Level Workflow (Draw This on Whiteboard)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              USER REQUEST                                        │
│                    (Resume PDF + Job Description)                                │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           LANGGRAPH WORKFLOW                                     │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                         SHARED STATE (AgentState)                        │   │
│  │  ┌──────────────┬──────────────┬──────────────┬──────────────────────┐  │   │
│  │  │ resume_text  │ job_skills   │ match_score  │ recommendations      │  │   │
│  │  │ resume_skills│ job_title    │ matched_skills│ career_advice       │  │   │
│  │  │ sections     │ requirements │ missing_skills│ messages[]          │  │   │
│  │  └──────────────┴──────────────┴──────────────┴──────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                      │                                          │
│  ════════════════════════════════════╪══════════════════════════════════════   │
│                                      ▼                                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │   AGENT 1   │───▶│   AGENT 2   │───▶│   AGENT 3   │───▶│   AGENT 4   │      │
│  │   Resume    │    │     Job     │    │   Matcher   │    │     ATS     │      │
│  │   Parser    │    │   Parser    │    │             │    │  Optimizer  │      │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘      │
│         │                  │                  │                  │              │
│         ▼                  ▼                  ▼                  ▼              │
│    ┌─────────┐        ┌─────────┐        ┌─────────┐        ┌─────────┐        │
│    │PyMuPDF  │        │  GPT-4  │        │Sentence │        │  GPT-4  │        │
│    │ spaCy   │        │  spaCy  │        │Transformr│        │         │        │
│    │ GPT-4   │        │         │        │Set Ops  │        │         │        │
│    └─────────┘        └─────────┘        └─────────┘        └─────────┘        │
│                                                                    │            │
│                                                                    ▼            │
│                              ┌─────────────┐    ┌─────────────┐                 │
│                              │   AGENT 5   │───▶│   AGENT 6   │                 │
│                              │   Career    │    │   Report    │                 │
│                              │   Advisor   │    │  Generator  │                 │
│                              └─────────────┘    └─────────────┘                 │
│                                     │                  │                        │
│                                     ▼                  ▼                        │
│                                ┌─────────┐        ┌─────────┐                   │
│                                │  GPT-4  │        │ReportLab│                   │
│                                │(temp=0.7)│       │  HTML   │                   │
│                                └─────────┘        └─────────┘                   │
│                                                        │                        │
└────────────────────────────────────────────────────────┼────────────────────────┘
                                                         ▼
                              ┌─────────────────────────────────────────┐
                              │              RESPONSE                    │
                              │  {matchScore, skills, recommendations}   │
                              └─────────────────────────────────────────┘
```

---

## 2. Detailed Agent Flow (What Each Agent Does)

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║  AGENT 1: RESUME PARSER                                                        ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  INPUT: resume_file (bytes), resume_filename                                   ║
║                                                                                ║
║  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐          ║
║  │  Text Extraction │────▶│  Section Parse  │────▶│  Skill Extract  │          ║
║  │    (PyMuPDF)     │     │    (Regex)      │     │ (spaCy + GPT-4) │          ║
║  └─────────────────┘     └─────────────────┘     └─────────────────┘          ║
║                                                                                ║
║  OUTPUT: resume_text, resume_sections, resume_skills, experience, education    ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
                                      │
                                      ▼
╔═══════════════════════════════════════════════════════════════════════════════╗
║  AGENT 2: JOB PARSER                                                           ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  INPUT: job_description                                                        ║
║                                                                                ║
║  ┌─────────────────┐     ┌─────────────────┐                                  ║
║  │  NLP Extraction │────▶│  LLM Enhancement │                                  ║
║  │    (spaCy)      │     │    (GPT-4)       │                                  ║
║  └─────────────────┘     └─────────────────┘                                  ║
║                                                                                ║
║  OUTPUT: job_title, job_skills, job_requirements, job_experience_required      ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
                                      │
                                      ▼
╔═══════════════════════════════════════════════════════════════════════════════╗
║  AGENT 3: MATCHER                                                              ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  INPUT: resume_text, job_description, resume_skills, job_skills                ║
║                                                                                ║
║  ┌─────────────────────────────────────────────────────────────────┐          ║
║  │                    MATCHING ALGORITHM                            │          ║
║  │                                                                  │          ║
║  │   ┌─────────────────┐          ┌─────────────────┐              │          ║
║  │   │ Semantic Match  │          │   Skill Match   │              │          ║
║  │   │ (Sentence Trans)│          │  (Set Intersect)│              │          ║
║  │   │                 │          │                 │              │          ║
║  │   │  resume_embed   │          │ resume ∩ job    │              │          ║
║  │   │     ·           │          │ = matched       │              │          ║
║  │   │  job_embed      │          │                 │              │          ║
║  │   │  ─────────      │          │ job - resume    │              │          ║
║  │   │  = similarity   │          │ = missing       │              │          ║
║  │   └────────┬────────┘          └────────┬────────┘              │          ║
║  │            │                            │                       │          ║
║  │            │         ┌──────────────────┘                       │          ║
║  │            ▼         ▼                                          │          ║
║  │   ┌─────────────────────────────┐                               │          ║
║  │   │      FINAL SCORE            │                               │          ║
║  │   │  (semantic × 0.6) +         │                               │          ║
║  │   │  (skill_match × 0.4)        │                               │          ║
║  │   └─────────────────────────────┘                               │          ║
║  └─────────────────────────────────────────────────────────────────┘          ║
║                                                                                ║
║  OUTPUT: match_score, matched_skills, missing_skills, strengths, weaknesses    ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
                                      │
                                      ▼
╔═══════════════════════════════════════════════════════════════════════════════╗
║  AGENT 4: ATS OPTIMIZER                                                        ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  INPUT: match_score, matched_skills, missing_skills, resume_sections           ║
║                                                                                ║
║  ┌─────────────────────────────────────────────────────────────────┐          ║
║  │  GPT-4 Prompt:                                                   │          ║
║  │  "Analyze this resume-job match and provide 5-7 ATS              │          ║
║  │   optimization recommendations focusing on:                      │          ║
║  │   - Keyword optimization                                         │          ║
║  │   - Formatting improvements                                      │          ║
║  │   - Missing keywords to add"                                     │          ║
║  └─────────────────────────────────────────────────────────────────┘          ║
║                                                                                ║
║  FALLBACK: Default recommendations if LLM fails                                ║
║                                                                                ║
║  OUTPUT: ats_recommendations[]                                                 ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
                                      │
                                      ▼
╔═══════════════════════════════════════════════════════════════════════════════╗
║  AGENT 5: CAREER ADVISOR                                                       ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  INPUT: job_title, match_score, strengths, weaknesses, experience_count        ║
║                                                                                ║
║  ┌─────────────────────────────────────────────────────────────────┐          ║
║  │  GPT-4 Prompt (temperature=0.7 for creativity):                  │          ║
║  │  "Provide 5-7 career development recommendations:                │          ║
║  │   - Skills to develop                                            │          ║
║  │   - Certifications to pursue                                     │          ║
║  │   - Experience to gain                                           │          ║
║  │   - Career progression path"                                     │          ║
║  └─────────────────────────────────────────────────────────────────┘          ║
║                                                                                ║
║  OUTPUT: career_advice[], improvement_suggestions[]                            ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
                                      │
                                      ▼
╔═══════════════════════════════════════════════════════════════════════════════╗
║  AGENT 6: REPORT GENERATOR                                                     ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  INPUT: All analysis data from state                                           ║
║                                                                                ║
║  ┌─────────────────┐     ┌─────────────────┐                                  ║
║  │  PDF Generation │     │ HTML Generation │                                  ║
║  │   (ReportLab)   │     │   (Template)    │                                  ║
║  └─────────────────┘     └─────────────────┘                                  ║
║                                                                                ║
║  OUTPUT: pdf_report (bytes), html_report (string)                              ║
║                                                                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## 3. State Flow Visualization

```
                    ┌─────────────────────────────────────────┐
                    │           INITIAL STATE                  │
                    │  resume_file: <bytes>                    │
                    │  job_description: "Senior Dev..."        │
                    │  messages: []                            │
                    │  (everything else: empty/null)           │
                    └─────────────────┬───────────────────────┘
                                      │
                    ┌─────────────────▼───────────────────────┐
                    │         AFTER RESUME PARSER              │
                    │  + resume_text: "John Doe..."            │
                    │  + resume_skills: [python, java, react]  │
                    │  + resume_sections: {exp, edu, skills}   │
                    │  + messages: ["✅ Resume parsed"]        │
                    └─────────────────┬───────────────────────┘
                                      │
                    ┌─────────────────▼───────────────────────┐
                    │          AFTER JOB PARSER                │
                    │  + job_title: "Senior Software Engineer" │
                    │  + job_skills: [python, docker, k8s]     │
                    │  + job_requirements: [...]               │
                    │  + messages: [..., "✅ Job parsed"]      │
                    └─────────────────┬───────────────────────┘
                                      │
                    ┌─────────────────▼───────────────────────┐
                    │            AFTER MATCHER                 │
                    │  + match_score: 72.5                     │
                    │  + matched_skills: [python]              │
                    │  + missing_skills: [docker, k8s]         │
                    │  + strengths: [python, java]             │
                    │  + weaknesses: [docker, k8s]             │
                    │  + messages: [..., "✅ Match: 72.5%"]    │
                    └─────────────────┬───────────────────────┘
                                      │
                    ┌─────────────────▼───────────────────────┐
                    │         AFTER ATS OPTIMIZER              │
                    │  + ats_recommendations: [                │
                    │      "Add Docker to skills section",     │
                    │      "Include Kubernetes experience"     │
                    │    ]                                     │
                    │  + messages: [..., "✅ ATS optimized"]   │
                    └─────────────────┬───────────────────────┘
                                      │
                    ┌─────────────────▼───────────────────────┐
                    │         AFTER CAREER ADVISOR             │
                    │  + career_advice: [                      │
                    │      "Get AWS certification",            │
                    │      "Build containerized projects"      │
                    │    ]                                     │
                    │  + improvement_suggestions: [...]        │
                    │  + messages: [..., "✅ Advice ready"]    │
                    └─────────────────┬───────────────────────┘
                                      │
                    ┌─────────────────▼───────────────────────┐
                    │        AFTER REPORT GENERATOR            │
                    │  + pdf_report: <bytes>                   │
                    │  + html_report: "<html>..."              │
                    │  + messages: [..., "✅ Reports ready"]   │
                    │                                          │
                    │  ══════════════════════════════════════  │
                    │           FINAL STATE COMPLETE           │
                    └─────────────────────────────────────────┘
```

---

## 4. Parallel Execution (Enhanced Version)

```
                              ┌─────────────┐
                              │   Resume    │
                              │   Parser    │
                              └──────┬──────┘
                                     │
                              ┌──────▼──────┐
                              │     Job     │
                              │   Parser    │
                              └──────┬──────┘
                                     │
                              ┌──────▼──────┐
                              │   Matcher   │
                              └──────┬──────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │            FAN-OUT              │
                    ▼                                 ▼
           ┌─────────────┐                   ┌─────────────┐
           │     ATS     │                   │   Career    │
           │  Optimizer  │                   │   Advisor   │
           └──────┬──────┘                   └──────┬──────┘
                  │                                 │
                  │    ┌─────────────────────┐     │
                  │    │      FAN-IN         │     │
                  └───▶│  (State Merging)    │◀────┘
                       │                     │
                       │  messages: Annotated│
                       │  [List, operator.add]
                       └──────────┬──────────┘
                                  │
                           ┌──────▼──────┐
                           │   Report    │
                           │  Generator  │
                           └─────────────┘
```

**Code for Parallel Execution:**
```python
# Fan-out: Matcher feeds both agents simultaneously
workflow.add_edge("matcher", "ats_optimizer")
workflow.add_edge("matcher", "career_advisor")

# Fan-in: Both converge at report_generator
workflow.add_edge("ats_optimizer", "report_generator")
workflow.add_edge("career_advisor", "report_generator")

# State handles concurrent writes with reducer
class AgentState(TypedDict):
    messages: Annotated[List[str], operator.add]  # Auto-merges lists
```

---

## 5. Error Handling & Fallback Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT EXECUTION                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   TRY: LLM Call │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
     ┌─────────────────┐          ┌─────────────────┐
     │    SUCCESS      │          │    EXCEPTION    │
     │                 │          │                 │
     │ Parse response  │          │ Log error       │
     │ Update state    │          │ Use fallback    │
     │ Add ✅ message  │          │ Add ⚠️ message  │
     └────────┬────────┘          └────────┬────────┘
              │                             │
              └──────────────┬──────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  RETURN STATE   │
                    │ (always returns │
                    │  valid state)   │
                    └─────────────────┘


Example Fallback:
─────────────────
try:
    response = llm.invoke(prompt)
    state['ats_recommendations'] = parse(response)
except Exception as e:
    state['ats_recommendations'] = [
        "Use standard section headers",
        "Include measurable achievements",
        "Match job keywords in resume"
    ]
    state['messages'].append(f"⚠️ Using defaults: {e}")
```

---

## 6. Technology Stack Visualization

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION LAYER                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    React Frontend (Vite)                             │   │
│  │                    localhost:5173 / Vercel                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API LAYER                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Flask REST API (Port 6000)                        │   │
│  │                                                                      │   │
│  │   POST /api/analyze          GET /api/report/pdf/:id                │   │
│  │   GET /api/report/html/:id   GET /health                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ORCHESTRATION LAYER                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    LangGraph StateGraph                              │   │
│  │                                                                      │   │
│  │   • 6 Agent Nodes                                                   │   │
│  │   • Shared AgentState (TypedDict)                                   │   │
│  │   • Sequential Edge Flow                                            │   │
│  │   • Compile to Executable Graph                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                             AI/ML LAYER                                      │
│  ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐       │
│  │    OpenAI GPT-4   │  │ Sentence Transform│  │   spaCy NLP       │       │
│  │    (gpt-4.1-nano) │  │ (MiniLM-L6-v2)    │  │ (en_core_web_sm)  │       │
│  │                   │  │                   │  │                   │       │
│  │  • Parsing        │  │  • Embeddings     │  │  • Tokenization   │       │
│  │  • Recommendations│  │  • Similarity     │  │  • Skill Extract  │       │
│  │  • Career Advice  │  │                   │  │  • Section Parse  │       │
│  └───────────────────┘  └───────────────────┘  └───────────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            TOOLS LAYER                                       │
│  ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐       │
│  │   Text Extraction │  │  Matching Tools   │  │  Report Generator │       │
│  │                   │  │                   │  │                   │       │
│  │  • PyMuPDF (PDF)  │  │  • Cosine Sim     │  │  • ReportLab PDF  │       │
│  │  • python-docx    │  │  • Set Operations │  │  • HTML Templates │       │
│  └───────────────────┘  └───────────────────┘  └───────────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Quick Whiteboard Version (For Interview)

Draw this simple version:

```
    [Resume + JD]
          │
          ▼
    ┌───────────┐
    │  PARSER   │ ──── spaCy + GPT-4
    └─────┬─────┘
          │
          ▼
    ┌───────────┐
    │  MATCHER  │ ──── Sentence Transformers
    └─────┬─────┘      (60% semantic + 40% skill)
          │
          ▼
    ┌───────────┐
    │ OPTIMIZER │ ──── GPT-4 + Fallbacks
    └─────┬─────┘
          │
          ▼
    ┌───────────┐
    │  ADVISOR  │ ──── GPT-4 (temp=0.7)
    └─────┬─────┘
          │
          ▼
    ┌───────────┐
    │  REPORT   │ ──── PDF + HTML
    └─────┬─────┘
          │
          ▼
    [Analysis Result]
    
    
    KEY: All agents share STATE (TypedDict)
         Each agent reads → processes → writes
```
