import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";
import { config } from "../config";

export function LandingPage() {
  const { status, signIn } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  if (status === "signedIn") return <Navigate to="/home" replace />;
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 p-6">
      <div className="w-full max-w-xl space-y-6">
        <h1 className="text-3xl font-bold">HireReady</h1>
        <p className="text-slate-700">
          See exactly how your résumé matches a job — every requirement backed by a quote from your
          résumé — then close the gaps.
        </p>
        <ul className="list-disc space-y-1 pl-5 text-slate-700">
          <li>Evidence-based match score</li>
          <li>ATS readability check</li>
          <li>Clear gaps with concrete next steps</li>
        </ul>
        {config.authMode === "dev" ? (
          <form
            className="space-y-3 rounded-lg border bg-white p-4"
            onSubmit={async (e) => {
              e.preventDefault();
              try {
                await signIn(email);
                navigate("/home");
              } catch (err) {
                setError((err as Error).message);
              }
            }}
          >
            <label htmlFor="dev-email" className="block text-sm font-medium">
              Email
            </label>
            <input
              id="dev-email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-md border px-3 py-2"
            />
            {error && (
              <p role="alert" className="text-sm text-red-700">
                {error}
              </p>
            )}
            <button type="submit" className="rounded-md bg-slate-900 px-4 py-2 text-white">
              Continue
            </button>
            <p className="text-xs text-slate-500">
              Development sign-in. Production uses Microsoft Entra.
            </p>
          </form>
        ) : (
          <button
            onClick={() => signIn()}
            className="rounded-md bg-slate-900 px-4 py-2 text-white"
          >
            Sign in or create an account
          </button>
        )}
      </div>
    </div>
  );
}
