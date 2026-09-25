const PULSE = "bg-muted/50 animate-pulse";

export function ProductCardSkeleton() {
  return (
    <div
      data-testid="product-skeleton"
      aria-hidden="true"
      className="product-card-skeleton bg-card border-border"
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 10,
        borderStyle: "solid",
        borderWidth: 1,
        borderRadius: 12,
        padding: 10,
      }}
    >
      <div className={PULSE} style={{ aspectRatio: "1 / 1", borderRadius: 8 }} />
      <div className={PULSE} style={{ height: 12, width: "70%", borderRadius: 4 }} />
      <div className={PULSE} style={{ height: 10, width: "40%", borderRadius: 4 }} />
    </div>
  );
}
