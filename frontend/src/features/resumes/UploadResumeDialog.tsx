import * as Dialog from "@radix-ui/react-dialog";
import { useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef, useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { errorMessage } from "../../api/errors";
import { rawRequest } from "../../api/raw";
import type { UploadOut } from "../../api/types";
import { useAuth } from "../../auth/AuthProvider";
import { useTaskNotifier } from "../../components/TaskNotifier";
import { TaskStepper } from "../../components/TaskStepper";
import { useTask } from "../../hooks/useTask";

const MAX_BYTES = 5 * 1024 * 1024;

export function UploadResumeDialog({ trigger, resumeId }: { trigger: string; resumeId?: string }) {
  const { getToken } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const notifier = useTaskNotifier();
  const [open, setOpen] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [started, setStarted] = useState<UploadOut | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const inFlight = useRef(false); // synchronous guard: two clicks can land before a re-render
  const { task, error: streamError } = useTask(started?.task_id);

  useEffect(() => {
    if (task?.status === "succeeded" && started) {
      void queryClient.invalidateQueries({ queryKey: ["resumes"] });
      void queryClient.invalidateQueries({ queryKey: ["resume", started.resume_id] });
      setOpen(false);
      navigate(`/resumes/${started.resume_id}?version=${started.resume_version_id}`);
    }
  }, [task?.status, started, navigate, queryClient]);

  const pickFile = (f: File | null) => {
    setError(null);
    setFile(null);
    if (!f) return;
    if (!/\.(pdf|docx)$/i.test(f.name)) return setError("Choose a PDF or DOCX file.");
    if (f.size > MAX_BYTES) return setError("This file is larger than 5 MB.");
    setFile(f);
    if (!title) setTitle(f.name.replace(/\.(pdf|docx)$/i, ""));
  };

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    if (!file) return setError("Choose a file to upload.");
    if (inFlight.current) return;
    inFlight.current = true;
    setSubmitting(true);
    const form = new FormData();
    form.append("file", file);
    if (!resumeId) form.append("title", title.trim() || file.name);
    try {
      const path = resumeId ? `/api/resumes/${resumeId}/versions` : "/api/resumes";
      const res = (await (
        await rawRequest(getToken, path, { method: "POST", body: form })
      ).json()) as UploadOut;
      setStarted(res);
      notifier.watch({
        id: res.task_id,
        label: "Résumé processing",
        href: () => `/resumes/${res.resume_id}?version=${res.resume_version_id}`,
      });
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      inFlight.current = false;
      setSubmitting(false);
    }
  };

  return (
    <Dialog.Root
      open={open}
      onOpenChange={(o) => {
        setOpen(o);
        if (!o) {
          setStarted(null);
          setFile(null);
          setError(null);
        }
      }}
    >
      <Dialog.Trigger asChild>
        <button className="rounded-md bg-slate-900 px-3 py-2 text-sm text-white">{trigger}</button>
      </Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/30" />
        <Dialog.Content className="fixed left-1/2 top-1/2 w-[min(32rem,92vw)] -translate-x-1/2 -translate-y-1/2 rounded-lg bg-white p-5 shadow-lg">
          <Dialog.Title className="text-lg font-semibold">
            {resumeId ? "Upload a new version" : "Upload résumé"}
          </Dialog.Title>
          <Dialog.Description className="text-sm text-slate-600">
            PDF or DOCX, up to 5 MB.
          </Dialog.Description>
          {started ? (
            <div className="mt-4">
              <TaskStepper task={task} error={streamError} label="Processing your résumé" />
            </div>
          ) : (
            <form onSubmit={submit} className="mt-4 space-y-3" noValidate>
              <div>
                <label htmlFor="resume-file" className="block text-sm font-medium">
                  Résumé file
                </label>
                <input
                  id="resume-file"
                  type="file"
                  accept=".pdf,.docx"
                  onChange={(e) => pickFile(e.target.files?.[0] ?? null)}
                  className="mt-1 block w-full text-sm"
                />
              </div>
              {!resumeId && (
                <div>
                  <label htmlFor="resume-title" className="block text-sm font-medium">
                    Title
                  </label>
                  <input
                    id="resume-title"
                    value={title}
                    maxLength={200}
                    onChange={(e) => setTitle(e.target.value)}
                    className="mt-1 w-full rounded-md border px-3 py-2"
                  />
                </div>
              )}
              {error && (
                <p role="alert" className="text-sm text-red-700">
                  {error}
                </p>
              )}
              <div className="flex justify-end gap-2">
                <Dialog.Close asChild>
                  <button type="button" className="rounded-md border px-3 py-2 text-sm">
                    Cancel
                  </button>
                </Dialog.Close>
                <button
                  type="submit"
                  disabled={submitting}
                  className="rounded-md bg-slate-900 px-3 py-2 text-sm text-white disabled:opacity-50"
                >
                  Upload
                </button>
              </div>
            </form>
          )}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
