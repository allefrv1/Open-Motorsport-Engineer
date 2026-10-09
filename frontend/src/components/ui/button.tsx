import { forwardRef, type ButtonHTMLAttributes } from "react";

type ButtonVariant = "default" | "secondary" | "outline" | "ghost";
type ButtonSize = "default" | "sm" | "lg" | "icon";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  function Button(
    { variant = "default", size = "default", className = "", type = "button", ...props },
    ref,
  ) {
    return (
      <button
        ref={ref}
        type={type}
        className={["ui-button", `ui-button--${variant}`, `ui-button--${size}`, className]
          .filter(Boolean)
          .join(" ")}
        {...props}
      />
    );
  },
);
