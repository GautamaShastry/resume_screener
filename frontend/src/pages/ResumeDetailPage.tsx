import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { useApi } from "../api/ApiProvider";
import { unwrap } from "../api/client";
import { errorMessage } from "../api/errors";
import { downloadFile } from "../api/raw";
import type { AtsReport, StructuredResume } from "../api/types";
import { useAuth } from "../auth/AuthProvider";
import { ConfirmDialog } from "../components/ConfirmDialog";
import { StatusBadge } from "../components/StatusBadge";
import { useToast } from "../components/Toaster";
import { AtsReportView } from "../features/resumes/AtsReportView";
import { StructuredResumeView } from "../features/resumes/StructuredResumeView";
import { UploadResumeDialog } from "../features/resumes/UploadResumeDialog";

export function ResumeDetailPage() {
  const { resumeId = "" } = useParams();
  const [params, setParams] = useSearchParams();
  const api = useApi();
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const toast = useToast();

  const resumeQ = useQuery({
    queryKey: ["resume", resumeId],
    queryFn: () =>
      unwrap(api.GET("/api/resumes/{resume_id}", { params: { path: { resume_id: resumeId } } })),
  });
  const versions = resumeQ.data?.versions ?? [];
  const versionId = params.get("version") ?? versions[versions.length - 1]?.id;
  const versionQ = useQuery({
    queryKey: ["version", versionId],
    enabled: Boolean(versionId),
    queryFn: () =>
      unwrap(
        api.GET("/api/resume-versions/{version_id}", {
          params: { path: { version_id: versionId! } },
        }),
      ),
    refetchInterval: (q) => (q.state.data?.parse_status === "pending" ? 2000 : false),
  });

  if (resumeQ.isLoading) return <p>Loading…</p>;
  if (resumeQ.error || !resumeQ.data) return <p role="alert">{errorMessage(resumeQ.error)}</p>;
  const resume = resumeQ.data;
  const version = versionQ.data;

  const setArchived = async (archived: boolean) => {
    await unwrap(
      api.PATCH("/api/resumes/{resume_id}", {
        params: { path: { resume_id: resumeId } },
        body: { archived },
      }),
    );
    await queryClient.invalidateQueries({ queryKey: ["resume", resumeId] });
    await queryClient.invalidateQueries({ queryKey: ["resumes"] });
  };

  return (
    <article className="space-y-4">
      <header className="flex flex-wrap items-center gap-3">
        <h1 className="text-2xl font-semibold">{resume.title}</h1>
        {version && <StatusBadge status={version.parse_status} />}
        <div className="ml-auto flex flex-wrap items-center gap-2">
          <label className="text-sm">
            Version{" "}
            <select
              value={versionId ?? ""}
              onChange={(e) => setParams({ version: e.target.value })}
              className="rounded-md border px-2 py-1"
            >
              {versions.map((v) => (
                <option key={v.id} value={v.id}>
                  v{v.version_no} ({v.source})
                </option>
              ))}
            </select>
          </label>
          {version && (
            <button
              className="rounded-md border px-3 py-1.5 text-sm"
              onClick={() =>
                downloadFile(
                  getToken,
                  `/api/resume-versions/${version.id}/download`,
                  `${resume.title}-v${version.version_no}.${version.file_type}`,
                ).catch((err) => toast({ kind: "error", message: errorMessage(err) }))
              }
            >
              Download original
            </button>
          )}
          <UploadResumeDialog trigger="Upload new version" resumeId={resumeId} />
          <button
            className="rounded-md border px-3 py-1.5 text-sm"
            onClick={() => setArchived(!resume.archived)}
          >
            {resume.archived ? "Unarchive" : "Archive"}
          </button>
          <ConfirmDialog
            trigger="Delete"
            title="Delete this résumé?"
            description="All versions and their analyses will be permanently deleted."
            confirmLabel="Delete résumé"
            onConfirm={async () => {
              await unwrap(
                api.DELETE("/api/resumes/{resume_id}", {
                  params: { path: { resume_id: resumeId } },
                }),
              );
              await queryClient.invalidateQueries({ queryKey: ["resumes"] });
              navigate("/resumes");
            }}
          />
        </div>
      </header>
      {versionQ.isLoading && <p>Loading version…</p>}
      {version?.parse_status === "pending" && (
        <p className="text-slate-600">
          Processing this version… this usually takes under a minute.
        </p>
      )}
      {version?.parse_status === "failed" && (
        <p role="alert" className="text-red-700">
          We couldn't process this file. Upload it again.
        </p>
      )}
      {version?.parse_status === "ready" && version.ats_report && (
        <>
          <AtsReportView report={version.ats_report as unknown as AtsReport} />
          {version.structured ? (
            <StructuredResumeView structured={version.structured as unknown as StructuredResume} />
          ) : (
            <p className="text-slate-700">
              We couldn't read text from this file, so it can't be analyzed. Upload a text-based
              PDF or DOCX.
            </p>
          )}
        </>
      )}
    </article>
  );
}
