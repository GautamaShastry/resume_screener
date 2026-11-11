import { fetchEventSource } from "@microsoft/fetch-event-source";
import { useEffect, useState } from "react";
import type { TaskOut } from "../api/types";
import { useAuth } from "../auth/AuthProvider";
import { config } from "../config";

class FatalStreamError extends Error {}

export function useTask(taskId: string | null | undefined) {
  const { getToken } = useAuth();
  const [task, setTask] = useState<TaskOut | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setTask(null);
    setError(null);
    if (!taskId) return;
    const controller = new AbortController();
    let failures = 0;
    (async () => {
      const token = await getToken();
      await fetchEventSource(`${config.apiBaseUrl}/api/tasks/${taskId}/events`, {
        headers: { Authorization: `Bearer ${token}` },
        signal: controller.signal,
        openWhenHidden: true,
        async onopen(response) {
          if (!response.ok) throw new FatalStreamError(`HTTP ${response.status}`);
        },
        onmessage(ev) {
          if (!ev.data) return;
          setTask(JSON.parse(ev.data) as TaskOut);
          if (ev.event === "done" || ev.event === "failed") controller.abort();
        },
        onerror(err) {
          failures += 1;
          if (err instanceof FatalStreamError || failures > 3) {
            setError("Lost connection to the server. Refresh to check the result.");
            throw err;
          }
        },
      });
    })().catch(() => {
      /* error state already set */
    });
    return () => controller.abort();
  }, [taskId, getToken]);

  return { task, error };
}
