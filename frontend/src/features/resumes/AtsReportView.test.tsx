import { render, screen, within } from "@testing-library/react";
import type { AtsReport } from "../../api/types";
import { AtsReportView } from "./AtsReportView";

const report: AtsReport = {
  checks: [
    {
      check: "multi_column",
      severity: "warning",
      message: "This résumé uses a multi-column layout.",
      how_to_fix: "Use a single column.",
    },
    {
      check: "missing_contact",
      severity: "error",
      message: "No phone found.",
      how_to_fix: "Add your phone number.",
    },
  ],
  parsed_view: {
    text: "Jane Doe\nEXPERIENCE",
    fields: { name: "Jane Doe", email: "jane@example.com", phone: null, sections: ["experience"] },
  },
};

test("lists issues by severity with text labels and shows the parsed view", () => {
  render(<AtsReportView report={report} />);
  const issues = within(screen.getByRole("region", { name: "ATS check" })).getAllByRole(
    "listitem",
  );
  expect(issues[0]).toHaveTextContent("Error");
  expect(issues[0]).toHaveTextContent("No phone found.");
  expect(issues[1]).toHaveTextContent("Warning");
  const panel = screen.getByRole("region", { name: "What an ATS sees" });
  expect(within(panel).getByText("jane@example.com")).toBeInTheDocument();
  expect(within(panel).getByText("Not found")).toBeInTheDocument();
});

test("no issues message", () => {
  render(<AtsReportView report={{ ...report, checks: [] }} />);
  expect(screen.getByText("No issues found.")).toBeInTheDocument();
});
