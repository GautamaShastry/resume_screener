import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useApi } from "../api/ApiProvider";
import { unwrap } from "../api/client";
import { errorMessage } from "../api/errors";
import { useTaskNotifier } from "../components/TaskNotifier";
import { useTask } from "./useTask";

const analysisHref = (ref: unknown) =>
  `/analyses/${(ref as { analysis_id: string }).analysis_id}`;

export function useAnalysisRunner() {
  const api = useApi();
  const navigate = useNavigate();
  const notifier = useTaskNotifier();
  const [taskId, setTaskId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { task, error: taskError } = useTask(taskId);

  useEffect(() => {
    if (task?.status === "succeeded") navigate(analysisHref(task.result_ref));
  }, [task?.status, task?.result_ref, navigate]);

  const start = useCallback(
    async (versionId: string, postingId: string, force = false) => {
      setError(null);
      try {
        const res = await unwrap(
          api.POST("/api/analyses", {
            body: { resume_version_id: versionId, posting_id: postingId, force },
          }),
        );
        if (res.analysis_id) {
          navigate(`/analyses/${res.analysis_id}`);
        } else if (res.task_id) {
          setTaskId(res.task_id);
          notifier.watch({
            id: res.task_id,
            label: "Analysis",
            href: (t) => analysisHref(t.result_ref),
          });
        }
      } catch (err) {
        setError(errorMessage(err));
      }
    },
    [api, navigate, notifier],
  );

  const reset = useCallback(() => {
    setTaskId(null);
    setError(null);
  }, []);

  return {
    start,
    task,
    taskError,
    error,
    running: Boolean(taskId) && task?.status !== "failed",
    reset,
    taskId,
  };
}
