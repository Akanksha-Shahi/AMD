import { Link } from "react-router-dom";

export default function Sidebar() {
  return (
    <div className="w-64 bg-gray-950 p-6 space-y-6">
      <h1 className="text-2xl font-bold text-indigo-400">
        RTL Risk AI
      </h1>

      <nav className="space-y-4">
        <Link to="/">Dashboard</Link>
        <Link to="/projects">Projects</Link>
        <Link to="/create-project">Create Project</Link>
        <Link to="/analyze">Analyze RTL</Link>
        <Link to="/analytics">Analytics</Link>
      </nav>
    </div>
  );
}