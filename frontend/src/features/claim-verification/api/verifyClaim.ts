import { postJson } from "../../../services/api/http";
import type {
  ClaimPayload,
  VerificationResponse
} from "../../../types/verification";

export function verifyClaim(payload: ClaimPayload) {
  return postJson<VerificationResponse>("/verify-text", payload);
}
