import { Fragment, useState } from "react";
import type { EvidenceItem, Requirement } from "../../api/types";

const STATUS = {
  met: { icon: "✓", label: "Met", cls: "text-emerald-700" },
  partial: { icon: "◐", label: "Partial", cls: "text-amber-700" },
  missing: { icon: "✗", label: "Missing", cls: "text-red-700" },
} as const;

type KindFilter = "all" | "must" | "nice";
type StatusFilter = "all" | "met" | "partial" | "missing";

export function RequirementsTable({
  requirements,
  evidence,
}: {
  requirements: Requirement[];
  evidence: EvidenceItem[];
}) {
  const [kind, setKind] = useState<KindFilter>("all");
  const [status, setStatus] = useState<StatusFilter>("all");
  const [open, setOpen] = useState<Set<string>>(new Set());
  const byId = new Map(evidence.map((e) => [e.requirement_id, e]));
  const rows = requirements.filter(
    (r) =>
      (kind === "all" || r.kind === kind) &&
      (status === "all" || (byId.get(r.id)?.status ?? "missing") === status),
  );
  const toggle = (id: string) =>
    setOpen((s) => {
      const next = new Set(s);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  return (
    <section aria-labelledby="req-heading" className="rounded-lg border bg-white p-4">
      <h2 id="req-heading" className="text-lg font-semibold">
        Requirements
      </h2>
      <div className="my-3 flex flex-wrap gap-4 text-sm">
        <label>
          Type{" "}
          <select
            value={kind}
            onChange={(e) => setKind(e.target.value as KindFilter)}
            className="rounded-md border px-2 py-1"
          >
            <option value="all">All</option>
            <option value="must">Must-have</option>
            <option value="nice">Nice-to-have</option>
          </select>
        </label>
        <label>
          Status{" "}
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value as StatusFilter)}
            className="rounded-md border px-2 py-1"
          >
            <option value="all">All</option>
            <option value="met">Met</option>
            <option value="partial">Partial</option>
            <option value="missing">Missing</option>
          </select>
        </label>
      </div>
      <div className="overflow-x-auto">
        <table aria-label="Requirements" className="w-full text-left text-sm">
          <thead>
            <tr className="text-slate-500">
              <th scope="col" className="py-2">
                Requirement
              </th>
              <th scope="col">Type</th>
              <th scope="col">Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => {
              const ev = byId.get(r.id);
              const st = STATUS[ev?.status ?? "missing"];
              const isOpen = open.has(r.id);
              return (
                <Fragment key={r.id}>
                  <tr className="border-t align-top">
                    <td className="py-2 pr-3">
                      <button
                        type="button"
                        aria-expanded={isOpen}
                        aria-controls={`ev-${r.id}`}
                        onClick={() => toggle(r.id)}
                        className="text-left hover:underline"
                      >
                        {r.text}
                      </button>
                    </td>
                    <td className="pr-3">{r.kind === "must" ? "Must-have" : "Nice-to-have"}</td>
                    <td className={st.cls}>
                      <span aria-hidden>{st.icon}</span> {st.label}
                    </td>
                  </tr>
                  {isOpen && (
                    <tr id={`ev-${r.id}`}>
                      <td colSpan={3} className="bg-slate-50 p-3">
                        {ev?.quotes.length ? (
                          <ul className="space-y-1">
                            {ev.quotes.map((q) => (
                              <li key={q.bullet_id}>
                                <blockquote className="border-l-2 border-slate-300 pl-2 italic">
                                  “{q.text}”
                                </blockquote>
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <p>No supporting line found in your résumé.</p>
                        )}
                        {ev?.note && <p className="mt-2 text-slate-600">{ev.note}</p>}
                        <p className="mt-1 text-xs text-slate-500">
                          From the posting: “{r.source_phrase}”
                        </p>
                      </td>
                    </tr>
                  )}
                </Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
      {rows.length === 0 && <p className="mt-2 text-sm">No requirements match these filters.</p>}
    </section>
  );
}
