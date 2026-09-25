import type { WebAlternate } from "../api/types";

// SG-119 G2: the visible render of a label/web conflict. The label value stays
// the candidate field; each web value is shown here with its source. The full
// source URL rides the anchor's href/title only — never as visible text (the
// SG-118 id discipline). Renders nothing when there are no alternates.
export function WebAlternates({ alternates }: { alternates: WebAlternate[] }) {
  if (alternates.length === 0) return null;
  return (
    <section
      aria-label="Web alternates"
      className="border-border"
      style={{ marginTop: 18, borderTopStyle: "solid", borderTopWidth: 1, paddingTop: 12 }}
    >
      <h3 style={{ marginTop: 0 }}>Web alternates</h3>
      <p className="text-muted-foreground" style={{ fontSize: 12, marginTop: 0 }}>
        A label/web conflict keeps both values; the web value is shown here with its source, never silently dropped.
      </p>
      <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
        {alternates.map((alternate, index) => (
          <li
            key={`${alternate.field}-${index}`}
            data-testid={`web-alternate-${alternate.field}`}
            className="border-border"
            style={{ padding: "6px 0", borderBottomStyle: "solid", borderBottomWidth: 1, fontSize: 13 }}
          >
            <span style={{ fontWeight: 600 }}>{alternate.field}</span>
            {": "}
            <span>{String(alternate.value)}</span>
            {" · "}
            <span className="text-muted-foreground">{alternate.source_type ?? "unknown source"}</span>
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
              <span className="text-muted-foreground">
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
