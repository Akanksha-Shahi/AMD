export default function RiskResult({ result }) {
  if (!result) return null;

  const colors = {
    Low: "text-green-400",
    Medium: "text-orange-400",
    High: "text-red-500",
  };

  return (
    <div className="bg-gray-800 p-6 rounded mt-6">
      <h3 className="text-lg font-semibold mb-4">Analysis Result</h3>

      <p className={`text-2xl font-bold ${colors[result.risk_level]}`}>
        {result.risk_level} Risk
      </p>

      <p className="mt-2 text-gray-400">
        Confidence: {(result.confidence * 100).toFixed(2)}%
      </p>

      <div className="w-full bg-gray-700 rounded h-3 mt-4">
        <div
          className="bg-blue-500 h-3 rounded transition-all"
          style={{ width: `${result.confidence * 100}%` }}
        ></div>
      </div>
    </div>
  );
}