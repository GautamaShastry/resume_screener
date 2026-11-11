import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { analysisFixture as a } from "../../test/fixtures";
import { GapsPanel } from "./GapsPanel";
import { RequirementsTable } from "./RequirementsTable";
import { ScoreHeader } from "./ScoreHeader";

test("score header explains missing must-haves and the cap", () => {
  const { rerender } = render(<ScoreHeader analysis={a} />);
  expect(screen.getByRole("heading", { name: "Match score: 53" })).toBeInTheDocument();
  expect(screen.getByText("1 must-have requirement is missing.")).toBeInTheDocument();
  rerender(
    <ScoreHeader
      analysis={{ ...a, score: 75, score_breakdown: { ...a.score_breakdown, capped: true } }}
    />,
  );
  expect(
    screen.getByText("Score capped at 75 because 1 must-have requirement is missing."),
  ).toBeInTheDocument();
});

test("requirements table filters and expands evidence", async () => {
  render(<RequirementsTable requirements={a.requirements} evidence={a.evidence} />);
  const table = screen.getByRole("table", { name: "Requirements" });
  expect(within(table).getAllByRole("row")).toHaveLength(4); // header + 3
  await userEvent.selectOptions(screen.getByLabelText("Status"), "missing");
  expect(within(table).getAllByRole("row")).toHaveLength(2);
  await userEvent.selectOptions(screen.getByLabelText("Status"), "all");
  const toggle = screen.getByRole("button", { name: "5+ years of Python" });
  await userEvent.click(toggle);
  expect(toggle).toHaveAttribute("aria-expanded", "true");
  expect(screen.getByText("“Built a Python FastAPI service.”")).toBeInTheDocument();
  expect(screen.getByText(/From the posting/)).toHaveTextContent(
    "5+ years of professional Python experience",
  );
});

test("gaps panel shows suggested bullet with a truth reminder and the project", () => {
  render(<GapsPanel gaps={a.gaps} requirements={a.requirements} />);
  expect(screen.getByText("Built REST APIs with FastAPI.")).toBeInTheDocument();
  expect(screen.getByText("Only add this if it's true.")).toBeInTheDocument();
  expect(screen.getByText("Deploy on Kubernetes")).toBeInTheDocument();
});
