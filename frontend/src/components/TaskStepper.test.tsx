import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { TaskOut } from "../api/types";
import { TaskStepper } from "./TaskStepper";

const base: TaskOut = {
  id: "t1",
  type: "analysis.run",
  status: "running",
  progress: {
    step: "Scoring",
    steps: ["Matching requirements", "Checking seniority", "Scoring", "Finding gaps"],
    percent: 50,
  },
  result_ref: null,
  error_code: null,
  error_message: null,
  created_at: "2026-01-01T00:00:00Z",
};

test("marks steps done, active, and pending", () => {
  render(<TaskStepper task={base} />);
  expect(screen.getByText("Matching requirements").parentElement).toHaveTextContent("(done)");
  expect(screen.getByText("Scoring").parentElement).toHaveTextContent("(in progress)");
  expect(screen.getByText("Finding gaps").parentElement).toHaveTextContent("(pending)");
});

test("queued task shows waiting message", () => {
  render(<TaskStepper task={{ ...base, status: "queued", progress: {} }} />);
  expect(screen.getByText("Waiting to start…")).toBeInTheDocument();
});

test("failed task shows message and retry", async () => {
  const onRetry = vi.fn();
  render(
    <TaskStepper
      task={{ ...base, status: "failed", error_message: "The page returned HTTP 404." }}
      onRetry={onRetry}
    />,
  );
  expect(screen.getByRole("alert")).toHaveTextContent("HTTP 404");
  await userEvent.click(screen.getByRole("button", { name: "Retry" }));
  expect(onRetry).toHaveBeenCalled();
});
