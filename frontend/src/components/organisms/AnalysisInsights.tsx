"use client";

import { Badge, Box, Group, Paper, RingProgress, Stack, Text, Title } from "@mantine/core";
import { IconCpu, IconStairsUp } from "@tabler/icons-react";

interface AnalysisInsightsProps {
  intent: string;
  domain: string | null;
  confidence: number;
  complexity: string;
  processSteps: string[];
}

const StatCard = ({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) => (
  <Paper withBorder p="sm" radius="md">
    <Group>
      <Box style={{ color: "var(--mantine-color-primary-6)" }}>{icon}</Box>
      <Stack gap={0}>
        <Text size="xs" c="dimmed">
          {label}
        </Text>
        <Text fw={600} size="sm">
          {value}
        </Text>
      </Stack>
    </Group>
  </Paper>
);

export const AnalysisInsights = ({
  intent,
  domain,
  confidence,
  complexity,
  processSteps,
}: AnalysisInsightsProps) => {
  return (
    <Stack>
      <Title order={4}>Analysis Insights</Title>
      <Group grow>
        <Paper withBorder p="md" radius="md">
          <Group>
            <RingProgress
              size={80}
              thickness={8}
              roundCaps
              sections={[{ value: confidence * 100, color: "teal" }]}
              label={
                <Text c="teal" fw={700} ta="center" size="sm">
                  {(confidence * 100).toFixed(0)}%
                </Text>
              }
            />
            <Stack gap={0}>
              <Text size="sm" c="dimmed">
                Confidence
              </Text>
              <Text fw={600} size="lg">
                {intent}
              </Text>
              {domain && <Badge variant="light">{domain}</Badge>}
            </Stack>
          </Group>
        </Paper>

        <StatCard
          icon={<IconStairsUp size={24} />}
          label="Complexity"
          value={complexity}
        />
      </Group>

      <Paper withBorder p="md" radius="md">
        <Group>
          <IconCpu size={24} style={{ color: "var(--mantine-color-primary-6)" }} />
          <Text fw={600}>Processing Steps</Text>
        </Group>
        <Group mt="sm" gap="xs">
          {processSteps.map((step, index) => (
            <Badge key={index} variant="gradient">
              {step.replace(/_/g, " ")}
            </Badge>
          ))}
        </Group>
      </Paper>
    </Stack>
  );
}; 