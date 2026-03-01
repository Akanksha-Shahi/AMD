import React from "react";

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, info) {
    console.error("App crashed:", error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="h-screen flex flex-col items-center justify-center text-red-400 bg-gray-900">
          <h1 className="text-3xl mb-4">⚠️ Something went wrong</h1>
          <p>Backend may be offline. Please refresh.</p>

          <button
            onClick={() => window.location.reload()}
            className="mt-6 px-6 py-2 bg-blue-600 rounded"
          >
            Reload
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
