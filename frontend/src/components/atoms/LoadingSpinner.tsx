import { Loader } from "@mantine/core";

export const LoadingSpinner = ({ className, size = "md" }: { className?: string; size?: "xs" | "sm" | "md" | "lg" | "xl" }) => (
  <Loader size={size} />
); 