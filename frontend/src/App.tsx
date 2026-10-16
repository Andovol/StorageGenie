import { useState } from "react";
import { Link, Routes, Route, NavLink, useLocation } from "react-router-dom";
import { Upload } from "lucide-react";
import { CatalogPage } from "./routes/CatalogPage";
import { CapturePage } from "./routes/CapturePage";
import { AssetDetailPage } from "./routes/AssetDetailPage";
import { SettingsPage } from "./routes/SettingsPage";
import { InboxPage } from "./routes/InboxPage";
import { ReviewPage } from "./routes/ReviewPage";
import { PlanningPage } from "./routes/PlanningPage";
import { ChatPage } from "./routes/ChatPage";
import { AnalyticsPage } from "./routes/AnalyticsPage";
import { ExpiryPage } from "./routes/ExpiryPage";
import { ThemeToggle } from "./theme/ThemeToggle";
import { AssetImportModal } from "./components/shell/AssetImportModal";
import { HouseholdSelector } from "./components/HouseholdSelector";
import { CONTROL_STYLE, THEMED_CONTROL_CLASS } from "./components/shell/CatalogToolbar";
import { useReviewTasks } from "./hooks/useAssets";
import { HouseholdProvider, useHouseholdContext } from "./hooks/HouseholdContext";

const NAV_DESTINATIONS: readonly { to: string; label: string; end?: boolean }[] = [
  { to: "/", label: "Catalog", end: true },
  { to: "/capture", label: "Capture" },
  { to: "/inbox", label: "Inbox" },
  { to: "/planning", label: "Planning" },
  { to: "/chat", label: "Chat" },
  { to: "/analytics", label: "Analytics" },
  { to: "/expiry", label: "Expiry" },
  { to: "/settings", label: "Settings" },
];

function Nav() {
  const { pathname } = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);
  const [importOpen, setImportOpen] = useState(false);
  // SG-196 G1: the nav reads the shared household context; its selector is the
  // one control that reaches every route in the same session.
  const {
    households,
    isError: householdsIsError,
    error: householdsError,
    householdId,
    setHouseholdId,
  } = useHouseholdContext();
  const effectiveHousehold = householdId || households?.[0]?.id || "";
  // SG-196 G3: the badge reads the same ["review-tasks", household] entry
  // InboxPage uses, so it counts the LOADED open tasks and shares one cache.
  // While there is no data (loading / error / no household) NO badge renders —
  // a zero there would be a false completion.
  const { data: reviewTasks } = useReviewTasks(effectiveHousehold);
  const openTaskCount = reviewTasks?.items.filter((task) => task.status !== "resolved").length;
  // The catalog route renders its own header (AppHeader) which already carries
  // the toggle; every other route gets it here so it is reachable everywhere.
  const showToggle = pathname !== "/";
  const showImport = pathname !== "/";
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
      style={{
        display: "flex",
        flexWrap: "wrap",
        gap: 8,
        padding: "12px 24px",
        borderBottomStyle: "solid",
        borderBottomWidth: 1,
        alignItems: "center",
      }}
    >
      <Link
        to="/"
        className="text-foreground focus-ring"
        style={{ fontWeight: 700, textDecoration: "none", marginRight: 16 }}
      >
        StorageGenie
      </Link>
      <button
        type="button"
        className="nav-menu-toggle bg-card text-foreground border-border focus-ring"
        aria-expanded={menuOpen}
        aria-controls="sg-nav-menu"
        onClick={() => setMenuOpen((open) => !open)}
        style={{
          padding: "6px 10px",
          borderRadius: 6,
          borderStyle: "solid",
          borderWidth: 1,
          fontSize: 13,
          cursor: "pointer",
        }}
      >
        Menu
      </button>
      <div id="sg-nav-menu" className="nav-menu" data-open={menuOpen ? "true" : "false"}>
        {NAV_DESTINATIONS.map((destination) => {
          const badgeCount = destination.to === "/inbox" ? openTaskCount : undefined;
          return (
            <NavLink
              key={destination.to}
              to={destination.to}
              end={destination.end}
              aria-label={
                badgeCount !== undefined ? `Inbox, ${badgeCount} open review tasks` : undefined
              }
              className={({ isActive }) => linkClass(isActive)}
              style={({ isActive }) => linkStyle(isActive)}
            >
              {destination.label}
              {badgeCount !== undefined ? (
                <span
                  data-testid="inbox-open-count"
                  aria-hidden="true"
                  style={{
                    marginLeft: 6,
                    padding: "0 6px",
                    borderRadius: 999,
                    borderStyle: "solid",
                    borderWidth: 1,
                    fontSize: 11,
                  }}
                >
                  {badgeCount}
                </span>
              ) : null}
            </NavLink>
          );
        })}
      </div>
      {showToggle ? <ThemeToggle /> : null}
      <HouseholdSelector
        value={effectiveHousehold}
        onChange={setHouseholdId}
        households={households}
        selectStyle={{ ...CONTROL_STYLE, maxWidth: "100%" }}
        selectClassName={THEMED_CONTROL_CLASS}
      />
      {householdsIsError ? (
        <div role="alert" style={{ fontSize: 12 }}>
          Could not load households: {String(householdsError)}
        </div>
      ) : null}
      {showImport ? (
        <Link
          to="/capture"
          onClick={(event) => {
            event.preventDefault();
            setImportOpen(true);
          }}
          className="bg-primary text-primary-foreground focus-ring"
          style={{
            padding: "6px 12px",
            borderRadius: 6,
            textDecoration: "none",
            fontWeight: 600,
            fontSize: 13,
            display: "inline-flex",
            alignItems: "center",
            gap: 6,
          }}
        >
          <Upload size={16} aria-hidden="true" />
          Import Asset
        </Link>
      ) : null}
      <span className="text-muted-foreground" style={{ marginLeft: "auto", fontSize: 11 }}>
        Phase 0 · local-first
      </span>
      {importOpen ? (
        <AssetImportModal householdId={effectiveHousehold} onClose={() => setImportOpen(false)} />
      ) : null}
    </nav>
  );
}

export default function App() {
  return (
    <HouseholdProvider>
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
          <Route path="/expiry" element={<ExpiryPage />} />
          <Route path="/review/:candidateId" element={<ReviewPage />} />
        </Routes>
      </div>
    </HouseholdProvider>
  );
}
