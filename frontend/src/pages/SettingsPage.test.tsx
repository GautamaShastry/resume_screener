import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { DEV_EMAIL_KEY } from "../auth/AuthProvider";
import { renderWithProviders } from "../test/render";
import { API, server } from "../test/server";
import { SettingsPage } from "./SettingsPage";

test("account deletion requires typing DELETE, then signs out", async () => {
  let deleted = false;
  server.use(
    http.get(`${API}/api/me`, () =>
      HttpResponse.json({ id: "u1", email: "me@example.com", name: "me", plan: "free" }),
    ),
    http.get(`${API}/api/me/usage`, () =>
      HttpResponse.json({
        resets_at: "2026-01-02T00:00:00+00:00",
        items: { analysis: { used: 2, limit: 20 } },
      }),
    ),
    http.delete(`${API}/api/me`, () => {
      deleted = true;
      return new HttpResponse(null, { status: 204 });
    }),
  );
  renderWithProviders(<SettingsPage />, { route: "/settings", path: "/settings" });
  expect(await screen.findByText("me@example.com")).toBeInTheDocument();
  expect(await screen.findByText("Analyses")).toBeInTheDocument();
  expect(screen.getByText("2 / 20")).toBeInTheDocument();

  await userEvent.click(screen.getByRole("button", { name: "Delete my account" }));
  const confirm = screen.getByRole("button", { name: "Delete everything" });
  expect(confirm).toBeDisabled();
  await userEvent.type(screen.getByLabelText("Type DELETE to confirm"), "DELETE");
  await userEvent.click(confirm);
  expect(await screen.findByTestId("location")).toHaveTextContent("/");
  expect(deleted).toBe(true);
  expect(localStorage.getItem(DEV_EMAIL_KEY)).toBeNull();
});
