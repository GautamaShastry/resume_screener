import { config } from "../config";
import { ApiError } from "./client";

export async function rawRequest(
  getToken: () => Promise<string>,
  path: string,
  init: RequestInit = {},
): Promise<Response> {
  const headers = new Headers(init.headers);
  headers.set("Authorization", `Bearer ${await getToken()}`);
  const res = await fetch(`${config.apiBaseUrl}${path}`, { ...init, headers });
  if (!res.ok) {
    let body: { code?: string; message?: string; details?: Record<string, unknown> } = {};
    try {
      body = await res.json();
    } catch {
      /* non-JSON error body */
    }
    throw new ApiError(
      res.status,
      body.code ?? "HTTP_ERROR",
      body.message ?? `Request failed (${res.status})`,
      body.details ?? {},
    );
  }
  return res;
}

export async function downloadFile(
  getToken: () => Promise<string>,
  path: string,
  filename: string,
) {
  const res = await rawRequest(getToken, path);
  const url = URL.createObjectURL(await res.blob());
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
