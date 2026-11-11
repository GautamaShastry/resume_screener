import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useApi } from "../api/ApiProvider";
import { unwrap } from "../api/client";
import { errorMessage } from "../api/errors";
import { TaskStepper } from "../components/TaskStepper";
import {
  JobSourceInput,
  emptyJobSource,
  jobSourceError,
  type JobSource,
} from "../features/jobs/JobSourceInput";
import { ResumeVersionSelect } from "../features/resumes/ResumeVersionSelect";
import { useAnalysisRunner } from "../hooks/useAnalysisRunner";
import { useTask } from "../hooks/useTask";

const USAGE_LABELS: Record<string, string> = {
  analysis: "Analyses",
  posting_import: "Job imports",
  resume_upload: "Résumé uploads",
};

function AnalyzeBox() {
  const api = useApi();
  const queryClient = useQueryClient();
  const runner = useAnalysisRunner();
  const { start: startAnalysis, reset: resetRunner } = runner;
  const [source, setSource] = useState<JobSource>(emptyJobSource);
  const [versionId, setVersionId] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [importTaskId, setImportTaskId] = useState<string | null>(null);
  const importTask = useTask(importTaskId);
  const importStatus = importTask.task?.status;
  const importRef = importTask.task?.result_ref;

  useEffect(() => {
    if (importStatus !== "succeeded") return;
    const postingId = (importRef as { posting_id: string }).posting_id;
    void queryClient.invalidateQueries({ queryKey: ["postings"] });
    setImportTaskId(null);
    void startAnalysis(versionId, postingId);
  }, [importStatus, importRef, queryClient, startAnalysis, versionId]);

  const analyze = async () => {
    const invalid = jobSourceError(source) ?? (versionId ? null : "Choose a résumé.");
    if (invalid) return setError(invalid);
    setError(null);
    resetRunner();
    if (source.tab === "saved") return startAnalysis(versionId, source.postingId);
    try {
      const body = source.tab === "url" ? { url: source.url.trim() } : { text: source.text };
      const res = await unwrap(api.POST("/api/postings", { body }));
      setImportTaskId(res.task_id);
    } catch (err) {
      setError(errorMessage(err));
    }
  };

  const busy = Boolean(importTaskId && importStatus !== "failed") || runner.running;
  const shownError = error ?? runner.error;
  return (
    <section className="space-y-4 rounded-lg border bg-white p-5">
      <h1 className="text-2xl font-semibold">Analyze a job</h1>
      <JobSourceInput value={source} onChange={setSource} allowSaved />
      <ResumeVersionSelect value={versionId} onChange={setVersionId} />
      {shownError && (
        <p role="alert" className="text-sm text-red-700">
          {shownError}
        </p>
      )}
      <button
        onClick={analyze}
        disabled={busy}
        className="rounded-md bg-slate-900 px-4 py-2 text-white disabled:opacity-50"
      >
        Analyze
      </button>
      {importTaskId && (
        <TaskStepper
          task={importTask.task}
          error={importTask.error}
          label="Importing job"
          onRetry={() => setImportTaskId(null)}
        />
      )}
      {runner.taskId && (
        <TaskStepper
          task={runner.task}
          error={runner.taskError}
          label="Analyzing"
          onRetry={resetRunner}
        />
      )}
    </section>
  );
}

function RecentAnalyses() {
  const api = useApi();
  const { data } = useQuery({
    queryKey: ["analyses", { limit: 5 }],
    queryFn: () => unwrap(api.GET("/api/analyses", { params: { query: { limit: 5 } } })),
  });
  if (!data?.length) return null;
  return (
    <section className="rounded-lg border bg-white p-5">
      <h2 className="text-lg font-semibold">Recent analyses</h2>
      <ul className="mt-2 divide-y">
        {data.map((a) => (
          <li key={a.id}>
            <Link to={`/analyses/${a.id}`} className="flex justify-between py-2 hover:underline">
              <span>
                {a.posting.title || "Untitled job"} · {a.resume_version.resume_title} v
                {a.resume_version.version_no}
              </span>
              <span className="font-semibold">{a.score}</span>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}

function UsageSummary() {
  const api = useApi();
  const { data } = useQuery({
    queryKey: ["usage"],
    queryFn: () => unwrap(api.GET("/api/me/usage")),
  });
  if (!data) return null;
  return (
    <section className="rounded-lg border bg-white p-5 text-sm">
      <h2 className="text-lg font-semibold">Today</h2>
      <ul className="mt-2 space-y-1">
        {Object.entries(USAGE_LABELS).map(([kind, label]) =>
          data.items[kind] ? (
            <li key={kind}>
              {label}: {data.items[kind].used} / {data.items[kind].limit}
            </li>
          ) : null,
        )}
      </ul>
    </section>
  );
}

export function HomePage() {
  return (
    <div className="grid gap-4 lg:grid-cols-[2fr_1fr]">
      <AnalyzeBox />
      <div className="space-y-4">
        <UsageSummary />
        <RecentAnalyses />
      </div>
    </div>
  );
}
