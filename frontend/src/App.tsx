import { Link, Routes, Route, NavLink } from "react-router-dom";
import { CatalogPage } from "./routes/CatalogPage";
import { CapturePage } from "./routes/CapturePage";
import { AssetDetailPage } from "./routes/AssetDetailPage";
import { SettingsPage } from "./routes/SettingsPage";

function Nav() {
  const linkStyle = (active: boolean): React.CSSProperties => ({
    padding: "6px 10px",
    borderRadius: 6,
    textDecoration: "none",
    color: active ? "white" : "#374151",
    background: active ? "#111827" : "transparent",
    fontSize: 13,
    fontWeight: active ? 600 : 400,
  });
  return (
    <nav style={{ display: "flex", gap: 8, padding: "12px 24px", borderBottom: "1px solid #e5e7eb", alignItems: "center", background: "#f9fafb" }}>
      <Link to="/" style={{ fontWeight: 700, textDecoration: "none", color: "#111827", marginRight: 16 }}>
        StorageGenie
      </Link>
      <NavLink to="/" end style={({ isActive }) => linkStyle(isActive)}>
        Catalog
      </NavLink>
      <NavLink to="/capture" style={({ isActive }) => linkStyle(isActive)}>
        Capture
      </NavLink>
      <NavLink to="/settings" style={({ isActive }) => linkStyle(isActive)}>
        Settings
      </NavLink>
      <span style={{ marginLeft: "auto", fontSize: 11, color: "#9ca3af" }}>Phase 0 · local-first</span>
    </nav>
  );
}

export default function App() {
  return (
    <div style={{ minHeight: "100vh", background: "white", color: "#111827" }}>
      <Nav />
      <Routes>
        <Route path="/" element={<CatalogPage />} />
        <Route path="/capture" element={<CapturePage />} />
        <Route path="/assets/:id" element={<AssetDetailPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Routes>
    </div>
  );
}
