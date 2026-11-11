import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { useApi } from "../api/ApiProvider";
import { unwrap } from "../api/client";
import { useAuth } from "../auth/AuthProvider";
import { ConfirmDialog } from "../components/ConfirmDialog";

const LABELS: Record<string, string> = {
  resume_upload: "Résumé uploads",
  posting_import: "Job imports",
  analysis: "Analyses",
  tailoring: "Tailoring runs",
  practice_session: "Practice sessions",
  practice_answer: "Practice answers",
  recommendation: "Recommendation runs",
};

export function SettingsPage() {
  const api = useApi();
  const { signOut } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const me = useQuery({ queryKey: ["me"], queryFn: () => unwrap(api.GET("/api/me")) });
  const usage = useQuery({ queryKey: ["usage"], queryFn: () => unwrap(api.GET("/api/me/usage")) });
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Settings</h1>
      <section className="rounded-lg border bg-white p-4">
        <h2 className="text-lg font-semibold">Account</h2>
        {me.data && (
          <dl className="mt-2 grid grid-cols-[8rem_1fr] gap-y-1 text-sm">
            <dt className="text-slate-500">Email</dt>
            <dd>{me.data.email}</dd>
            <dt className="text-slate-500">Plan</dt>
            <dd className="capitalize">{me.data.plan}</dd>
          </dl>
        )}
      </section>
      <section className="rounded-lg border bg-white p-4">
        <h2 className="text-lg font-semibold">Today's usage</h2>
        {usage.data && (
          <>
            <table className="mt-2 text-sm">
              <tbody>
                {Object.entries(usage.data.items).map(([kind, item]) => (
                  <tr key={kind}>
                    <th scope="row" className="pr-6 text-left font-normal text-slate-600">
                      {LABELS[kind] ?? kind}
                    </th>
                    <td>{`${item.used} / ${item.limit}`}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="mt-2 text-xs text-slate-500">
              Limits reset at {new Date(usage.data.resets_at).toLocaleString()}.
            </p>
          </>
        )}
      </section>
      <section className="rounded-lg border border-red-200 bg-white p-4">
        <h2 className="text-lg font-semibold">Delete account</h2>
        <p className="my-2 text-sm text-slate-700">
          Permanently deletes your résumés, jobs, analyses, and uploaded files.
        </p>
        <ConfirmDialog
          trigger="Delete my account"
          title="Delete your account?"
          description="This permanently deletes all your data. It can't be undone."
          confirmLabel="Delete everything"
          requireText="DELETE"
          onConfirm={async () => {
            await unwrap(api.DELETE("/api/me"));
            queryClient.clear();
            await signOut();
            navigate("/");
          }}
        />
      </section>
    </div>
  );
}
