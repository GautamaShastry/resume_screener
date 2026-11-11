import type { components } from "./schema";

type S = components["schemas"];
export type TaskOut = S["TaskOut"];
export type ResumeOut = S["ResumeOut"];
export type VersionOut = S["VersionOut"];
export type UploadOut = S["UploadOut"];
export type PostingSummary = S["PostingSummary"];
export type PostingOut = S["PostingOut"];
export type AnalysisOut = S["AnalysisOut"];
export type AnalysisSummary = S["AnalysisSummary"];
export type EvidenceItem = S["EvidenceItem"];
export type GapItem = S["GapItem"];
export type Requirement = S["Requirement"];
export type UsageOut = S["UsageOut"];
export type MeOut = S["MeOut"];

export interface AtsCheck {
  check: string;
  severity: "error" | "warning" | "info";
  message: string;
  how_to_fix: string;
}
export interface AtsReport {
  checks: AtsCheck[];
  parsed_view: {
    text: string;
    fields: { name: string | null; email: string | null; phone: string | null; sections: string[] };
  };
}
export interface StructuredResume {
  contact: { name: string; email: string; phone: string; location: string; links: string[] };
  summary: { id: string; text: string } | null;
  skills: { id: string; text: string }[];
  sections: {
    id: string;
    kind: string;
    title: string;
    entries: {
      id: string;
      org: string;
      role: string;
      start: string;
      end: string;
      location: string;
      bullets: { id: string; text: string }[];
    }[];
  }[];
}
