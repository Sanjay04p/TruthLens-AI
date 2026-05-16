import { FormEvent, useState } from "react";

interface ClaimFormProps {
  isLoading: boolean;
  onSubmit: (text: string) => Promise<void>;
}

export function ClaimForm({ isLoading, onSubmit }: ClaimFormProps) {
  const [claim, setClaim] = useState("");

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const normalizedClaim = claim.trim();
    if (!normalizedClaim) {
      return;
    }

    await onSubmit(normalizedClaim);
  };

  return (
    <form className="claim-form" onSubmit={handleSubmit}>
      <label className="field-label" htmlFor="claim-input">
        Enter a claim to verify
      </label>
      <textarea
        id="claim-input"
        className="claim-textarea"
        value={claim}
        onChange={(event) => setClaim(event.target.value)}
        placeholder="Example: A new study proved dark chocolate cures diabetes."
        rows={6}
      />
      <div className="form-footer">
        <p className="helper-text">
          TruthLens checks your claim against a local semantic cache and live web
          context from the FastAPI backend.
        </p>
        <button className="primary-button" type="submit" disabled={isLoading}>
          {isLoading ? "Verifying..." : "Verify Claim"}
        </button>
      </div>
    </form>
  );
}
