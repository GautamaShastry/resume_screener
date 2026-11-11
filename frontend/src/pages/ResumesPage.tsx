import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useApi } from "../api/ApiProvider";
import { unwrap } from "../api/client";
import { errorMessage } from "../api/errors";
import type { ResumeOut } from "../api/types";
import { StatusBadge } from "../components/StatusBadge";
import { UploadResumeDialog } from "../features/resumes/UploadResumeDialog";

function ResumeCard({ resume }: { resume: ResumeOut }) {
  const latest = resume.versions[resume.versions.length - 1];
  return (
    <li>
      <Link
        to={`/resumes/${resume.id}`}
        className="block rounded-lg border bg-white p-4 hover:border-slate-400"
      >
        <p className="font-medium">{resume.title}</p>
        <p className="text-sm text-slate-600">
          {resume.versions.length} version{resume.versions.length === 1 ? "" : "s"}
          {latest && ` · latest v${latest.version_no}`}
        </p>
        {latest && <StatusBadge status={latest.parse_status} />}
      </Link>
    </li>
  );
}

export function ResumesPage() {
  const api = useApi();
  const { data, isLoading, error } = useQuery({
    queryKey: ["resumes"],
    queryFn: () => unwrap(api.GET("/api/resumes")),
  });
  const active = data?.filter((r) => !r.archived) ?? [];
  const archived = data?.filter((r) => r.archived) ?? [];
  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Résumés</h1>
        <UploadResumeDialog trigger="Upload résumé" />
      </div>
      {isLoading && <p>Loading…</p>}
      {error && <p role="alert">{errorMessage(error)}</p>}
      {data && data.length === 0 && (
        <p className="text-slate-600">No résumés yet. Upload one to get started.</p>
      )}
      <ul className="grid gap-3 sm:grid-cols-2">
        {active.map((r) => (
          <ResumeCard key={r.id} resume={r} />
        ))}
      </ul>
      {archived.length > 0 && (
        <details>
          <summary className="cursor-pointer text-sm text-slate-600">
            Archived ({archived.length})
          </summary>
          <ul className="mt-2 grid gap-3 sm:grid-cols-2">
            {archived.map((r) => (
              <ResumeCard key={r.id} resume={r} />
            ))}
          </ul>
        </details>
      )}
    </section>
  );
}
