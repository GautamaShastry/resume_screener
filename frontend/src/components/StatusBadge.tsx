const STYLES: Record<string, { label: string; icon: string; cls: string }> = {
  ready: { label: "Ready", icon: "✓", cls: "bg-emerald-50 text-emerald-800" },
  pending: { label: "Processing", icon: "…", cls: "bg-amber-50 text-amber-800" },
  failed: { label: "Failed", icon: "✗", cls: "bg-red-50 text-red-800" },
};

export function StatusBadge({ status }: { status: string }) {
  const s = STYLES[status] ?? STYLES.pending;
  return (
    <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs ${s.cls}`}>
      <span aria-hidden>{s.icon}</span>
      {s.label}
    </span>
  );
}
