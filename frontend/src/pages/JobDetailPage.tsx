import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useApi } from "../api/ApiProvider";
import { unwrap } from "../api/client";
import { errorMessage } from "../api/errors";
import { ConfirmDialog } from "../components/ConfirmDialog";
import { TaskStepper } from "../components/TaskStepper";
import { ResumeVersionSelect } from "../features/resumes/ResumeVersionSelect";
import { useAnalysisRunner } from "../hooks/useAnalysisRunner";

export function JobDetailPage() {
  const { postingId = "" } = useParams();
  const api = useApi();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const runner = useAnalysisRunner();
  const [versionId, setVersionId] = useState("");
  const {
    data: p,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["posting", postingId],
    queryFn: () =>
      unwrap(api.GET("/api/postings/{posting_id}", { params: { path: { posting_id: postingId } } })),
  });
  if (isLoading) return <p>Loading…</p>;
  if (error || !p) return <p role="alert">{errorMessage(error)}</p>;
  const must = p.requirements.filter((r) => r.kind === "must");
  const nice = p.requirements.filter((r) => r.kind === "nice");
  return (
    <article className="space-y-4">
      <header className="flex flex-wrap items-start gap-3">
        <div>
          <h1 className="text-2xl font-semibold">{p.title || "Untitled job"}</h1>
          <p className="text-slate-600">{[p.company, p.location].filter(Boolean).join(" · ")}</p>
          {p.source_url && (
            <a href={p.source_url} target="_blank" rel="noreferrer" className="text-sm underline">
              View original posting
            </a>
          )}
        </div>
        <div className="ml-auto">
          <ConfirmDialog
            trigger="Delete"
            title="Delete this job?"
            description="Its analyses will be deleted too."
            confirmLabel="Delete job"
            onConfirm={async () => {
              await unwrap(
                api.DELETE("/api/postings/{posting_id}", {
                  params: { path: { posting_id: postingId } },
                }),
              );
              await queryClient.invalidateQueries({ queryKey: ["postings"] });
              navigate("/jobs");
            }}
          />
        </div>
      </header>
      <section className="space-y-3 rounded-lg border bg-white p-4">
        <h2 className="text-lg font-semibold">Analyze against a résumé</h2>
        <ResumeVersionSelect value={versionId} onChange={setVersionId} />
        <button
          disabled={!versionId || runner.running || p.requirements.length === 0}
          onClick={() => runner.start(versionId, p.id)}
          className="rounded-md bg-slate-900 px-3 py-2 text-sm text-white disabled:opacity-50"
        >
          Analyze
        </button>
        {p.requirements.length === 0 && (
          <p className="text-sm text-slate-700">
            We couldn't find requirements in this posting, so it can't be analyzed.
          </p>
        )}
        {runner.error && (
          <p role="alert" className="text-sm text-red-700">
            {runner.error}
          </p>
        )}
        {runner.taskId && (
          <TaskStepper
            task={runner.task}
            error={runner.taskError}
            label="Analyzing"
            onRetry={runner.reset}
          />
        )}
      </section>
      {[
        { title: "Must-have", items: must },
        { title: "Nice-to-have", items: nice },
      ].map((group) => (
        <section key={group.title} className="rounded-lg border bg-white p-4">
          <h2 className="text-lg font-semibold">
            {group.title} ({group.items.length})
          </h2>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm">
            {group.items.map((r) => (
              <li key={r.id}>{r.text}</li>
            ))}
          </ul>
        </section>
      ))}
    </article>
  );
}
