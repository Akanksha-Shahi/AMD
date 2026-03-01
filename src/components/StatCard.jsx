export default function StatCard({ title, value }) {
  return (
    <div className="bg-gray-800 p-5 rounded shadow">
      <h3 className="text-gray-400 text-sm">{title}</h3>
      <p className="text-2xl font-bold mt-2">{value}</p>
    </div>
  );
}