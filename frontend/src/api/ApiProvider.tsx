import { createContext, useContext, useMemo, type ReactNode } from "react";
import { useAuth } from "../auth/AuthProvider";
import { createApi, type ApiClient } from "./client";

const ApiContext = createContext<ApiClient | null>(null);

export function ApiProvider({ children }: { children: ReactNode }) {
  const { getToken } = useAuth();
  const api = useMemo(() => createApi(getToken), [getToken]);
  return <ApiContext.Provider value={api}>{children}</ApiContext.Provider>;
}

export function useApi(): ApiClient {
  const api = useContext(ApiContext);
  if (!api) throw new Error("useApi must be used inside ApiProvider");
  return api;
}
