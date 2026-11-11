import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { App } from "./App";
import { DEV_EMAIL_KEY } from "./auth/AuthProvider";
import { renderWithProviders } from "./test/render";

test("dev sign-in leads to the app with main navigation", async () => {
  renderWithProviders(<App />, { path: "/*", email: null });
  await userEvent.type(screen.getByLabelText("Email"), "Me@Example.com");
  await userEvent.click(screen.getByRole("button", { name: "Continue" }));
  expect(await screen.findByRole("navigation", { name: "Main" })).toBeInTheDocument();
  expect(localStorage.getItem(DEV_EMAIL_KEY)).toBe("me@example.com");
});

test("protected pages redirect to the landing page when signed out", async () => {
  renderWithProviders(<App />, { route: "/home", path: "/*", email: null });
  expect(await screen.findByLabelText("Email")).toBeInTheDocument();
});
