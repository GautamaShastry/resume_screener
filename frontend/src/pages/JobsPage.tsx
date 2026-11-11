import * as Dialog from "@radix-ui/react-dialog";
import { useQuery } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router-dom";
import { useApi } from "../api/ApiProvider";
import { unwrap } from "../api/client";
import { errorMessage } from "../api/errors";
import { ImportJobForm } from "../features/jobs/ImportJobForm";

export function JobsPage() {
  const api = useApi();
  const navigate = useNavigate();
  const { data, isLoading, error } = useQuery({
    queryKey: ["postings"],
    queryFn: () => unwrap(api.GET("/api/postings")),
  });
  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Jobs</h1>
        <Dialog.Root>
          <Dialog.Trigger asChild>
            <button className="rounded-md bg-slate-900 px-3 py-2 text-sm text-white">
              Import job
            </button>
          </Dialog.Trigger>
          <Dialog.Portal>
            <Dialog.Overlay className="fixed inset-0 bg-black/30" />
            <Dialog.Content className="fixed left-1/2 top-1/2 w-[min(40rem,94vw)] -translate-x-1/2 -translate-y-1/2 rounded-lg bg-white p-5 shadow-lg">
              <Dialog.Title className="mb-3 text-lg font-semibold">Import a job</Dialog.Title>
              <Dialog.Description className="sr-only">
                Import a job from a link or pasted text.
              </Dialog.Description>
              <ImportJobForm onImported={(id) => navigate(`/jobs/${id}`)} />
            </Dialog.Content>
          </Dialog.Portal>
        </Dialog.Root>
      </div>
      {isLoading && <p>Loading…</p>}
      {error && <p role="alert">{errorMessage(error)}</p>}
      {data && data.length === 0 && <p className="text-slate-600">No saved jobs yet.</p>}
      <ul className="divide-y rounded-lg border bg-white">
        {data?.map((p) => (
          <li key={p.id}>
            <Link
              to={`/jobs/${p.id}`}
              className="flex items-center justify-between p-4 hover:bg-slate-50"
            >
              <span>
                <span className="font-medium">{p.title || "Untitled job"}</span>
                {p.company && <span className="text-slate-600"> — {p.company}</span>}
              </span>
              <span className="text-sm text-slate-500">{p.requirements_count} requirements</span>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
