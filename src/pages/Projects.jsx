import { useState } from "react";
import api from "../services/api";

export default function Projects() {
  const [name, setName] = useState("");
  const [message, setMessage] = useState("");

  const createProject = async () => {
    try {
      await api.post("/projects", { name });
      setMessage("✅ Project Created");
      setName("");
    } catch {
      setMessage("❌ Failed to create project");
    }
  };

  return (
    <div className="p-6 space-y-4">
      <h2 className="text-2xl font-bold">Create Project</h2>

      <input
        className="p-2 bg-gray-800 rounded w-full"
        placeholder="Project Name"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />

      <button
        onClick={createProject}
        className="bg-indigo-600 px-4 py-2 rounded"
      >
        Create
      </button>

      <p>{message}</p>
    </div>
  );
}