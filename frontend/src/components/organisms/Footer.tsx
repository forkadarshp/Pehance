import { ThemeToggle } from "@/components/molecules/ThemeToggle";
import { Anchor, Group, Text } from "@mantine/core";
import Link from "next/link";

export const Footer = () => (
  <Group justify="space-between" style={{ width: '100%' }}>
    <Group gap="md">
      <Anchor component={Link} href="/dashboard" size="sm">
        Dashboard
      </Anchor>
      <Anchor href="#" size="sm">
        Docs
      </Anchor>
      <Anchor href="#" size="sm">
        GitHub
      </Anchor>
    </Group>
    <Group gap="sm">
      <ThemeToggle />
      <Text size="sm" c="dimmed">Built with Pehance</Text>
    </Group>
  </Group>
); 