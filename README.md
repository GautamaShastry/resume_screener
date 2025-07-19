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
- Select the `/resume_analyzer` folder inside the cloned repository.
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

### 2️⃣ Frontend Setup (React.js)

### Steps:

1. **Navigate to the frontend folder:**

```bash
cd frontend
```

2. **Install dependencies:**

```bash
npm install
```

3. **Start the React Development Server:**

```bash
npm run dev
```

4. **Access the application:**

   The Application will be running locally at: http://localhost:3000/

### 3️⃣ AI Scoring Service Setup (Python – Flask)

This is the Python-based AI microservice responsible for analyzing resumes against job descriptions using sentence embeddings and NLP keyword extraction.

---

### Steps:

1. **Navigate to the AI service folder:**

  ```bash
  cd ai
  ```

2. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```
   
3. **Run the AI scoring service:**

   ```bash
   python app.py
   ```

4. **Access the AI score API:**

   The API will be running locally at: http://localhost:6000/api/analyze


## 📡 AI Scoring API Endpoint Details

This service provides a single REST API endpoint to analyze resumes against job descriptions and return a match score along with strengths and weaknesses.

---

### 🎯 Endpoint

**POST** `/api/analyze`

---

### 📥 Request Parameters

- **file** (Form-Data):  
  Upload the resume file (supported formats: PDF or DOCX).

- **jobDescriptionText** (Form-Data):  
  Paste the job description text directly in the form.

---

### 📤 Example Request (using Postman or similar tools)

- **URL:**  
  `http://localhost:6000/api/analyze`

- **Method:**  
  POST

- **Body:**  
  Form-Data:
  - `file`: Attach resume file (PDF or DOCX)
  - `jobDescriptionText`: Paste job description text

---

### 📊 Example Response (JSON)

```json
{
  "matchScore": 87.45,
  "skills": "python, machine learning, data analysis",
  "strengths": "python, data analysis",
  "weaknesses": "deep learning, optimization",
  "accuracy": 87.45
}
```

## 📦 Deployment Instructions

- **Frontend:**  
  1. Build the React frontend using:

  ```bash
  npm run build
  ```

  2. Deploy the build folder to **Vercel** or any static hosting provider.

- **Backend (Spring Boot):**

  - Package the Spring Boot application as a JAR file using:

  ```bash
  mvn clean install
  ```

  Deploy the generated JAR to **Render.com** as a web service.

---

## AI Scoring Service (Python Flask)

- Ensure all Python dependencies are listed in `requirements.txt`.
- Deploy the Flask service to **Render.com** as a web service.

---

## Database (PostgreSQL)

- Use **PostgreSQL** hosted on **Render.com** or any managed database provider.
- Ensure connection URLs and credentials are correctly set in the `application.properties` of the backend.

---

## 🔭 Future Enhancements

- Role-based access control (Admin/Recruiter)
- Enhanced resume parsing and keyword extraction
- Analytics dashboard for recruiters
- Dockerized deployment

---

## ✅ Contributions

Contributions are welcome!  
Fork the repository, create a feature branch, and submit a pull request.

---

## 📚 License

This project is licensed under the [MIT License](LICENSE).

---

## 👨‍💻 Author

Developed by **Gautama Shastry**  
🌐 [gautamportfolio.com](https://gautamportfolio.com)
