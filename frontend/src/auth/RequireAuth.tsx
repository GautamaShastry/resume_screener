import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "./AuthProvider";

export function RequireAuth({ children }: { children: ReactNode }) {
  const { status } = useAuth();
  if (status === "loading") return <p className="p-6">Loading…</p>;
  if (status === "signedOut") return <Navigate to="/" replace />;
  return <>{children}</>;
}
