import { Moon, Sun } from "lucide-react";
import { useTheme } from "./ThemeProvider";

export function ThemeToggle() {
  const { resolvedTheme, setTheme } = useTheme();
  const next = resolvedTheme === "dark" ? "light" : "dark";
  const label = `Switch to ${next} theme`;

  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      onClick={() => setTheme(next)}
      className="bg-card text-foreground border-border focus-ring"
      style={{
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 6,
        borderRadius: 6,
        borderStyle: "solid",
        borderWidth: 1,
        cursor: "pointer",
      }}
    >
      {resolvedTheme === "dark" ? (
        <Sun size={18} aria-hidden="true" />
      ) : (
        <Moon size={18} aria-hidden="true" />
      )}
    </button>
  );
}
