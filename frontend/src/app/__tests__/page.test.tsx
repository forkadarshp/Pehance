import { theme } from "@/lib/theme";
import { MantineProvider } from "@mantine/core";
import { render, screen } from "@testing-library/react";
import Home from "../page";

// Wrap component with MantineProvider for testing
const HomeWithProvider = () => (
  <MantineProvider theme={theme}>
    <Home />
  </MantineProvider>
);

describe("Home Page", () => {
  it("renders the main heading", () => {
    render(<HomeWithProvider />);
    const heading = screen.getByRole("heading", {
      name: /prompt engineering excellence/i,
    });
    expect(heading).toBeInTheDocument();
  });
}); 