import { useState } from "react";
import api from "../services/api";

export default function CreateProject() {
  const [name, setName] = useState("");
  const [msg, setMsg] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const res = await api.post("/projects/", {
        name,
        filename: "sample.v",
      });

      localStorage.setItem("project_id", res.data.id);
      setMsg(`Project created. ID: ${res.data.id}`);
      setName("");
    } catch {
      setMsg("Error creating project");
    }
  };

  return (
    <div className="p-6 max-w-lg">
      <h2 className="text-2xl font-bold mb-4">Create Project</h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
          placeholder="Project Name"
          className="w-full p-3 bg-gray-800 rounded"
        />

        <button className="bg-blue-600 px-4 py-2 rounded">
          Create
        </button>
      </form>

      {msg && <p className="mt-4 text-green-400">{msg}</p>}
    </div>
  );
}