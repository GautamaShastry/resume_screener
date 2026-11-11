import { screen } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { renderWithProviders } from "../test/render";
import { API, server } from "../test/server";
import { RunningTasks } from "./RunningTasks";

test("shows the number of running tasks", async () => {
  server.use(http.get(`${API}/api/tasks`, () => HttpResponse.json([{ id: "1" }, { id: "2" }])));
  renderWithProviders(<RunningTasks />);
  expect(await screen.findByText("2 tasks running")).toBeInTheDocument();
});

test("renders nothing when idle", async () => {
  renderWithProviders(<RunningTasks />);
  await new Promise((r) => setTimeout(r, 50));
  expect(screen.queryByRole("status")).not.toBeInTheDocument();
  expect(screen.queryByText(/running/)).not.toBeInTheDocument();
});
