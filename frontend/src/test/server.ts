import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";

export const API = "http://localhost:8000";
export const defaultHandlers = [http.get(`${API}/api/tasks`, () => HttpResponse.json([]))];
export const server = setupServer(...defaultHandlers);
