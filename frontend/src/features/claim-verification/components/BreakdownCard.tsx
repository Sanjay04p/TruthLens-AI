import type { TierTwoBreakdown } from "../../../types/verification";

interface BreakdownCardProps {
  breakdown: TierTwoBreakdown;
}

const items = [
  { key: "historical", label: "Historical Similarity" },
  { key: "credibility", label: "Source Credibility" },
  { key: "web_match", label: "Web Match" },
  { key: "certainty", label: "LLM Certainty" }
] as const;

export function BreakdownCard({ breakdown }: BreakdownCardProps) {
  return (
    <section className="panel">
      <div className="panel-header">
        <h3>Confidence Breakdown</h3>
        <p>Weighted signals used by the tier-2 verification pipeline.</p>
      </div>
      <div className="metric-grid">
        {items.map((item) => {
          const value = breakdown[item.key];

          return (
            <article className="metric-card" key={item.key}>
              <span>{item.label}</span>
              <strong>{value}</strong>
            </article>
          );
        })}
      </div>
    </section>
  );
}
