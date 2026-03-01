import { BrowserRouter, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";

import Dashboard from "./pages/Dashboard";
import Projects from "./pages/Projects";
import CreateProject from "./pages/CreateProject";
import Analyze from "./pages/Analyze";
import Analytics from "./pages/Analytics";

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen bg-gray-900 text-white">
        
        {/* Sidebar */}
        <Sidebar />

        {/* Main Content */}
        <main className="flex-1 p-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />

            <Route path="/projects" element={<Projects />} />

            {/* ✅ IMPORTANT */}
            <Route path="/create-project" element={<CreateProject />} />

            <Route path="/analyze" element={<Analyze />} />

            <Route path="/analytics" element={<Analytics />} />
          </Routes>
        </main>

      </div>
    </BrowserRouter>
  );
}