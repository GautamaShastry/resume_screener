import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { useApi } from "../api/ApiProvider";
import { unwrap } from "../api/client";
import { errorMessage } from "../api/errors";
import { ErrorBoundary } from "../components/ErrorBoundary";
import { TaskStepper } from "../components/TaskStepper";
import { GapsPanel } from "../features/analysis/GapsPanel";
import { RequirementsTable } from "../features/analysis/RequirementsTable";
import { ScoreHeader } from "../features/analysis/ScoreHeader";
import { useAnalysisRunner } from "../hooks/useAnalysisRunner";

export function AnalysisPage() {
  const { analysisId = "" } = useParams();
  const api = useApi();
  const runner = useAnalysisRunner();
  const {
    data: a,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["analysis", analysisId],
    queryFn: () =>
      unwrap(
        api.GET("/api/analyses/{analysis_id}", { params: { path: { analysis_id: analysisId } } }),
      ),
  });
  if (isLoading) return <p>Loading…</p>;
  if (error || !a) return <p role="alert">{errorMessage(error)}</p>;
  return (
    <article className="space-y-4">
      <ScoreHeader analysis={a} />
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => runner.start(a.resume_version.id, a.posting.id, true)}
          disabled={runner.running}
          className="rounded-md border px-3 py-1.5 text-sm disabled:opacity-50"
        >
          Re-run analysis
        </button>
      </div>
      {runner.error && (
        <p role="alert" className="text-sm text-red-700">
          {runner.error}
        </p>
      )}
      {runner.taskId && (
        <TaskStepper
          task={runner.task}
          error={runner.taskError}
          label="Re-running analysis"
          onRetry={runner.reset}
        />
      )}
      <ErrorBoundary>
        <RequirementsTable requirements={a.requirements} evidence={a.evidence} />
      </ErrorBoundary>
      <ErrorBoundary>
        <GapsPanel gaps={a.gaps} requirements={a.requirements} />
      </ErrorBoundary>
    </article>
  );
}
