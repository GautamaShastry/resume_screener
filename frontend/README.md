# 🎨 Frontend - Resume Analyzer

Modern React application built with **Vite** and **Tailwind CSS** providing an intuitive interface for AI-powered resume analysis.

## 📁 Project Structure
```
frontend/
├── src/
│   ├── components/
│   │   ├── Dashboard.jsx          # Main dashboard with stats
│   │   ├── LoginForm.jsx           # Login with OTP
│   │   ├── SignupForm.jsx          # User registration
│   │   ├── OtpVerification.jsx     # OTP input component
│   │   ├── UploadResumePage.jsx    # Drag & drop upload
│   │   ├── UploadJobPage.jsx       # Job description form
│   │   ├── MatchResumePage.jsx     # Pre-match confirmation
│   │   ├── ResultPage.jsx          # Analysis results with charts
│   │   ├── MatchHistory.jsx        # Past matches
│   │   ├── Navbar.jsx              # Navigation
│   │   └── Loading.jsx             # Loading spinner
│   ├── App.jsx                     # Main app with routing
│   ├── main.jsx                    # React entry point
│   └── index.css                   # Tailwind imports
├── package.json
└── vite.config.js
```

## 🛠️ Tech Stack

- **React 18.2.0** - UI library
- **Vite** - Build tool & dev server
- **Tailwind CSS 3.x** - Utility-first styling
- **React Router 6.x** - Client-side routing
- **Axios** - HTTP client
- **Chart.js** - Data visualization
- **React Toastify** - Toast notifications
- **React Icons** - Feather icons

## 🚀 Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
# Runs on http://localhost:5173

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🛣️ Routes

| Route | Component | Protected | Description |
|-------|-----------|-----------|-------------|
| `/` | Redirect | No | Home redirect |
| `/signup` | SignupForm | No | User registration |
| `/login` | LoginForm | No | Login + OTP |
| `/dashboard` | Dashboard | Yes | Main dashboard |
| `/upload-resume` | UploadResumePage | Yes | Upload resume |
| `/upload-job` | UploadJobPage | Yes | Add job description |
| `/match` | MatchResumePage | Yes | Confirm analysis |
| `/result` | ResultPage | Yes | View results |
| `/history` | MatchHistory | Yes | Match history |

## ✨ Key Features

### 🔐 Authentication
- JWT-based authentication with localStorage
- OTP email verification (6-digit code)
- Auto-focus OTP inputs with paste support
- 2-minute countdown timer with resend option

### 📤 File Upload
- Drag & drop interface
- File validation (PDF/DOCX only, max 5MB)
- Visual feedback and file preview
- Remove file option before upload

### 📊 Dashboard
- User statistics (resumes, jobs, matches)
- Animated progress bars
- Quick action cards with gradients
- Feature highlights and success stories

### 📈 Results Visualization
- Pie chart (match vs mismatch percentages)
- Color-coded scores (green/yellow/red)
- Detailed strengths and weaknesses lists
- ATS recommendations preview
- Career advice display
- Download PDF/HTML reports

### 📜 Match History
- Filterable list (All/High/Medium/Low scores)
- Score badges with color coding
- Job title and resume information
- Quick access to past reports
- Formatted timestamps

## 🎨 Design System

### Color Palette
```css
/* Primary Colors */
--blue-600: #2563eb     /* Primary actions */
--purple-600: #7c3aed   /* Secondary actions */

/* Status Colors */
--green-600: #10b981    /* Success, high scores */
--yellow-600: #f59e0b   /* Warning, medium scores */
--red-600: #ef4444      /* Error, low scores */

/* Neutrals */
--gray-100: #f3f4f6     /* Backgrounds */
--gray-600: #4b5563     /* Text */
```

### Score Colors
- **80-100%** → Green (Excellent match)
- **60-79%** → Yellow (Good match)
- **<60%** → Red (Needs improvement)

## 🔌 API Integration

Backend URL: `http://localhost:8001`

All authenticated requests include:
```javascript
headers: {
  'Authorization': `Bearer ${localStorage.getItem('token')}`
}
```

### Endpoints Used
- `POST /api/auth/signup` - Register
- `POST /api/auth/login` - Login
- `POST /api/auth/verify` - Verify OTP
- `POST /api/resume/upload` - Upload resume
- `POST /api/job/upload` - Add job
- `POST /api/match/matchResume` - Analyze
- `GET /api/match/history` - Get history
- `GET /api/report/pdf/{id}` - Download PDF
- `GET /api/report/html/{id}` - View HTML

## 💾 State Management

- **useState** - Component state
- **useEffect** - Side effects & data fetching
- **useNavigate** - Programmatic navigation
- **useLocation** - Route state
- **localStorage** - JWT token & IDs persistence

## 📦 Deployment

### Vercel (Recommended)
```bash
npm run build
vercel --prod
```

### Environment Variables
```env
VITE_API_URL=https://your-backend-url.com
```

### Netlify
```bash
npm run build
# Deploy dist/ folder
```

Create `public/_redirects`:
```
/*  /index.html  200
```

## 🐛 Troubleshooting

**Issue:** Cannot connect to backend  
**Solution:** Check backend is running on port 8001, verify CORS configuration

**Issue:** OTP not received  
**Solution:** Check email configuration in backend, verify spam folder

**Issue:** Charts not displaying  
**Solution:** Ensure Chart.js is installed: `npm install chart.js react-chartjs-2`