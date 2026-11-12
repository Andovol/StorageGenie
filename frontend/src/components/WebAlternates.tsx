import type { WebAlternate } from "../api/types";

function plainAlternateField(field: string): string {
  const lower = field.toLowerCase();
  if (lower.includes("display_name") || lower === "name") return "Name";
  if (lower.includes("quantity")) return "Amount";
  if (lower.includes("expiry")) return "Expiry date";
  if (lower.includes("classification") || lower.includes("category")) return "Shelf life";
  return field.replace(/[_.:]+/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function plainAlternateSource(sourceType: string | null): string {
  if (!sourceType) return "Source not named";
  if (sourceType.startsWith("web:")) return "Web";
  return sourceType.replace(/[_.:]+/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

// SG-119 G2: the visible render of a label/web conflict. The label value stays
// the candidate field; each web value is shown here with its source. The full
// source URL rides the anchor's href/title only — never as visible text (the
// SG-118 id discipline). Renders nothing when there are no alternates.
export function WebAlternates({ alternates }: { alternates: WebAlternate[] }) {
  if (alternates.length === 0) return null;
  return (
    <section
      aria-label="Web alternates"
      style={{ marginTop: 18, borderTopStyle: "solid", borderTopWidth: 1, borderColor: "hsl(var(--line))", paddingTop: 12 }}
    >
      <h3 style={{ marginTop: 0 }}>Web alternates</h3>
      <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
        {alternates.map((alternate, index) => (
          <li
            key={`${alternate.field}-${index}`}
            data-testid={`web-alternate-${alternate.field}`}
            style={{ padding: "6px 0", borderBottomStyle: "solid", borderBottomWidth: 1, borderColor: "hsl(var(--line))", fontSize: 13 }}
          >
            <span style={{ fontWeight: 600 }}>{plainAlternateField(alternate.field)}</span>
            {": "}
            <span>{String(alternate.value)}</span>
            {" · "}
            <span style={{ color: "hsl(var(--ink-muted))" }}>{plainAlternateSource(alternate.source_type)}</span>
            {alternate.source_url ? (
              <>
                {" · "}
                <a
                  className="text-link focus-ring"
                  href={alternate.source_url}
                  title={alternate.source_url}
                  target="_blank"
                  rel="noreferrer"
                >
                  source
                </a>
              </>
            ) : null}
            {alternate.retrieved_at ? (
              <span style={{ color: "hsl(var(--ink-muted))" }}>
                {" · "}
                {alternate.retrieved_at}
              </span>
            ) : null}
          </li>
        ))}
      </ul>
    </section>
  );
}
