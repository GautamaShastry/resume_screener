import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { renderWithProviders } from "../test/render";
import { API, server } from "../test/server";
import { HomePage } from "./HomePage";

const now = "2026-01-01T00:00:00Z";

test("analyzing a saved job with a cached result navigates straight to it", async () => {
  let body: unknown;
  server.use(
    http.get(`${API}/api/resumes`, () =>
      HttpResponse.json([
        {
          id: "r1",
          title: "Backend",
          archived: false,
          created_at: now,
          versions: [
            {
              id: "v1",
              version_no: 1,
              source: "upload",
              file_type: "pdf",
              parse_status: "ready",
              created_at: now,
            },
          ],
        },
      ]),
    ),
    http.get(`${API}/api/postings`, () =>
      HttpResponse.json([
        {
          id: "p1",
          title: "Backend Engineer",
          company: "Acme",
          location: "",
          source: "paste",
          source_url: null,
          requirements_count: 4,
          created_at: now,
        },
      ]),
    ),
    http.get(`${API}/api/analyses`, () => HttpResponse.json([])),
    http.get(`${API}/api/me/usage`, () =>
      HttpResponse.json({ resets_at: now, items: { analysis: { used: 1, limit: 20 } } }),
    ),
    http.post(`${API}/api/analyses`, async ({ request }) => {
      body = await request.json();
      return HttpResponse.json({ analysis_id: "a1", task_id: null });
    }),
  );
  renderWithProviders(<HomePage />, { route: "/home", path: "/home" });
  await userEvent.click(await screen.findByRole("tab", { name: "Saved job" }));
  await userEvent.selectOptions(await screen.findByRole("combobox", { name: "Saved job" }), "p1");
  await userEvent.selectOptions(await screen.findByLabelText("Résumé"), "v1");
  await userEvent.click(screen.getByRole("button", { name: "Analyze" }));
  expect(await screen.findByTestId("location")).toHaveTextContent("/analyses/a1");
  expect(body).toEqual({ resume_version_id: "v1", posting_id: "p1", force: false });
});
