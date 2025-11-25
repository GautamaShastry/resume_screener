# 🔧 Backend API - Resume Analyzer

Spring Boot REST API with **JWT authentication**, **OTP email verification**, and **PostgreSQL** database for the resume analysis platform.

## 📁 Project Structure
```
resume-analyzer/
├── src/main/java/com/resume/resume_analyzer/
│   ├── config/
│   │   ├── SecurityConfig.java    # Security & CORS
│   │   ├── JWTUtil.java          # JWT utilities
│   │   ├── JwtAuthFilter.java    # JWT filter
│   │   └── MailConfig.java       # Email configuration
│   ├── controller/
│   │   ├── AuthController.java        # Authentication
│   │   ├── ResumeController.java      # Resume upload
│   │   ├── JobDescriptionController.java
│   │   ├── MatchResultController.java # Analysis
│   │   ├── ReportController.java      # PDF/HTML reports
│   │   └── UserController.java        # User profile
│   ├── dto/                       # Data transfer objects
│   ├── entity/                    # JPA entities
│   ├── repository/                # Database repos
│   └── service/                   # Business logic
├── src/main/resources/
│   └── application.properties     # Configuration
└── pom.xml
```

## 🛠️ Tech Stack

- **Spring Boot 3.x** - Application framework
- **Spring Security 6.x** - Authentication & authorization
- **Spring Data JPA** - Database ORM
- **PostgreSQL** - Primary database
- **JWT (jjwt 0.11.5)** - Token authentication
- **JavaMail** - Email OTP delivery
- **Lombok** - Boilerplate reduction
- **Maven** - Build tool

## 🚀 Setup

### 1. Database Setup
```sql
CREATE DATABASE resume_db;
```

### 2. Configure Application

Edit `src/main/resources/application.properties`:
```properties
# Database Configuration
spring.datasource.url=jdbc:postgresql://localhost:5432/resume_db
spring.datasource.username=postgres
spring.datasource.password=your_password
spring.jpa.hibernate.ddl-auto=update

# Server Port
server.port=8001

# JWT Configuration
jwt.secret=your_base64_encoded_secret_key
jwt.expiration=86400000

# Email Configuration (Gmail)
spring.mail.host=smtp.gmail.com
spring.mail.port=587
spring.mail.username=your_email@gmail.com
spring.mail.password=your_app_specific_password
spring.mail.properties.mail.smtp.auth=true
spring.mail.properties.mail.smtp.starttls.enable=true

# File Upload
spring.servlet.multipart.max-file-size=10MB
spring.servlet.multipart.max-request-size=10MB
```

**Generate JWT Secret:**
```bash
openssl rand -base64 64
```

**Gmail App Password:**
1. Enable 2-factor authentication
2. Generate App Password in Google Account
3. Use this password in configuration

### 3. Build & Run
```bash
cd resume-analyzer

# Build project
mvn clean install

# Run application
mvn spring-boot:run
```

Server runs on: `http://localhost:8001`

## 📡 API Endpoints

### Authentication

#### Signup
**POST** `/api/auth/signup`
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```
Response: `"User registered successfully"`

#### Login (Sends OTP)
**POST** `/api/auth/login`
```json
{
  "email": "john@example.com",
  "password": "securepassword123"
}
```
Response:
```json
{
  "message": "OTP sent successfully to john@example.com",
  "email": "john@example.com"
}
```

#### Verify OTP
**POST** `/api/auth/verify`
```json
{
  "email": "john@example.com",
  "otpCode": "123456"
}
```
Response:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Resend OTP
**POST** `/api/auth/resend-otp`
```json
{
  "email": "john@example.com"
}
```

### Resume Management

#### Upload Resume
**POST** `/api/resume/upload`
- Headers: `Authorization: Bearer <token>`
- Content-Type: `multipart/form-data`
- Body: `file` (PDF or DOCX)

Response:
```json
{
  "resumeId": 1
}
```

#### Get Resume Details
**GET** `/api/resume/{id}`
- Headers: `Authorization: Bearer <token>`

Response:
```json
{
  "id": 1,
  "fileName": "resume.pdf",
  "uploadedAt": "2024-01-15T10:30:00",
  "uploadedBy": "john@example.com"
}
```

### Job Description

#### Upload Job
**POST** `/api/job/upload`
- Headers: `Authorization: Bearer <token>`
```json
{
  "title": "Senior Software Engineer",
  "description": "Full job description text..."
}
```
Response:
```json
{
  "jobDescriptionId": 1
}
```

#### Get Job Details
**GET** `/api/job/{id}`
- Headers: `Authorization: Bearer <token>`

### Match Analysis

#### Analyze Resume
**POST** `/api/match/matchResume?resumeId=1&jobDescriptionId=1`
- Headers: `Authorization: Bearer <token>`

Response:
```json
{
  "matchResultId": 1,
  "analysisId": "uuid-string",
  "matchScore": 87.45,
  "accuracy": 87.45,
  "skills": "python, java, spring boot",
  "strengths": "python, java, algorithms",
  "weaknesses": "docker, kubernetes, aws",
  "hasReports": true,
  "jobTitle": "Senior Software Engineer",
  "atsRecommendations": [...],
  "careerAdvice": [...],
  "improvementSuggestions": [...]
}
```

#### Get Match History
**GET** `/api/match/history`
- Headers: `Authorization: Bearer <token>`

Returns array of all past matches with details.

### Reports

#### Download PDF Report
**GET** `/api/report/pdf/{matchResultId}`
- Headers: `Authorization: Bearer <token>`
- Returns: PDF file

#### View HTML Report
**GET** `/api/report/html/{matchResultId}`
- Headers: `Authorization: Bearer <token>`
- Returns: HTML content

### User Profile

#### Get Profile
**GET** `/api/user/profile`
- Headers: `Authorization: Bearer <token>`

Response:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "resumeCount": 5,
  "jobDescriptionCount": 3,
  "matchCount": 8
}
```

