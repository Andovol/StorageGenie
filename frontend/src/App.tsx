import { useState } from "react";
import { Link, Routes, Route, NavLink, useLocation } from "react-router-dom";
import { Upload } from "lucide-react";
import { CatalogPage } from "./routes/CatalogPage";
import { PantryPage } from "./routes/PantryPage";
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
import { useReviewTasks } from "./hooks/useAssets";
import { HouseholdProvider, useHouseholdContext } from "./hooks/HouseholdContext";

const NAV_DESTINATIONS: readonly { to: string; label: string; end?: boolean }[] = [
  { to: "/", label: "Catalog", end: true },
  { to: "/pantry", label: "Pantry" },
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
  // SG-196 G1 / SG-208 D-13: the nav reads the shared household context's
  // resolved household; it carries no switching control.
  const {
    households,
    isError: householdsIsError,
    householdId,
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
    `${active ? "bg-primary text-primary-foreground" : ""} focus-ring`;
  const linkStyle = (active: boolean): React.CSSProperties => ({
    padding: "6px 10px",
    borderRadius: 0,
    textDecoration: active ? "underline" : "none",
    textUnderlineOffset: 3,
    fontSize: 13,
    fontWeight: active ? 600 : 400,
    backgroundColor: active ? "hsl(var(--ink))" : "transparent",
    color: active ? "hsl(var(--paper))" : "hsl(var(--ink))",
    border: active ? "none" : "1px solid transparent",
  });
  return (
    <nav
      style={{
        display: "flex",
        flexWrap: "wrap",
        gap: 8,
        padding: "12px 24px",
        borderBottomStyle: "solid",
        borderBottomWidth: 1,
        borderBottomColor: "hsl(var(--line))",
        backgroundColor: "hsl(var(--paper))",
        color: "hsl(var(--ink))",
        alignItems: "center",
      }}
    >
      <Link
        to="/"
        className="focus-ring"
        style={{ fontWeight: 700, textDecoration: "none", marginRight: 16, color: "hsl(var(--ink))", fontSize: 20 }}
      >
        StorageGenie
      </Link>
      <button
        type="button"
        className="focus-ring"
        aria-expanded={menuOpen}
        aria-controls="sg-nav-menu"
        onClick={() => setMenuOpen((open) => !open)}
        style={{
          padding: "6px 10px",
          borderRadius: 0,
          borderStyle: "solid",
          borderWidth: 1,
          borderColor: "hsl(var(--line))",
          backgroundColor: "hsl(var(--paper))",
          color: "hsl(var(--ink))",
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
                    borderRadius: 0,
                    borderStyle: "solid",
                    borderWidth: 1,
                    borderColor: "currentColor",
                    fontSize: 13,
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
      {householdsIsError ? (
        <div role="alert" style={{ fontSize: 13 }}>
          Could not load households.
        </div>
      ) : null}
      {showImport ? (
        <Link
          to="/capture"
          onClick={(event) => {
            event.preventDefault();
            setImportOpen(true);
          }}
          className="focus-ring"
          style={{
            padding: "6px 12px",
            borderRadius: 0,
            textDecoration: "none",
            fontWeight: 600,
            fontSize: 13,
            display: "inline-flex",
            alignItems: "center",
            gap: 6,
            backgroundColor: "hsl(var(--ink))",
            color: "hsl(var(--paper))",
          }}
        >
          <Upload size={16} aria-hidden="true" />
          Import Asset
        </Link>
      ) : null}
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
          <Route path="/pantry" element={<PantryPage />} />
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
