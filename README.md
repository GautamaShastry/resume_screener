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
| Database        | PostgreSQL (Render)               |
| Authentication  | JWT (Spring Security)        |
| API Testing     | Postman                      |

---

## 🚀 Deployment Overview

| Component           | Platform      |
|---------------------|---------------|
| Frontend (React)    | Vercel        |
| Backend (Spring Boot) | Render      |
| AI Scoring Service  | Render        |
| PostgreSQL Database      | Render        |

---

## 🏗️ Local Setup Guide

Follow these steps to run the project locally:

### Prerequisites

- **Java 17+**
- **Maven**
- **Node.js 16+**
- **PostgreSQL** (local or cloud)
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

- Ensure PostgreSQL is running locally or remotely.
- Create the database using the following SQL command:

```sql
CREATE DATABASE resume_db;
```

4. **Configure `application.properties`:**

- Navigate to:  
  `/src/main/resources/application.properties`

- Replace the placeholders with your actual credentials:

```properties
spring.datasource.url=jdbc:postgresql://localhost:5432/resume_db
spring.datasource.username=your_postgresql_username
spring.datasource.password=your_postgresql_password
jwt.secret=your_jwt_secret_key
```

4. **Run the Spring Boot Application:**

- Locate the file:  
  `src/main/java/com/your/package/ResumeScreenerApplication.java`

- In IntelliJ IDEA:
  - Click the **Run** button (green play icon).
  - Or use the shortcut: **Shift + F10**

- Once running, the backend API will be available at:
http://localhost:8080/