## 🗄️ Database Schema

### Main Tables

**users**
- id (BIGSERIAL PRIMARY KEY)
- email (VARCHAR UNIQUE)
- name (VARCHAR)
- password (VARCHAR - BCrypt hashed)

**resume**
- id (BIGSERIAL PRIMARY KEY)
- file_name (VARCHAR)
- file_data (BYTEA - Binary data)
- uploaded_by (VARCHAR → users.email)
- upload_time (TIMESTAMP)

**job_descriptions**
- id (BIGSERIAL PRIMARY KEY)
- title (VARCHAR)
- description (TEXT)
- uploaded_by (VARCHAR → users.email)

**match_result**
- id (BIGSERIAL PRIMARY KEY)
- resume_id (BIGINT → resume.id)
- job_description_id (BIGINT → job_descriptions.id)
- match_score (DOUBLE PRECISION)
- extracted_skills (VARCHAR)
- strengths (VARCHAR)
- weaknesses (VARCHAR)
- match_time (TIMESTAMP)
- analysis_id (VARCHAR - for reports)

**otp**
- id (BIGSERIAL PRIMARY KEY)
- email (VARCHAR)
- otp_code (VARCHAR - 6 digits)
- expiry_time (TIMESTAMP)
- verified (BOOLEAN)

## 🔐 Security Features

- **Password Hashing:** BCrypt with salt
- **JWT Tokens:** HS256 algorithm, 24-hour expiration
- **OTP Verification:** 6-digit code, 2-minute expiry
- **CORS:** Configured for localhost:5173
- **Stateless Sessions:** No server-side session storage
- **Protected Routes:** All except `/api/auth/**`

## 🔌 AI Service Integration

Backend communicates with Flask AI service:
```java
// Send resume file + job description to AI service
String AI_SERVICE_URL = "http://localhost:6000/api/analyze";

// Prepare multipart request
MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
body.add("file", fileAsResource);
body.add("jobDescriptionText", jobDescription);

// Call AI service
ResponseEntity<Map> response = restTemplate.exchange(
    AI_SERVICE_URL,
    HttpMethod.POST,
    new HttpEntity<>(body, headers),
    Map.class
);

// Store results in database
```

## 📧 Email OTP System

- **Provider:** Gmail SMTP
- **Format:** 6-digit numeric code
- **Expiry:** 2 minutes
- **One-time use:** Marked as verified after successful validation

Example OTP email:
```
Subject: Resume Analyzer - Your OTP Code

Your OTP code is: 123456
This code will expire in 2 minutes.
```

## 📦 Build & Deploy

### Build JAR
```bash
mvn clean package -DskipTests
```
Output: `target/resume-analyzer-0.0.1-SNAPSHOT.jar`

### Run JAR
```bash
java -jar target/resume-analyzer-0.0.1-SNAPSHOT.jar
```

### Deploy to Render.com
1. Connect GitHub repository
2. Set build command: `mvn clean install`
3. Set start command: `java -jar target/resume-analyzer-0.0.1-SNAPSHOT.jar`
4. Add environment variables (DATABASE_URL, JWT_SECRET, EMAIL credentials)

## 🧪 Testing

### Using cURL

**Signup:**
```bash
curl -X POST http://localhost:8001/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"test123"}'
```

**Login:**
```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

**Upload Resume:**
```bash
curl -X POST http://localhost:8001/api/resume/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@resume.pdf"
```

## 🐛 Troubleshooting

**Database connection failed**
- Verify PostgreSQL is running: `sudo service postgresql status`
- Check credentials in application.properties
- Ensure database exists

**Email not sending**
- Use Gmail App-Specific Password (not regular password)
- Enable 2-factor authentication
- Check spam folder

**JWT token invalid**
- Verify secret key is consistent
- Check token expiration time
- Ensure proper Authorization header format

**File upload fails**
- Check file size (max 10MB)
- Verify file type (PDF or DOCX only)
- Ensure multipart configuration is set