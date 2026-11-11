import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { renderWithProviders } from "../../test/render";
import { API, server } from "../../test/server";
import { ImportJobForm } from "./ImportJobForm";

test("unsupported site switches to paste mode with an explanation", async () => {
  server.use(
    http.post(`${API}/api/postings`, () =>
      HttpResponse.json(
        {
          code: "UNSUPPORTED_SOURCE",
          message: "We can't import from this site. Paste the job description instead.",
          details: {},
        },
        { status: 422 },
      ),
    ),
  );
  renderWithProviders(<ImportJobForm onImported={() => {}} />);
  await userEvent.type(
    screen.getByLabelText("Job posting URL"),
    "https://www.linkedin.com/jobs/view/1",
  );
  await userEvent.click(screen.getByRole("button", { name: "Import job" }));
  expect(await screen.findByRole("alert")).toHaveTextContent(
    "Paste the job description instead",
  );
  expect(screen.getByRole("tab", { name: "Paste text" })).toHaveAttribute("aria-selected", "true");
  expect(screen.getByLabelText("Job description")).toBeInTheDocument();
});
