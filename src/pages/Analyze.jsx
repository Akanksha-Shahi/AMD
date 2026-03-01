import { useState, useEffect } from "react";
import api from "../services/api";
import Loader from "../components/Loader";
import RiskResult from "../components/RiskResult";
import FeatureChart from "../components/FeatureChart";

export default function Analyze() {
  const [file, setFile] = useState(null);
  const [pid, setPid] = useState("");
  const [projects, setProjects] = useState([]);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [features, setFeatures] = useState([]);
  const [status, setStatus] = useState("");

  // ================= LOAD DATA =================
  useEffect(() => {
    // Load projects
    api.get("/projects")
      .then(res => setProjects(res.data))
      .catch(() => console.log("Project fetch failed"));

    // Load feature importance
    api.get("/analytics/model-importance")
      .then(res => {
        const arr = Object.entries(res.data.feature_importance)
          .map(([k, v]) => ({ name: k, value: v }));
        setFeatures(arr);
      });
  }, []);

  // ================= ANALYZE =================
  const handleAnalyze = async () => {
    if (!file || !pid) {
      setStatus("❌ Select project and file");
      return;
    }

    const form = new FormData();
    form.append("project_id", pid);
    form.append("file", file);

    setLoading(true);
    setStatus("🚀 Running AI Analysis...");

    try {
      const res = await api.post("/analyze/", form);
      setResult(res.data);
      setStatus("✅ Analysis Completed");
    } catch {
      setStatus("❌ Analysis Failed");
    } finally {
      setLoading(false);
    }
  };

  // ================= UI =================
  return (
    <div className="p-6 space-y-6 max-w-4xl">
      <h2 className="text-3xl font-bold">
        AI RTL Risk Analyzer
      </h2>

      {/* PROJECT SELECT */}
      <div>
        <label className="block mb-2">Select Project</label>

        <select
          value={pid}
          onChange={(e) => setPid(e.target.value)}
          className="w-full p-3 bg-gray-800 rounded"
        >
          <option value="">Choose Project</option>
          {projects.map(p => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
      </div>

      {/* FILE UPLOAD */}
      <div>
        <label className="block mb-2">
          Upload RTL File (.v)
        </label>

        <input
          type="file"
          accept=".v"
          onChange={(e) => setFile(e.target.files[0])}
          className="w-full"
        />
      </div>

      {/* ANALYZE BUTTON */}
      <button
        onClick={handleAnalyze}
        className="bg-indigo-600 hover:bg-indigo-700 px-6 py-3 rounded font-semibold"
      >
        Analyze RTL
      </button>

      {/* STATUS */}
      {status && (
        <div className="text-indigo-400 font-medium">
          {status}
        </div>
      )}

      {/* LOADER */}
      {loading && <Loader />}

      {/* RESULT */}
      {result && (
        <div className="bg-gray-900 p-5 rounded">
          <RiskResult result={result} />
        </div>
      )}

      {/* FEATURE IMPORTANCE */}
      {features.length > 0 && (
        <div className="bg-gray-900 p-5 rounded">
          <h3 className="mb-3 font-semibold">
            Model Feature Importance
          </h3>
          <FeatureChart data={features} />
        </div>
      )}
    </div>
  );
}