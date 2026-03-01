import { useEffect, useState } from "react";
import api from "../services/api";
import StatCard from "../components/StatCard";
import Loader from "../components/Loader";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const res = await api.get("/analytics/summary");

        // safety fallback
        setData({
          total_projects: res.data?.total_projects ?? 0,
          total_analyses: res.data?.total_analyses ?? 0,
          risk_distribution:
            res.data?.risk_distribution || {
              Low: 0,
              Medium: 0,
              High: 0,
            },
        });

        setError("");
      } catch (err) {
        console.error("Backend Error:", err);
        setError("Backend not reachable");
      } finally {
        setLoading(false);
      }
    };

    fetchSummary();
  }, []);

  // =====================
  // Loading Screen
  // =====================
  if (loading) return <Loader />;

  // =====================
  // Error Screen
  // =====================
  if (error) {
    return (
      <div className="flex items-center justify-center h-full text-red-400 text-xl">
        ❌ {error}. Please start backend on port 8000
      </div>
    );
  }

  // =====================
  // Chart Data
  // =====================
  const chartData = Object.entries(
    data?.risk_distribution || {}
  ).map(([key, val]) => ({
    name: key,
    value: val,
  }));

  const COLORS = ["#22c55e", "#f97316", "#ef4444"];

  // =====================
  // UI
  // =====================
  return (
    <div className="p-6 space-y-6">
      <h2 className="text-3xl font-bold text-white">
        RTL Risk AI Dashboard
      </h2>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard title="Total Projects" value={data.total_projects} />
        <StatCard title="Total Analyses" value={data.total_analyses} />
      </div>

      {/* Chart */}
      <div className="bg-gray-800 p-6 rounded-xl shadow-lg">
        <h3 className="mb-4 text-lg font-semibold text-white">
          Risk Distribution
        </h3>

        {chartData.length === 0 ? (
          <p className="text-gray-400">
            No analysis data available yet.
          </p>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={chartData}
                dataKey="value"
                nameKey="name"
                label
              >
                {chartData.map((_, i) => (
                  <Cell
                    key={i}
                    fill={COLORS[i % COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}