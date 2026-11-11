import { ApiError } from "./client";

export function errorMessage(err: unknown): string {
  if (err instanceof ApiError) {
    if (err.code === "QUOTA_EXCEEDED") {
      const resets = err.details["resets_at"];
      const when =
        typeof resets === "string"
          ? ` It resets at ${new Date(resets).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}.`
          : "";
      return `You've reached today's limit for this action.${when}`;
    }
    if (err.code === "RATE_LIMITED") return "Too many requests. Wait a minute and try again.";
    return err.message;
  }
  return "Something went wrong. Try again.";
}
