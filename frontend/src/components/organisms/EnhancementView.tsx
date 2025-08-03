"use client";

import {
    ActionIcon,
    Box,
    Button,
    CopyButton,
    Grid,
    Group,
    Paper,
    Stack,
    Text,
    Textarea,
    Tooltip
} from "@mantine/core";
import { IconArrowLeft, IconCheck, IconCopy } from "@tabler/icons-react";
import { motion } from "framer-motion";
import { AnalysisInsights } from "./AnalysisInsights";

interface EnhancementResult {
  enhanced_prompt: string;
  intent_analysis: {
    intent_category: string;
    confidence: number;
    specific_domain: string | null;
    complexity_level: string;
  };
  process_steps: string[];
}

interface EnhancementViewProps {
  originalPrompt: string;
  enhancementResult: EnhancementResult;
  onBack: () => void;
}

export const EnhancementView = ({
  originalPrompt,
  enhancementResult,
  onBack,
}: EnhancementViewProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Stack gap="xl" style={{ width: "100%", maxWidth: "1200px" }}>
        <Group>
          <Button
            variant="subtle"
            onClick={onBack}
            leftSection={<IconArrowLeft size={16} />}
          >
            Back
          </Button>
        </Group>

        <AnalysisInsights
          intent={enhancementResult.intent_analysis.intent_category}
          domain={enhancementResult.intent_analysis.specific_domain}
          confidence={enhancementResult.intent_analysis.confidence}
          complexity={enhancementResult.intent_analysis.complexity_level}
          processSteps={enhancementResult.process_steps}
        />

        <Grid gutter="xl">
          <Grid.Col span={{ base: 12, md: 6 }}>
            <Paper 
              withBorder 
              radius="lg" 
              p="md" 
              style={{ 
                height: "100%",
                backgroundColor: "hsla(var(--background), 0.5)",
                backdropFilter: "blur(10px)",
                borderColor: "hsla(var(--border), 0.2)",
              }}
            >
              <Stack>
                <Text fw={500}>Original Prompt</Text>
                <Textarea
                  value={originalPrompt}
                  readOnly
                  variant="unstyled"
                  minRows={10}
                  autosize
                />
              </Stack>
            </Paper>
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 6 }}>
            <Paper
              withBorder
              radius="lg"
              p="md"
              style={{
                position: "relative",
                overflow: "hidden",
                height: "100%",
                borderColor: "hsla(var(--border), 0.2)",
                backgroundColor: "hsla(var(--background), 0.5)",
                backdropFilter: "blur(10px)",
              }}
            >
              <Box 
                style={{
                  position: "absolute",
                  top: 0,
                  left: "-100%",
                  width: "100%",
                  height: "100%",
                  background: "linear-gradient(90deg, transparent, hsla(var(--mantine-color-primary-5), 0.1), transparent)",
                  animation: "shine 4s infinite",
                }}
              />
              <Stack>
                <Group justify="space-between">
                  <Text fw={600} size="lg">Enhanced Prompt</Text>
                  <CopyButton value={enhancementResult.enhanced_prompt}>
                    {({ copied, copy }) => (
                      <Tooltip label={copied ? "Copied" : "Copy"} withArrow>
                        <ActionIcon
                          variant="subtle"
                          onClick={copy}
                          color={copied ? "teal" : "gray"}
                        >
                          {copied ? (
                            <IconCheck size={16} />
                          ) : (
                            <IconCopy size={16} />
                          )}
                        </ActionIcon>
                      </Tooltip>
                    )}
                  </CopyButton>
                </Group>
                <Textarea
                  value={enhancementResult.enhanced_prompt}
                  readOnly
                  variant="unstyled"
                  minRows={10}
                  autosize
                />
              </Stack>
            </Paper>
          </Grid.Col>
        </Grid>
      </Stack>
    </motion.div>
  );
}; 