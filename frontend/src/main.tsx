import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { ApiProvider } from "./api/ApiProvider";
import { ApiError } from "./api/client";
import { App } from "./App";
import { AuthProvider } from "./auth/AuthProvider";
import { TaskNotifierProvider } from "./components/TaskNotifier";
import { ToastProvider } from "./components/Toaster";
import "./index.css";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 10_000,
      retry: (count, err) => !(err instanceof ApiError && err.status < 500) && count < 2,
    },
  },
});

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <ApiProvider>
          <QueryClientProvider client={queryClient}>
            <ToastProvider>
              <TaskNotifierProvider>
                <App />
              </TaskNotifierProvider>
            </ToastProvider>
          </QueryClientProvider>
        </ApiProvider>
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>,
);
