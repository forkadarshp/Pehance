import { Badge as MantineBadge, BadgeProps as MantineBadgeProps } from "@mantine/core";
import { forwardRef } from "react";

export interface BadgeProps extends Omit<MantineBadgeProps, 'variant'> {
  variant?: "default" | "secondary" | "destructive" | "outline";
}

const Badge = forwardRef<HTMLDivElement, BadgeProps>(
  ({ variant = "default", ...props }, ref) => {
    // Map custom variants to Mantine variants
    let mantineVariant: MantineBadgeProps['variant'] = "filled";
    let mantineColor: string | undefined = undefined;

    switch (variant) {
      case "secondary":
        mantineVariant = "light";
        break;
      case "destructive":
        mantineVariant = "filled";
        mantineColor = "red";
        break;
      case "outline":
        mantineVariant = "outline";
        break;
      default:
        mantineVariant = "filled";
        mantineColor = "blue";
    }

    return (
      <MantineBadge
        variant={mantineVariant}
        color={mantineColor}
        ref={ref}
        {...props}
      />
    );
  }
);
Badge.displayName = "Badge";

export { Badge };
