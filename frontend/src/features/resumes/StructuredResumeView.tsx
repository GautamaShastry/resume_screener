import type { StructuredResume } from "../../api/types";

export function StructuredResumeView({ structured }: { structured: StructuredResume }) {
  return (
    <section aria-labelledby="structured-heading" className="rounded-lg border bg-white p-4">
      <h2 id="structured-heading" className="text-lg font-semibold">
        How we read your résumé
      </h2>
      {structured.summary && <p className="mt-2 text-sm">{structured.summary.text}</p>}
      {structured.skills.length > 0 && (
        <ul className="mt-3 flex flex-wrap gap-1" aria-label="Skills">
          {structured.skills.map((s) => (
            <li key={s.id} className="rounded bg-slate-100 px-2 py-0.5 text-xs">
              {s.text}
            </li>
          ))}
        </ul>
      )}
      {structured.sections.map((section) => (
        <div key={section.id} className="mt-4">
          <h3 className="font-medium">{section.title}</h3>
          {section.entries.map((entry) => (
            <div key={entry.id} className="mt-2">
              <p className="text-sm font-medium">
                {[entry.role, entry.org].filter(Boolean).join(", ")}
                {(entry.start || entry.end) && (
                  <span className="font-normal text-slate-500">
                    {" "}
                    ({[entry.start, entry.end].filter(Boolean).join(" – ")})
                  </span>
                )}
              </p>
              <ul className="list-disc pl-5 text-sm">
                {entry.bullets.map((b) => (
                  <li key={b.id}>{b.text}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      ))}
    </section>
  );
}
