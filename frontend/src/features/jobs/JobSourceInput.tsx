import * as Tabs from "@radix-ui/react-tabs";
import { useQuery } from "@tanstack/react-query";
import { useApi } from "../../api/ApiProvider";
import { unwrap } from "../../api/client";

export interface JobSource {
  tab: "url" | "paste" | "saved";
  url: string;
  text: string;
  postingId: string;
}
export const emptyJobSource: JobSource = { tab: "url", url: "", text: "", postingId: "" };

const tabClass =
  "rounded-md border px-3 py-1.5 text-sm data-[state=active]:bg-slate-900 data-[state=active]:text-white";

export function jobSourceError(v: JobSource): string | null {
  if (v.tab === "url" && !/^https?:\/\//i.test(v.url.trim()))
    return "Enter a job posting link starting with http or https.";
  if (v.tab === "paste" && v.text.trim().length < 100)
    return "Paste the full job description (at least 100 characters).";
  if (v.tab === "saved" && !v.postingId) return "Choose a saved job.";
  return null;
}

export function JobSourceInput({
  value,
  onChange,
  allowSaved = false,
}: {
  value: JobSource;
  onChange: (v: JobSource) => void;
  allowSaved?: boolean;
}) {
  const api = useApi();
  const postings = useQuery({
    queryKey: ["postings"],
    enabled: allowSaved,
    queryFn: () => unwrap(api.GET("/api/postings")),
  });
  return (
    <Tabs.Root
      value={value.tab}
      onValueChange={(tab) => onChange({ ...value, tab: tab as JobSource["tab"] })}
    >
      <Tabs.List aria-label="Job source" className="mb-3 flex gap-2">
        <Tabs.Trigger value="url" className={tabClass}>
          Job link
        </Tabs.Trigger>
        <Tabs.Trigger value="paste" className={tabClass}>
          Paste text
        </Tabs.Trigger>
        {allowSaved && (
          <Tabs.Trigger value="saved" className={tabClass}>
            Saved job
          </Tabs.Trigger>
        )}
      </Tabs.List>
      <Tabs.Content value="url">
        <label htmlFor="job-url" className="block text-sm font-medium">
          Job posting URL
        </label>
        <input
          id="job-url"
          type="url"
          value={value.url}
          onChange={(e) => onChange({ ...value, url: e.target.value })}
          placeholder="https://jobs.lever.co/…"
          className="mt-1 w-full rounded-md border px-3 py-2"
        />
        <p className="mt-1 text-xs text-slate-500">
          Greenhouse, Lever, Ashby and most company career pages work. For LinkedIn or Indeed,
          paste the text.
        </p>
      </Tabs.Content>
      <Tabs.Content value="paste">
        <label htmlFor="job-text" className="block text-sm font-medium">
          Job description
        </label>
        <textarea
          id="job-text"
          rows={10}
          value={value.text}
          onChange={(e) => onChange({ ...value, text: e.target.value })}
          className="mt-1 w-full rounded-md border px-3 py-2"
        />
      </Tabs.Content>
      {allowSaved && (
        <Tabs.Content value="saved">
          <label htmlFor="job-saved" className="block text-sm font-medium">
            Saved job
          </label>
          <select
            id="job-saved"
            value={value.postingId}
            onChange={(e) => onChange({ ...value, postingId: e.target.value })}
            className="mt-1 w-full rounded-md border px-3 py-2"
          >
            <option value="">Choose a job…</option>
            {postings.data?.map((p) => (
              <option key={p.id} value={p.id}>
                {p.title || "Untitled"}
                {p.company ? ` — ${p.company}` : ""}
              </option>
            ))}
          </select>
        </Tabs.Content>
      )}
    </Tabs.Root>
  );
}
