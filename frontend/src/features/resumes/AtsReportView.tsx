import type { AtsReport } from "../../api/types";

const ORDER = { error: 0, warning: 1, info: 2 } as const;
const LABEL = {
  error: { text: "Error", icon: "✗", cls: "border-red-200 bg-red-50 text-red-900" },
  warning: { text: "Warning", icon: "!", cls: "border-amber-200 bg-amber-50 text-amber-900" },
  info: { text: "Info", icon: "i", cls: "border-slate-200 bg-slate-50 text-slate-800" },
};

export function AtsReportView({ report }: { report: AtsReport }) {
  const checks = [...report.checks].sort((a, b) => ORDER[a.severity] - ORDER[b.severity]);
  const f = report.parsed_view.fields;
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <section aria-labelledby="ats-heading" className="rounded-lg border bg-white p-4">
        <h2 id="ats-heading" className="text-lg font-semibold">
          ATS check
        </h2>
        <p className="mb-3 text-xs text-slate-500">
          Simulates how common ATS parsers read your file.
        </p>
        {checks.length === 0 ? (
          <p>No issues found.</p>
        ) : (
          <ul className="space-y-2">
            {checks.map((c) => (
              <li key={c.check} className={`rounded-md border p-3 text-sm ${LABEL[c.severity].cls}`}>
                <p className="font-medium">
                  <span aria-hidden>{LABEL[c.severity].icon} </span>
                  {LABEL[c.severity].text}: {c.message}
                </p>
                <p className="mt-1">{c.how_to_fix}</p>
              </li>
            ))}
          </ul>
        )}
      </section>
      <section aria-labelledby="ats-sees" className="rounded-lg border bg-white p-4">
        <h2 id="ats-sees" className="text-lg font-semibold">
          What an ATS sees
        </h2>
        <dl className="my-3 grid grid-cols-[8rem_1fr] gap-y-1 text-sm">
          {(["name", "email", "phone"] as const).map((k) => (
            <div key={k} className="contents">
              <dt className="capitalize text-slate-500">{k}</dt>
              <dd>{f[k] ?? "Not found"}</dd>
            </div>
          ))}
          <dt className="text-slate-500">Sections</dt>
          <dd>{f.sections.length ? f.sections.join(", ") : "Not found"}</dd>
        </dl>
        <pre className="max-h-80 overflow-auto whitespace-pre-wrap rounded bg-slate-50 p-3 text-xs">
          {report.parsed_view.text}
        </pre>
      </section>
    </div>
  );
}
