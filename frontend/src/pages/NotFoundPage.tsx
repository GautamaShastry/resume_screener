import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold">Page not found</h1>
      <Link to="/home" className="underline">
        Go home
      </Link>
    </div>
  );
}
