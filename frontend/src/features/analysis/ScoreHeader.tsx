import type { AnalysisOut } from "../../api/types";

export function ScoreHeader({ analysis: a }: { analysis: AnalysisOut }) {
  const b = a.score_breakdown;
  const n = b.must_missing_count;
  const phrase = `${n} must-have requirement${n === 1 ? " is" : "s are"} missing.`;
  return (
    <header className="space-y-3 rounded-lg border bg-white p-5">
      <h1 className="text-2xl font-semibold">Match score: {a.score}</h1>
      <p className="text-slate-700">
        {a.posting.title || "Untitled job"}
        {a.posting.company && ` at ${a.posting.company}`} · {a.resume_version.resume_title} v
        {a.resume_version.version_no}
      </p>
      <dl className="grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
        <div>
          <dt className="text-slate-500">Requirement coverage</dt>
          <dd className="text-lg font-medium">{Math.round(b.coverage * 100)}%</dd>
        </div>
        <div>
          <dt className="text-slate-500">Seniority fit</dt>
          <dd className="text-lg font-medium">{b.seniority_fit}%</dd>
        </div>
        <div>
          <dt className="text-slate-500">Experience</dt>
          <dd className="text-lg font-medium">{b.years_experience} yrs</dd>
        </div>
        <div>
          <dt className="text-slate-500">Missing must-haves</dt>
          <dd className="text-lg font-medium">{n}</dd>
        </div>
      </dl>
      {n > 0 && (
        <p className="text-sm text-amber-800">
          {b.capped ? `Score capped at 75 because ${phrase}` : phrase}
        </p>
      )}
      <p className="text-xs text-slate-500">
        Score = 85% requirement coverage (must-haves count 3×, partial matches count half) + 15%
        seniority fit.
      </p>
    </header>
  );
}
