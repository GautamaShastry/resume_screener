import { createContext, useCallback, useContext, useState, type ReactNode } from "react";
import { Link } from "react-router-dom";

export interface ToastInput {
  message: string;
  kind: "success" | "error" | "info";
  href?: string;
  linkLabel?: string;
}
type Toast = ToastInput & { id: number };

const ToastContext = createContext<(t: ToastInput) => void>(() => {});
export const useToast = () => useContext(ToastContext);

const TONE = {
  success: "border-emerald-300 bg-emerald-50",
  error: "border-red-300 bg-red-50",
  info: "border-slate-300 bg-white",
};

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const push = useCallback((t: ToastInput) => {
    const id = Date.now() + Math.random();
    setToasts((ts) => [...ts, { ...t, id }]);
    setTimeout(() => setToasts((ts) => ts.filter((x) => x.id !== id)), 6000);
  }, []);
  return (
    <ToastContext.Provider value={push}>
      {children}
      <div aria-live="polite" className="fixed bottom-4 right-4 z-50 space-y-2">
        {toasts.map((t) => (
          <div
            key={t.id}
            role="status"
            className={`rounded-md border px-4 py-3 text-sm shadow ${TONE[t.kind]}`}
          >
            {t.message}
            {t.href && (
              <Link to={t.href} className="ml-2 font-medium underline">
                {t.linkLabel ?? "Open"}
              </Link>
            )}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
