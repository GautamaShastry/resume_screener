import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import type { ReactElement } from "react";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";
import { ApiProvider } from "../api/ApiProvider";
import { DEV_EMAIL_KEY, DevAuthProvider } from "../auth/AuthProvider";
import { ToastProvider } from "../components/Toaster";

export function LocationProbe() {
  const location = useLocation();
  return <div data-testid="location">{location.pathname}</div>;
}

export function renderWithProviders(
  ui: ReactElement,
  {
    route = "/",
    path = "/",
    email = "me@example.com",
  }: { route?: string; path?: string; email?: string | null } = {},
) {
  if (email) localStorage.setItem(DEV_EMAIL_KEY, email);
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  const result = render(
    <MemoryRouter initialEntries={[route]}>
      <DevAuthProvider>
        <ApiProvider>
          <QueryClientProvider client={queryClient}>
            <ToastProvider>
              <Routes>
                <Route path={path} element={ui} />
                <Route path="*" element={<LocationProbe />} />
              </Routes>
            </ToastProvider>
          </QueryClientProvider>
        </ApiProvider>
      </DevAuthProvider>
    </MemoryRouter>,
  );
  return { queryClient, ...result };
}
