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

// SG-330 R2 (D41 Midnight): the header speaks plain words — Add item is the
// one filled main-action button; the search names your things; the count box
// is gone (the live count sits under Your things, SG-330 R3).
export function AppHeader({ searchValue, onSearchChange }: AppHeaderProps) {
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
      data-testid="catalog-header"
      className="sg-header"
      style={{
        display: "flex",
        flexWrap: "wrap",
        alignItems: "center",
        gap: 12,
        rowGap: 8,
        padding: "10px 24px",
        borderBottomStyle: "solid",
        borderBottomWidth: 1,
        borderBottomColor: "hsl(var(--line))",
        backgroundColor: "hsl(var(--paper))",
        color: "hsl(var(--ink))",
      }}
    >
      {/* SG-105 G4: the global nav already carries the brand on this route;
           the Catalog header does not repeat it. */}
      {/* center stays reserved: category pills live in the toolbar, not here */}
      <div style={{ flex: 1 }} aria-hidden="true" />

      <input
        ref={searchRef}
        type="search"
        aria-label="Search your things"
        placeholder="Search your things"
        value={searchValue}
        onChange={(event) => onSearchChange(event.target.value)}
        className="sg-paper-control focus-ring sg-header-search"
        style={{
          padding: "6px 10px",
          borderRadius: 0,
          flex: "1 1 120px",
          minWidth: 0,
          maxWidth: 420,
          fontSize: 13,
        }}
      />
      <ThemeToggle />
      <Link
        to="/capture"
        aria-label="Add item"
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
          backgroundColor: "hsl(var(--primary))",
          color: "hsl(var(--primary-foreground))",
        }}
      >
        <Upload size={16} aria-hidden="true" />
        <span className="sg-import-label">Add item</span>
      </Link>
      {importOpen ? (
        <AssetImportModal householdId={householdId} onClose={() => setImportOpen(false)} />
      ) : null}
    </div>
  );
}
