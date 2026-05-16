import { useState } from "react";
import { verifyClaim } from "../api/verifyClaim";
import type { VerificationResponse } from "../../../types/verification";

interface ClaimVerificationState {
  data: VerificationResponse | null;
  error: string | null;
  isLoading: boolean;
}

const initialState: ClaimVerificationState = {
  data: null,
  error: null,
  isLoading: false
};

export function useClaimVerification() {
  const [state, setState] = useState<ClaimVerificationState>(initialState);

  const submitClaim = async (text: string) => {
    setState({
      data: null,
      error: null,
      isLoading: true
    });

    try {
      const data = await verifyClaim({ text });
      setState({
        data,
        error: null,
        isLoading: false
      });
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Something went wrong.";

      setState({
        data: null,
        error: message,
        isLoading: false
      });
    }
  };

  return {
    ...state,
    submitClaim
  };
}
