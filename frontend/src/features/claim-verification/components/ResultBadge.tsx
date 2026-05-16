interface ResultBadgeProps {
  label: string;
}

const badgeClassByLabel: Record<string, string> = {
  Real: "badge badge-real",
  Fake: "badge badge-fake",
  Unverified: "badge badge-unverified",
  Error: "badge badge-error"
};

export function ResultBadge({ label }: ResultBadgeProps) {
  return (
    <span className={badgeClassByLabel[label] || "badge badge-neutral"}>
      {label}
    </span>
  );
}
