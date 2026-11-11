import clsx from "clsx";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";
import { ErrorBoundary } from "./ErrorBoundary";
import { RunningTasks } from "./RunningTasks";

const linkClass = ({ isActive }: { isActive: boolean }) =>
  clsx(
    "rounded-md px-3 py-2 text-sm font-medium",
    isActive ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-100",
  );

export function Layout() {
  const { email, signOut } = useAuth();
  const navigate = useNavigate();
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b bg-white">
        <div className="mx-auto flex h-14 max-w-6xl items-center gap-4 px-4">
          <span className="font-semibold">HireReady</span>
          <nav aria-label="Main" className="flex gap-1 overflow-x-auto">
            <NavLink to="/home" className={linkClass}>
              Home
            </NavLink>
            <NavLink to="/resumes" className={linkClass}>
              Résumés
            </NavLink>
            <NavLink to="/jobs" className={linkClass}>
              Jobs
            </NavLink>
            <NavLink to="/settings" className={linkClass}>
              Settings
            </NavLink>
          </nav>
          <div className="ml-auto flex items-center gap-3">
            <RunningTasks />
            <span className="hidden text-sm text-slate-500 sm:inline">{email}</span>
            <button
              className="rounded-md border px-3 py-1.5 text-sm"
              onClick={async () => {
                await signOut();
                navigate("/");
              }}
            >
              Sign out
            </button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-6">
        <ErrorBoundary>
          <Outlet />
        </ErrorBoundary>
      </main>
    </div>
  );
}
