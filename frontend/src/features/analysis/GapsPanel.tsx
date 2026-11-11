import type { GapItem, Requirement } from "../../api/types";

export function GapsPanel({ gaps, requirements }: { gaps: GapItem[]; requirements: Requirement[] }) {
  const text = new Map(requirements.map((r) => [r.id, r.text]));
  const notStated = gaps.filter((g) => g.type === "not_stated");
  const real = gaps.filter((g) => g.type === "real_gap" && g.project);
  return (
    <section aria-labelledby="gaps-heading" className="space-y-4 rounded-lg border bg-white p-4">
      <h2 id="gaps-heading" className="text-lg font-semibold">
        Gaps
      </h2>
      {gaps.length === 0 && <p>No gaps found — every requirement has evidence.</p>}
      {notStated.length > 0 && (
        <div>
          <h3 className="font-medium">You likely have these — say so</h3>
          <ul className="mt-2 space-y-3">
            {notStated.map((g) => (
              <li key={g.requirement_id} className="rounded-md border p-3 text-sm">
                <p className="font-medium">{text.get(g.requirement_id)}</p>
                <p className="mt-1 text-slate-600">Related lines in your résumé:</p>
                <ul className="list-disc pl-5">
                  {g.related_quotes.map((q) => (
                    <li key={q.bullet_id}>“{q.text}”</li>
                  ))}
                </ul>
                <p className="mt-2 text-slate-600">Suggested bullet:</p>
                <p className="rounded bg-slate-50 p-2">{g.suggested_bullet}</p>
                <p className="mt-1 text-xs text-amber-800">Only add this if it's true.</p>
              </li>
            ))}
          </ul>
        </div>
      )}
      {real.length > 0 && (
        <div>
          <h3 className="font-medium">Real gaps — a project to close each</h3>
          <ul className="mt-2 space-y-3">
            {real.map((g) =>
              g.project ? (
                <li key={g.requirement_id} className="rounded-md border p-3 text-sm">
                  <p className="font-medium">{text.get(g.requirement_id)}</p>
                  <p className="mt-1 font-semibold">{g.project.title}</p>
                  <p>{g.project.scope}</p>
                  <ul className="list-disc pl-5">
                    {g.project.deliverables.map((d) => (
                      <li key={d}>{d}</li>
                    ))}
                  </ul>
                  <p className="mt-1 text-slate-600">
                    Résumé bullet once done: “{g.project.resume_bullet}”
                  </p>
                </li>
              ) : null,
            )}
          </ul>
        </div>
      )}
    </section>
  );
}
