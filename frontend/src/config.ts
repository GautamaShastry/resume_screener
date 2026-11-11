const env = import.meta.env;

export const config = {
  apiBaseUrl: (env.VITE_API_BASE_URL as string | undefined) ?? "http://localhost:8000",
  authMode: ((env.VITE_AUTH_MODE as string | undefined) ?? "dev") as "dev" | "entra",
  entra: {
    clientId: (env.VITE_ENTRA_CLIENT_ID as string | undefined) ?? "",
    authority: (env.VITE_ENTRA_AUTHORITY as string | undefined) ?? "",
    apiScope: (env.VITE_ENTRA_API_SCOPE as string | undefined) ?? "",
  },
};
