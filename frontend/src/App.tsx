import { Route, Routes } from "react-router-dom";
import { RequireAuth } from "./auth/RequireAuth";
import { Layout } from "./components/Layout";
import { AnalysisPage } from "./pages/AnalysisPage";
import { HomePage } from "./pages/HomePage";
import { JobDetailPage } from "./pages/JobDetailPage";
import { JobsPage } from "./pages/JobsPage";
import { LandingPage } from "./pages/LandingPage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { ResumeDetailPage } from "./pages/ResumeDetailPage";
import { ResumesPage } from "./pages/ResumesPage";
import { SettingsPage } from "./pages/SettingsPage";

export function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route
        element={
          <RequireAuth>
            <Layout />
          </RequireAuth>
        }
      >
        <Route path="/home" element={<HomePage />} />
        <Route path="/resumes" element={<ResumesPage />} />
        <Route path="/resumes/:resumeId" element={<ResumeDetailPage />} />
        <Route path="/jobs" element={<JobsPage />} />
        <Route path="/jobs/:postingId" element={<JobDetailPage />} />
        <Route path="/analyses/:analysisId" element={<AnalysisPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
