import type { HTMLAttributes } from "react";

type BadgeVariant = "default" | "secondary" | "outline" | "warning";

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
}

export function Badge({ variant = "secondary", className = "", ...props }: BadgeProps) {
  return (
    <span
      className={["ui-badge", `ui-badge--${variant}`, className].filter(Boolean).join(" ")}
      {...props}
    />
  );
}
