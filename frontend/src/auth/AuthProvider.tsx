import {
  InteractionRequiredAuthError,
  InteractionStatus,
  PublicClientApplication,
} from "@azure/msal-browser";
import { MsalProvider, useMsal } from "@azure/msal-react";
import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";
import { config } from "../config";

export interface AuthApi {
  status: "loading" | "signedOut" | "signedIn";
  email: string | null;
  getToken: () => Promise<string>;
  signIn: (email?: string) => Promise<void>;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthApi | null>(null);
export const DEV_EMAIL_KEY = "hireready.devEmail";

export function useAuth(): AuthApi {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}

export function DevAuthProvider({ children }: { children: ReactNode }) {
  const [email, setEmail] = useState<string | null>(() => localStorage.getItem(DEV_EMAIL_KEY));
  const getToken = useCallback(async () => {
    if (!email) throw new Error("Not signed in");
    return `dev:${email}`;
  }, [email]);
  const signIn = useCallback(async (value?: string) => {
    const v = (value ?? "").trim().toLowerCase();
    if (!v.includes("@")) throw new Error("Enter an email address");
    localStorage.setItem(DEV_EMAIL_KEY, v);
    setEmail(v);
  }, []);
  const signOut = useCallback(async () => {
    localStorage.removeItem(DEV_EMAIL_KEY);
    setEmail(null);
  }, []);
  const value = useMemo<AuthApi>(
    () => ({ status: email ? "signedIn" : "signedOut", email, getToken, signIn, signOut }),
    [email, getToken, signIn, signOut],
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

function EntraAuthBridge({ children }: { children: ReactNode }) {
  const { instance, accounts, inProgress } = useMsal();
  const account = accounts[0] ?? null;
  const scopes = useMemo(() => [config.entra.apiScope], []);
  const getToken = useCallback(async () => {
    if (!account) throw new Error("Not signed in");
    try {
      return (await instance.acquireTokenSilent({ scopes, account })).accessToken;
    } catch (err) {
      if (err instanceof InteractionRequiredAuthError) {
        await instance.acquireTokenRedirect({ scopes, account });
      }
      throw err;
    }
  }, [instance, account, scopes]);
  const signIn = useCallback(async () => {
    await instance.loginRedirect({ scopes });
  }, [instance, scopes]);
  const signOut = useCallback(async () => {
    await instance.logoutRedirect({ account: account ?? undefined });
  }, [instance, account]);
  const status: AuthApi["status"] = account
    ? "signedIn"
    : inProgress !== InteractionStatus.None
      ? "loading"
      : "signedOut";
  const value = useMemo<AuthApi>(
    () => ({ status, email: account?.username ?? null, getToken, signIn, signOut }),
    [status, account, getToken, signIn, signOut],
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

let msal: PublicClientApplication | null = null;
function getMsal(): PublicClientApplication {
  msal ??= new PublicClientApplication({
    auth: {
      clientId: config.entra.clientId,
      authority: config.entra.authority,
      knownAuthorities: config.entra.authority ? [new URL(config.entra.authority).host] : [],
      redirectUri: window.location.origin,
    },
    cache: { cacheLocation: "localStorage" },
  });
  return msal;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  if (config.authMode === "entra") {
    return (
      <MsalProvider instance={getMsal()}>
        <EntraAuthBridge>{children}</EntraAuthBridge>
      </MsalProvider>
    );
  }
  return <DevAuthProvider>{children}</DevAuthProvider>;
}
