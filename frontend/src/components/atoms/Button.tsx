import { Button as MantineButton, ButtonProps as MantineButtonProps } from "@mantine/core";
import { forwardRef } from "react";

export interface ButtonProps extends Omit<MantineButtonProps, 'variant' | 'size'> {
  variant?: "default" | "ghost";
  size?: "default" | "lg" | "icon" | "sm";
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = "default", size = "default", ...props }, ref) => {
    // Map custom variants to Mantine variants
    const mantineVariant = variant === "ghost" ? "subtle" : "filled";
    
    // Map custom sizes to Mantine sizes
    const mantineSize = size === "lg" ? "lg" : size === "icon" ? "sm" : "md";

    return (
      <MantineButton
        variant={mantineVariant}
        size={mantineSize}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button };
