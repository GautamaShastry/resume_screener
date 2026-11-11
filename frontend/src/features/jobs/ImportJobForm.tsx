import { useEffect, useState, type FormEvent } from "react";
import { useApi } from "../../api/ApiProvider";
import { ApiError, unwrap } from "../../api/client";
import { errorMessage } from "../../api/errors";
import { useTaskNotifier } from "../../components/TaskNotifier";
import { TaskStepper } from "../../components/TaskStepper";
import { useTask } from "../../hooks/useTask";
import { JobSourceInput, emptyJobSource, jobSourceError, type JobSource } from "./JobSourceInput";

export function ImportJobForm({ onImported }: { onImported: (postingId: string) => void }) {
  const api = useApi();
  const notifier = useTaskNotifier();
  const [source, setSource] = useState<JobSource>(emptyJobSource);
  const [error, setError] = useState<string | null>(null);
  const [taskId, setTaskId] = useState<string | null>(null);
  const { task, error: streamError } = useTask(taskId);

  useEffect(() => {
    if (task?.status === "succeeded") {
      onImported((task.result_ref as { posting_id: string }).posting_id);
    }
  }, [task?.status, task?.result_ref, onImported]);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    const invalid = jobSourceError(source);
    if (invalid) return setError(invalid);
    setError(null);
    try {
      const body = source.tab === "url" ? { url: source.url.trim() } : { text: source.text };
      const res = await unwrap(api.POST("/api/postings", { body }));
      setTaskId(res.task_id);
      notifier.watch({
        id: res.task_id,
        label: "Job import",
        href: (t) => `/jobs/${(t.result_ref as { posting_id: string }).posting_id}`,
      });
    } catch (err) {
      if (err instanceof ApiError && err.code === "UNSUPPORTED_SOURCE") {
        setSource((s) => ({ ...s, tab: "paste" }));
      }
      setError(errorMessage(err));
    }
  };

  if (taskId) {
    return (
      <TaskStepper
        task={task}
        error={streamError}
        label="Importing job"
        onRetry={() => setTaskId(null)}
      />
    );
  }
  return (
    <form onSubmit={submit} className="space-y-3" noValidate>
      <JobSourceInput value={source} onChange={setSource} />
      {error && (
        <p role="alert" className="text-sm text-red-700">
          {error}
        </p>
      )}
      <button type="submit" className="rounded-md bg-slate-900 px-3 py-2 text-sm text-white">
        Import job
      </button>
    </form>
  );
}
