"use client";

import { Button } from "@/components/atoms/Button";
import {
  ActionIcon,
  Box,
  Container,
  Group,
  Loader,
  LoadingOverlay,
  Paper,
  Stack,
  Text,
  Textarea,
  Title,
  Tooltip,
} from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { IconLink, IconPhoto, IconSend, IconX } from "@tabler/icons-react";
import { motion } from "framer-motion";
import { useState } from "react";
import { EnhancementView } from "./EnhancementView";

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

interface SuggestedPrompt {
  text: string;
  category: string;
}

const suggestedPrompts: SuggestedPrompt[] = [
  { text: "A blog post about AI", category: "Creative" },
  { text: "Explain quantum computing", category: "Academic" },
  { text: "Code a snake game in python", category: "Technical" },
  { text: "Marketing plan for a new app", category: "Business" },
  { text: "How to be more productive", category: "Personal" },
  { text: "Write a short story", category: "Creative" },
];

export const CentralPrompt = () => {
  const [prompt, setPrompt] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [enhancementResult, setEnhancementResult] = useState<EnhancementResult | null>(null);

  const handleSubmit = async () => {
    if (!prompt.trim()) return;
    setIsLoading(true);
    setEnhancementResult(null);
    
    try {
      const response = await fetch("http://localhost:8000/enhance", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json();
      setEnhancementResult(data);
    } catch (error) {
      console.error("Error submitting prompt:", error);
      notifications.show({
        title: "Enhancement Failed",
        message: "Sorry, we couldn't enhance your prompt. Please try again later.",
        color: "red",
        icon: <IconX size={18} />,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestedPrompt = (suggestedText: string) => {
    setPrompt(suggestedText);
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === "Enter" && (event.metaKey || event.ctrlKey)) {
      handleSubmit();
    }
  };

  if (enhancementResult) {
    return (
      <Container size="xl" style={{ paddingTop: "2rem" }}>
        <EnhancementView
          originalPrompt={prompt}
          enhancementResult={enhancementResult}
          onBack={() => setEnhancementResult(null)}
        />
      </Container>
    );
  }

  return (
    <>
      <LoadingOverlay
        visible={isLoading}
        overlayProps={{ radius: "sm", blur: 2 }}
        loaderProps={{ type: 'bars' }}
      />
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Container size="md" style={{ minHeight: "80vh", display: "flex", flexDirection: "column", justifyContent: "center" }}>
          <Stack align="center" gap="xl" style={{ paddingTop: "4rem", paddingBottom: "4rem" }}>
            {/* Main heading */}
            <Stack align="center" gap="lg" style={{ textAlign: "center" }}>
              <Title
                order={1}
                style={{
                  fontSize: "clamp(3rem, 5vw, 4.5rem)",
                  fontWeight: 700,
                  lineHeight: 1.1,
                  letterSpacing: "-0.02em",
                }}
              >
                <Text
                  span
                  style={{
                    background:
                      "linear-gradient(145deg, var(--mantine-color-gray-1) 0%, var(--mantine-color-gray-5) 100%)",
                    backgroundClip: "text",
                    WebkitTextFillColor: "transparent",
                  }}
                >
                  Prompt Engineering Excellence
                </Text>
              </Title>
              <Text
                size="xl"
                c="dimmed"
                style={{
                  fontSize: "1.25rem",
                  maxWidth: "600px",
                  lineHeight: 1.5,
                }}
              >
                Transform your ideas into precision-crafted prompts that unlock AI's
                full potential.
              </Text>
            </Stack>

            {/* Central input area */}
            <Paper
              shadow="sm"
              radius="lg"
              withBorder
              style={{
                width: "100%",
                maxWidth: "700px",
                position: "relative",
                backgroundColor: "hsla(var(--background), 0.5)",
                backdropFilter: "blur(10px)",
                borderColor: "hsla(var(--border), 0.2)",
                boxShadow: "0 4px 30px rgba(0, 0, 0, 0.1)",
              }}
            >
              <Box p="md">
                <Textarea
                  placeholder="Enter a simple prompt to see it enhanced..."
                  value={prompt}
                  onChange={(event) => setPrompt(event.currentTarget.value)}
                  onKeyDown={handleKeyPress}
                  minRows={4}
                  maxRows={10}
                  autosize
                  variant="unstyled"
                  style={{
                    fontSize: "1.1rem",
                    lineHeight: 1.5,
                  }}
                  styles={{
                    input: {
                      border: "none",
                      padding: "0.5rem 0",
                      fontSize: "1.1rem",
                      resize: "none",
                    },
                  }}
                />
                
                {/* Input actions */}
                <Group justify="space-between" mt="sm">
                  <Group gap="xs">
                    <Tooltip label="Attach link">
                      <ActionIcon variant="subtle" size="sm">
                        <IconLink size={16} />
                      </ActionIcon>
                    </Tooltip>
                    <Tooltip label="Add image">
                      <ActionIcon variant="subtle" size="sm">
                        <IconPhoto size={16} />
                      </ActionIcon>
                    </Tooltip>
                  </Group>
                  
                  <Button
                    onClick={handleSubmit}
                    disabled={!prompt.trim() || isLoading}
                    size="lg"
                    radius="xl"
                    style={{
                      background: "linear-gradient(145deg, var(--mantine-color-primary-5), var(--mantine-color-primary-7))",
                      boxShadow: "0px 4px 15px rgba(var(--mantine-color-primary-9-rgb), 0.2)",
                    }}
                  >
                    <Group gap="xs">
                      {isLoading ? (
                        <Loader color="white" size="sm" />
                      ) : (
                        <>
                          <IconSend size={18} />
                          <span>Enhance Prompt</span>
                        </>
                      )}
                    </Group>
                  </Button>
                </Group>
              </Box>
            </Paper>

            {/* Suggested prompts */}
            <Stack gap="sm" align="center" style={{ marginTop: "2rem" }}>
              <Group gap="sm" justify="center" style={{ flexWrap: "wrap", maxWidth: "800px" }}>
                {suggestedPrompts.map((suggestion, index) => (
                  <Button
                    key={index}
                    variant="default"
                    size="sm"
                    onClick={() => handleSuggestedPrompt(suggestion.text)}
                    style={{
                      borderRadius: "2rem",
                      color: "var(--mantine-color-dimmed)",
                    }}
                    styles={{
                      root: {
                        transition: "transform 0.2s ease, box-shadow 0.2s ease",
                        "&:hover": {
                          transform: "translateY(-2px)",
                          boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                        },
                      },
                    }}
                  >
                    {suggestion.text}
                  </Button>
                ))}
              </Group>
            </Stack>
          </Stack>
        </Container>
      </motion.div>
    </>
  );
}; 