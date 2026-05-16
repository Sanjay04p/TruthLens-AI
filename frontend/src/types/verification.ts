export interface ClaimPayload {
  text: string;
}

export interface TierOneVerification {
  tier: 1;
  label: string;
  confidence: number;
  reason: string;
}

export interface TierTwoBreakdown {
  historical: number;
  credibility: number;
  web_match: number;
  certainty: number;
}

export interface TierTwoVerification {
  tier: 2;
  label: string;
  confidence_score?: string;
  breakdown?: TierTwoBreakdown;
  reason: string;
}

export type VerificationResponse = TierOneVerification | TierTwoVerification;
