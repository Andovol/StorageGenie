import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { Upload } from "lucide-react";
import { ThemeToggle } from "../../theme/ThemeToggle";
import { AssetImportModal } from "./AssetImportModal";
import { useHouseholdContext } from "../../hooks/HouseholdContext";

type AppHeaderProps = {
  loadedCount: number;
  searchValue: string;
  onSearchChange: (value: string) => void;
};

export function AppHeader({ loadedCount, searchValue, onSearchChange }: AppHeaderProps) {
  const searchRef = useRef<HTMLInputElement>(null);
  // SG-198 G1: the import-modal id comes from the shared household context;
  // preserved behavior: localStorage-first with the first-household fallback,
  // now derived (and persisted) once in HouseholdProvider — same accepted id,
  // no branch or wording change.
  const { householdId } = useHouseholdContext();
  const [importOpen, setImportOpen] = useState(false);

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
        flexWrap: "wrap",
        alignItems: "center",
        gap: 12,
        rowGap: 8,
        padding: "10px 24px",
        borderBottomStyle: "solid",
        borderBottomWidth: 1,
      }}
    >
      {/* SG-105 G4: the global nav already carries the brand on this route;
          the Catalog header does not repeat it. */}
      <span
        className="bg-card-muted text-muted-foreground"
        aria-label={`Total loaded items: ${loadedCount}`}
        title="Items loaded on this page, not the household total"
        style={{ fontSize: 12, padding: "2px 8px", borderRadius: 999 }}
      >
        Loaded: {loadedCount} {loadedCount === 1 ? "item" : "items"}
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
          flex: "1 1 180px",
          minWidth: 180,
          maxWidth: 420,
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
