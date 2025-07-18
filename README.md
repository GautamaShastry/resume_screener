# 📄 Resume Screener

An AI-powered resume screening platform that helps recruiters and hiring teams evaluate candidate resumes against job descriptions. Upload documents and instantly generate AI-based fit scores, making candidate shortlisting faster and more efficient.

## ✨ Features

- Upload resumes and job descriptions (PDF, DOCX supported)
- AI-generated fit scores using NLP models
- Score breakdown across skills, experience, and keyword relevance
- Secure JWT-based user authentication
- Responsive React.js user interface
- RESTful APIs tested via Postman
- **Future Roadmap:** Role-based access control (Admin/Recruiter)

---

## 🛠️ Tech Stack

| Layer           | Technology                  |
|-----------------|------------------------------|
| Frontend        | React.js (Vercel)            |
| Backend         | Spring Boot (Render)         |
| AI Scoring      | Python NLP Microservice (Render) |
| Database        | MySQL (Render)               |
| Authentication  | JWT (Spring Security)        |
| API Testing     | Postman                      |

---

## 🚀 Deployment Overview

| Component           | Platform      |
|---------------------|---------------|
| Frontend (React)    | Vercel        |
| Backend (Spring Boot) | Render      |
| AI Scoring Service  | Render        |
| MySQL Database      | Render        |

---

## 🏗️ Local Setup Guide

Follow these steps to run the project locally:

### Prerequisites

- **Java 17+**
- **Maven**
- **Node.js 16+**
- **MySQL** (local or cloud)
- **Python 3.x** (for AI scoring microservice)
- **IntelliJ IDEA** (recommended for backend)

---

### 1️⃣ Backend Setup (Spring Boot – IntelliJ)

### Steps:

1. **Clone the repository:**

```bash
git clone https://github.com/GautamaShastry/resume_screener.git
```

2. **Open in IntelliJ IDEA:**

- Go to **File > Open**.
- Select the `/backend` folder inside the cloned repository.
- IntelliJ will recognize it as a Maven project and auto-download dependencies.

3. **Set up MySQL Database:**

- Ensure MySQL is running locally or remotely.
- Create the database using the following SQL command:

```sql
CREATE DATABASE resume_db;
```
