import { ClaimForm } from "../components/ClaimForm";
import { VerificationResult } from "../components/VerificationResult";
import { useClaimVerification } from "../hooks/useClaimVerification";

export function ClaimVerifierPage() {
  const { data, error, isLoading, submitClaim } = useClaimVerification();

  return (
    <main className="page-shell">
      <section className="hero-card">
        <div className="hero-copy">
          <p className="hero-kicker">TruthLens AI</p>
          <h1>Fast claim verification with hybrid AI evidence scoring.</h1>
          <p className="hero-description">
            Submit any text claim and inspect how the backend classifies it using
            semantic cache hits, live web context, and LLM certainty.
          </p>
        </div>

        <div className="hero-stat">
          <span>Endpoint</span>
          <strong>POST /verify-text</strong>
          <p>Powered by your FastAPI service in `backend_server/main.py`.</p>
        </div>
      </section>

      <section className="workspace-grid">
        <div className="panel">
          <div className="panel-header">
            <h2>Analyze Claim</h2>
            <p>Paste a sentence, headline, or viral statement to inspect it.</p>
          </div>
          <ClaimForm isLoading={isLoading} onSubmit={submitClaim} />
        </div>

        <div className="status-column">
          {isLoading ? (
            <section className="panel status-panel">
              <p className="eyebrow">Pipeline Status</p>
              <h2>Verification in progress</h2>
              <p>
                The frontend is waiting for a response from the FastAPI backend.
              </p>
            </section>
          ) : null}

          {error ? (
            <section className="panel status-panel error-panel">
              <p className="eyebrow">Request Error</p>
              <h2>We could not verify that claim</h2>
              <p>{error}</p>
            </section>
          ) : null}

          {data ? (
            <VerificationResult result={data} />
          ) : (
            <section className="panel status-panel empty-panel">
              <p className="eyebrow">Results</p>
              <h2>No claim submitted yet</h2>
              <p>
                Once you run a verification, the result label, confidence, and
                reasoning will appear here.
              </p>
            </section>
          )}
        </div>
      </section>
    </main>
  );
}
