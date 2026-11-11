import { useQuery } from "@tanstack/react-query";
import { useApi } from "../api/ApiProvider";
import { unwrap } from "../api/client";

export function RunningTasks() {
  const api = useApi();
  const { data } = useQuery({
    queryKey: ["tasks", "active"],
    queryFn: () => unwrap(api.GET("/api/tasks", { params: { query: { active: true } } })),
    refetchInterval: (q) => (q.state.data && q.state.data.length > 0 ? 3000 : 15000),
  });
  const n = data?.length ?? 0;
  if (!n) return null;
  return (
    <span role="status" className="rounded-full bg-amber-100 px-2 py-1 text-xs text-amber-900">
      {n} {n === 1 ? "task" : "tasks"} running
    </span>
  );
}
