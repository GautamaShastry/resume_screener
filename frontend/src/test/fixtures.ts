import type { AnalysisOut } from "../api/types";

export const analysisFixture: AnalysisOut = {
  id: "a1",
  score: 53,
  created_at: "2026-01-01T00:00:00Z",
  posting: {
    id: "p1",
    title: "Senior Backend Engineer",
    company: "Acme",
    location: "Remote",
    source_url: null,
  },
  resume_version: { id: "v1", resume_id: "r1", version_no: 1, resume_title: "Backend" },
  score_breakdown: {
    coverage: 0.45,
    seniority_fit: 100,
    must_missing_count: 1,
    capped: false,
    years_experience: 8.7,
    weights: { must: 3, nice: 1 },
  },
  requirements: [
    {
      id: "r1",
      text: "5+ years of Python",
      kind: "must",
      category: "experience",
      source_phrase: "5+ years of professional Python experience",
    },
    {
      id: "r2",
      text: "REST APIs",
      kind: "must",
      category: "skill",
      source_phrase: "Experience building REST APIs",
    },
    {
      id: "r3",
      text: "Kubernetes",
      kind: "nice",
      category: "skill",
      source_phrase: "Kubernetes experience is a plus",
    },
  ],
  evidence: [
    {
      requirement_id: "r1",
      status: "met",
      quotes: [{ bullet_id: "b7", text: "Built a Python FastAPI service." }],
      note: "Clear Python work.",
    },
    { requirement_id: "r2", status: "missing", quotes: [], note: "" },
    {
      requirement_id: "r3",
      status: "partial",
      quotes: [{ bullet_id: "b8", text: "Ran Docker in production." }],
      note: "",
    },
  ],
  gaps: [
    {
      requirement_id: "r2",
      type: "not_stated",
      related_bullet_ids: ["b7"],
      related_quotes: [{ bullet_id: "b7", text: "Built a Python FastAPI service." }],
      suggested_bullet: "Built REST APIs with FastAPI.",
      project: null,
    },
    {
      requirement_id: "r3",
      type: "real_gap",
      related_bullet_ids: [],
      related_quotes: [],
      suggested_bullet: null,
      project: {
        title: "Deploy on Kubernetes",
        scope: "Two weeks",
        deliverables: ["Helm chart"],
        resume_bullet: "Deployed a service on Kubernetes.",
      },
    },
  ],
};
