import { useQueryClient } from "@tanstack/react-query";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import type { TaskOut } from "../api/types";
import { useTask } from "../hooks/useTask";
import { useToast } from "./Toaster";

export interface Watch {
  id: string;
  label: string;
  href?: (task: TaskOut) => string | undefined;
}

const NotifierContext = createContext<{ watch: (w: Watch) => void }>({ watch: () => {} });
export const useTaskNotifier = () => useContext(NotifierContext);

function Watcher({ watch, onFinished }: { watch: Watch; onFinished: (id: string) => void }) {
  const { task } = useTask(watch.id);
  const toast = useToast();
  const queryClient = useQueryClient();
  useEffect(() => {
    if (task?.status === "succeeded") {
      toast({ kind: "success", message: `${watch.label} finished.`, href: watch.href?.(task) });
      void queryClient.invalidateQueries();
      onFinished(watch.id);
    } else if (task?.status === "failed") {
      toast({
        kind: "error",
        message: `${watch.label} failed: ${task.error_message ?? "Something went wrong."}`,
      });
      onFinished(watch.id);
    }
  }, [task, watch, toast, queryClient, onFinished]);
  return null;
}

export function TaskNotifierProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<Watch[]>([]);
  const watch = useCallback(
    (w: Watch) => setItems((xs) => (xs.some((x) => x.id === w.id) ? xs : [...xs, w])),
    [],
  );
  const remove = useCallback((id: string) => setItems((xs) => xs.filter((x) => x.id !== id)), []);
  const value = useMemo(() => ({ watch }), [watch]);
  return (
    <NotifierContext.Provider value={value}>
      {children}
      {items.map((w) => (
        <Watcher key={w.id} watch={w} onFinished={remove} />
      ))}
    </NotifierContext.Provider>
  );
}
