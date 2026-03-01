import { useEffect, useState } from "react";
import api from "../services/api";

export default function Analytics() {
  const [data, setData] = useState([]);

  useEffect(() => {
    api.get("/analytics")
      .then((res) => setData(res.data))
      .catch(() => console.log("error"));
  }, []);

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">
        Analysis Reports
      </h2>

      <div className="space-y-3">
        {data.map((item, i) => (
          <div key={i} className="bg-gray-800 p-4 rounded">
            <p>Project: {item.project}</p>
            <p>Risk: {item.risk}</p>
          </div>
        ))}
      </div>
    </div>
  );
}