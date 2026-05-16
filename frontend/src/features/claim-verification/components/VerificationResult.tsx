import type { VerificationResponse } from "../../../types/verification";
import { BreakdownCard } from "./BreakdownCard";
import { ResultBadge } from "./ResultBadge";

interface VerificationResultProps {
  result: VerificationResponse;
}

export function VerificationResult({ result }: VerificationResultProps) {
  const isTierOne = result.tier === 1;

  return (
    <div className="results-stack">
      <section className="panel result-panel">
        <div className="panel-header">
          <div>
            <p className="eyebrow">Verification Result</p>
            <h2>Claim assessment complete</h2>
          </div>
          <ResultBadge label={result.label} />
        </div>

        <div className="result-grid">
          <article className="metric-card">
            <span>Pipeline Tier</span>
            <strong>{result.tier}</strong>
          </article>
          <article className="metric-card">
            <span>{isTierOne ? "Similarity Confidence" : "Final Confidence"}</span>
            <strong>
              {isTierOne ? `${Math.round(result.confidence * 100)}%` : result.confidence_score || "N/A"}
            </strong>
          </article>
        </div>

        <div className="reason-block">
          <p className="eyebrow">Reasoning</p>
          <p>{result.reason}</p>
        </div>
      </section>

      {!isTierOne && result.breakdown ? (
        <BreakdownCard breakdown={result.breakdown} />
      ) : null}
    </div>
  );
}
