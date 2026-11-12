const PULSE = "bg-muted/50 animate-pulse";

export function ProductCardSkeleton() {
  return (
    <div
      data-testid="product-skeleton"
      aria-hidden="true"
      className="product-card-skeleton"
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 10,
        borderStyle: "solid",
        borderWidth: 1,
        borderColor: "hsl(var(--line))",
        borderRadius: 0,
        padding: 10,
        backgroundColor: "hsl(var(--paper))",
      }}
    >
      <div className={PULSE} style={{ aspectRatio: "1 / 1", borderRadius: 0 }} />
      <div className={PULSE} style={{ height: 12, width: "70%", borderRadius: 0 }} />
      <div className={PULSE} style={{ height: 10, width: "40%", borderRadius: 0 }} />
    </div>
  );
}
