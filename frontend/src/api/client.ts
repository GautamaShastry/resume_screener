import createClient, { type Middleware } from "openapi-fetch";
import { config } from "../config";
import type { paths } from "./schema";

export class ApiError extends Error {
  status: number;
  code: string;
  details: Record<string, unknown>;

  constructor(status: number, code: string, message: string, details: Record<string, unknown> = {}) {
    super(message);
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

export function createApi(getToken: () => Promise<string>) {
  const client = createClient<paths>({ baseUrl: config.apiBaseUrl });
  const auth: Middleware = {
    async onRequest({ request }) {
      request.headers.set("Authorization", `Bearer ${await getToken()}`);
      return request;
    },
  };
  client.use(auth);
  return client;
}

export type ApiClient = ReturnType<typeof createApi>;

export async function unwrap<T>(
  promise: Promise<{ data?: T; error?: unknown; response: Response }>,
): Promise<T> {
  const { data, error, response } = await promise;
  if (!response.ok) {
    const e = (error ?? {}) as {
      code?: string;
      message?: string;
      details?: Record<string, unknown>;
    };
    throw new ApiError(
      response.status,
      e.code ?? "HTTP_ERROR",
      e.message ?? `Request failed (${response.status})`,
      e.details ?? {},
    );
  }
  return data as T;
}
