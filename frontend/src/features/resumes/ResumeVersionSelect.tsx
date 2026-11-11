import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useApi } from "../../api/ApiProvider";
import { unwrap } from "../../api/client";

export function ResumeVersionSelect({
  value,
  onChange,
}: {
  value: string;
  onChange: (id: string) => void;
}) {
  const api = useApi();
  const { data, isLoading } = useQuery({
    queryKey: ["resumes"],
    queryFn: () => unwrap(api.GET("/api/resumes")),
  });
  const options = (data ?? [])
    .filter((r) => !r.archived)
    .map((r) => {
      const ready = [...r.versions].reverse().find((v) => v.parse_status === "ready");
      return ready ? { id: ready.id, label: `${r.title} (v${ready.version_no})` } : null;
    })
    .filter((o): o is { id: string; label: string } => o !== null);
  if (!isLoading && options.length === 0) {
    return (
      <p className="text-sm text-slate-700">
        <Link to="/resumes" className="underline">
          Upload a résumé
        </Link>{" "}
        first.
      </p>
    );
  }
  return (
    <div>
      <label htmlFor="resume-version" className="block text-sm font-medium">
        Résumé
      </label>
      <select
        id="resume-version"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="mt-1 w-full rounded-md border px-3 py-2"
      >
        <option value="">Choose a résumé…</option>
        {options.map((o) => (
          <option key={o.id} value={o.id}>
            {o.label}
          </option>
        ))}
      </select>
    </div>
  );
}
