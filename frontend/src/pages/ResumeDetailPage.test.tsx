import { screen } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { renderWithProviders } from "../test/render";
import { API, server } from "../test/server";
import { ResumeDetailPage } from "./ResumeDetailPage";

const version = {
  id: "v1",
  resume_id: "r1",
  version_no: 1,
  source: "upload",
  file_type: "pdf",
  parse_status: "ready",
  created_at: "2026-01-01T00:00:00Z",
  structured: {
    contact: { name: "Jane", email: "", phone: "", location: "", links: [] },
    summary: null,
    skills: [{ id: "b1", text: "Python" }],
    sections: [],
  },
  ats_report: {
    checks: [],
    parsed_view: {
      text: "Jane",
      fields: { name: "Jane", email: null, phone: null, sections: [] },
    },
  },
};

function resume(v: object) {
  return {
    id: "r1",
    title: "Backend",
    archived: false,
    created_at: version.created_at,
    versions: [v],
  };
}

test("shows the ATS check for the latest version", async () => {
  server.use(
    http.get(`${API}/api/resumes/r1`, () => HttpResponse.json(resume(version))),
    http.get(`${API}/api/resume-versions/v1`, () => HttpResponse.json(version)),
  );
  renderWithProviders(<ResumeDetailPage />, { route: "/resumes/r1", path: "/resumes/:resumeId" });
  expect(await screen.findByRole("heading", { name: "Backend" })).toBeInTheDocument();
  expect(await screen.findByRole("heading", { name: "ATS check" })).toBeInTheDocument();
  expect(screen.getByText("Python")).toBeInTheDocument();
});

test("shows processing state for pending versions", async () => {
  const pending = { ...version, parse_status: "pending", structured: null, ats_report: null };
  server.use(
    http.get(`${API}/api/resumes/r1`, () => HttpResponse.json(resume(pending))),
    http.get(`${API}/api/resume-versions/v1`, () => HttpResponse.json(pending)),
  );
  renderWithProviders(<ResumeDetailPage />, { route: "/resumes/r1", path: "/resumes/:resumeId" });
  expect(await screen.findByText(/Processing this version/)).toBeInTheDocument();
});
