import { Link, Routes, Route, NavLink, useLocation } from "react-router-dom";
import { CatalogPage } from "./routes/CatalogPage";
import { CapturePage } from "./routes/CapturePage";
import { AssetDetailPage } from "./routes/AssetDetailPage";
import { SettingsPage } from "./routes/SettingsPage";
import { InboxPage } from "./routes/InboxPage";
import { ReviewPage } from "./routes/ReviewPage";
import { PlanningPage } from "./routes/PlanningPage";
import { ChatPage } from "./routes/ChatPage";
import { AnalyticsPage } from "./routes/AnalyticsPage";
import { ThemeToggle } from "./theme/ThemeToggle";

function Nav() {
  const { pathname } = useLocation();
  // The catalog route renders its own header (AppHeader) which already carries
  // the toggle; every other route gets it here so it is reachable everywhere.
  const showToggle = pathname !== "/";
  const linkClass = (active: boolean): string =>
    `${active ? "bg-primary text-primary-foreground" : "text-foreground"} focus-ring`;
  const linkStyle = (active: boolean): React.CSSProperties => ({
    padding: "6px 10px",
    borderRadius: 6,
    textDecoration: "none",
    fontSize: 13,
    fontWeight: active ? 600 : 400,
  });
  return (
    <nav
      className="bg-card border-border"
      style={{ display: "flex", gap: 8, padding: "12px 24px", borderBottomStyle: "solid", borderBottomWidth: 1, alignItems: "center" }}
    >
      <Link
        to="/"
        className="text-foreground focus-ring"
        style={{ fontWeight: 700, textDecoration: "none", marginRight: 16 }}
      >
        StorageGenie
      </Link>
      <NavLink to="/" end className={({ isActive }) => linkClass(isActive)} style={({ isActive }) => linkStyle(isActive)}>
        Catalog
      </NavLink>
      <NavLink to="/capture" className={({ isActive }) => linkClass(isActive)} style={({ isActive }) => linkStyle(isActive)}>
        Capture
      </NavLink>
      <NavLink to="/settings" className={({ isActive }) => linkClass(isActive)} style={({ isActive }) => linkStyle(isActive)}>
        Settings
      </NavLink>
      <NavLink to="/inbox" className={({ isActive }) => linkClass(isActive)} style={({ isActive }) => linkStyle(isActive)}>
        Inbox
      </NavLink>
      <NavLink to="/planning" className={({ isActive }) => linkClass(isActive)} style={({ isActive }) => linkStyle(isActive)}>
        Planning
      </NavLink>
      <NavLink to="/chat" className={({ isActive }) => linkClass(isActive)} style={({ isActive }) => linkStyle(isActive)}>
        Chat
      </NavLink>
      <NavLink to="/analytics" className={({ isActive }) => linkClass(isActive)} style={({ isActive }) => linkStyle(isActive)}>
        Analytics
      </NavLink>
      {showToggle ? <ThemeToggle /> : null}
      <span className="text-muted-foreground" style={{ marginLeft: "auto", fontSize: 11 }}>
        Phase 0 · local-first
      </span>
    </nav>
  );
}

export default function App() {
  return (
    <div className="bg-background text-foreground" style={{ minHeight: "100vh" }}>
      <Nav />
      <Routes>
        <Route path="/" element={<CatalogPage />} />
        <Route path="/capture" element={<CapturePage />} />
        <Route path="/assets/:id" element={<AssetDetailPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/inbox" element={<InboxPage />} />
        <Route path="/planning" element={<PlanningPage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/review/:candidateId" element={<ReviewPage />} />
      </Routes>
    </div>
  );
}
