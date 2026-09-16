import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { Upload } from "lucide-react";
import { ThemeToggle } from "../../theme/ThemeToggle";
import { AssetImportModal } from "./AssetImportModal";
import { useHouseholds } from "../../hooks/useAssets";

type AppHeaderProps = {
  loadedCount: number;
  searchValue: string;
  onSearchChange: (value: string) => void;
};

export function AppHeader({ loadedCount, searchValue, onSearchChange }: AppHeaderProps) {
  const searchRef = useRef<HTMLInputElement>(null);
  const { data: households } = useHouseholds();
  const [importOpen, setImportOpen] = useState(false);
  const householdId =
    (typeof localStorage !== "undefined" ? localStorage.getItem("household_id") : "") ||
    households?.[0]?.id ||
    "";

  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && (event.key === "k" || event.key === "K")) {
        const field = searchRef.current;
        if (!field) return;
        event.preventDefault();
        field.focus();
        field.select();
      }
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, []);

  return (
    <div
      className="bg-card border-border"
      style={{
        display: "flex",
        alignItems: "center",
        gap: 12,
        padding: "10px 24px",
        borderBottomStyle: "solid",
        borderBottomWidth: 1,
      }}
    >
      <Link
        to="/"
        className="text-foreground focus-ring"
        style={{ fontWeight: 700, textDecoration: "none", marginRight: 4 }}
      >
        StorageGenie
      </Link>
      <span
        className="bg-card-muted text-muted-foreground"
        aria-label={`Total loaded items: ${loadedCount}`}
        title="Items loaded on this page, not the household total"
        style={{ fontSize: 12, padding: "2px 8px", borderRadius: 999 }}
      >
        Total: {loadedCount} {loadedCount === 1 ? "item" : "items"}
      </span>

      {/* center stays reserved: category pills live in the toolbar, not here */}
      <div style={{ flex: 1 }} aria-hidden="true" />

      <input
        ref={searchRef}
        type="search"
        aria-label="Search catalog"
        placeholder="Search…"
        value={searchValue}
        onChange={(event) => onSearchChange(event.target.value)}
        className="bg-background text-foreground border-border focus-ring"
        style={{
          padding: "6px 10px",
          borderRadius: 6,
          borderStyle: "solid",
          borderWidth: 1,
          minWidth: 200,
          fontSize: 13,
        }}
      />
      <ThemeToggle />
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
      {importOpen ? (
        <AssetImportModal householdId={householdId} onClose={() => setImportOpen(false)} />
      ) : null}
    </div>
  );
}
