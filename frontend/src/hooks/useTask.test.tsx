import { fetchEventSource } from "@microsoft/fetch-event-source";
import { renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { DEV_EMAIL_KEY, DevAuthProvider } from "../auth/AuthProvider";
import { useTask } from "./useTask";

vi.mock("@microsoft/fetch-event-source", () => ({ fetchEventSource: vi.fn() }));

const wrapper = ({ children }: { children: ReactNode }) => (
  <DevAuthProvider>{children}</DevAuthProvider>
);

test("streams progress then final state with the bearer token", async () => {
  localStorage.setItem(DEV_EMAIL_KEY, "me@example.com");
  const running = { id: "t1", status: "running", progress: { step: "A", steps: ["A"] } };
  const done = { ...running, status: "succeeded", result_ref: { analysis_id: "a1" } };
  vi.mocked(fetchEventSource).mockImplementation(async (url, opts) => {
    expect(String(url)).toBe("http://localhost:8000/api/tasks/t1/events");
    expect((opts.headers as Record<string, string>).Authorization).toBe(
      "Bearer dev:me@example.com",
    );
    await opts.onopen?.(new Response(null, { status: 200 }));
    opts.onmessage?.({ event: "progress", data: JSON.stringify(running), id: "" });
    opts.onmessage?.({ event: "done", data: JSON.stringify(done), id: "" });
  });
  const { result } = renderHook(() => useTask("t1"), { wrapper });
  await waitFor(() => expect(result.current.task?.status).toBe("succeeded"));
});

test("no task id does nothing", () => {
  vi.mocked(fetchEventSource).mockClear();
  renderHook(() => useTask(null), { wrapper });
  expect(fetchEventSource).not.toHaveBeenCalled();
});

test("a stream that closes before a final event reconnects instead of hanging", async () => {
  localStorage.setItem(DEV_EMAIL_KEY, "me@example.com");
  let closeError: unknown = null;
  let retryOutcome: unknown = "not-called";
  vi.mocked(fetchEventSource).mockImplementation(async (_url, opts) => {
    try {
      opts.onclose?.();
    } catch (err) {
      closeError = err;
    }
    try {
      retryOutcome = opts.onerror?.(closeError);
    } catch {
      retryOutcome = "threw";
    }
  });
  const { result } = renderHook(() => useTask("t2"), { wrapper });
  await waitFor(() => expect(retryOutcome).not.toBe("not-called"));
  expect(closeError).toBeInstanceOf(Error); // onclose must signal "retry"
  expect(retryOutcome).not.toBe("threw"); // and onerror must allow the retry
  expect(result.current.error).toBeNull();
});
