import { Component, type ReactNode } from "react";

export class ErrorBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };

  static getDerivedStateFromError() {
    return { failed: true };
  }

  render() {
    if (this.state.failed) {
      return (
        <div role="alert" className="rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-800">
          This section failed to load.{" "}
          <button className="underline" onClick={() => this.setState({ failed: false })}>
            Try again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
