import type { TaskOut } from "../api/types";

interface Props {
  task: TaskOut | null;
  error?: string | null;
  onRetry?: () => void;
  label?: string;
}

export function TaskStepper({ task, error, onRetry, label }: Props) {
  const failedMessage =
    error ?? (task?.status === "failed" ? (task.error_message ?? "Something went wrong.") : null);
  if (failedMessage) {
    return (
      <div role="alert" className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-800">
        <p>{failedMessage}</p>
        {onRetry && (
          <button onClick={onRetry} className="mt-2 font-medium underline">
            Retry
          </button>
        )}
      </div>
    );
  }
  const progress = (task?.progress ?? {}) as { step?: unknown; steps?: unknown };
  const steps = Array.isArray(progress.steps) ? (progress.steps as string[]) : [];
  const current = typeof progress.step === "string" ? steps.indexOf(progress.step) : -1;
  const allDone = task?.status === "succeeded";
  return (
    <div aria-live="polite" className="rounded-md border bg-white p-3">
      {label && <p className="mb-2 text-sm font-medium">{label}</p>}
      {(!task || task.status === "queued") && (
        <p className="text-sm text-slate-600">Waiting to start…</p>
      )}
      <ol className="space-y-1">
        {steps.map((step, i) => {
          const state = allDone || i < current ? "done" : i === current ? "active" : "pending";
          return (
            <li key={step} className="flex items-center gap-2 text-sm">
              <span aria-hidden className="w-4 text-center">
                {state === "done" ? "✓" : state === "active" ? "…" : "○"}
              </span>
              <span className={state === "pending" ? "text-slate-500" : ""}>{step}</span>
              <span className="sr-only">
                {state === "done" ? "(done)" : state === "active" ? "(in progress)" : "(pending)"}
              </span>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
