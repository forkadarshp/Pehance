"use client";

import { Button } from "@/components/atoms/Button";
import { Grid, Group, LoadingOverlay, Paper, Textarea } from "@mantine/core";
import { useState } from "react";

export const PromptPanel = () => {
  const [prompt, setPrompt] = useState("");
  const [enhancedPrompt, setEnhancedPrompt] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleEnhance = async () => {
    if (!prompt) return;
    setIsLoading(true);
    setEnhancedPrompt("");

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
      setEnhancedPrompt(data.enhanced_prompt);
    } catch (error) {
      console.error("Failed to enhance prompt:", error);
      setEnhancedPrompt("Error: Could not enhance prompt.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Paper shadow="sm" p="lg" radius="md" withBorder style={{ width: '100%', maxWidth: '1024px' }}>
      <Grid>
        <Grid.Col span={{ base: 12, md: 6 }}>
          <Textarea
            label="Your Prompt"
            placeholder="Enter your prompt here..."
            value={prompt}
            onChange={(event) => setPrompt(event.currentTarget.value)}
            minRows={8}
            maxRows={12}
            autosize
            description={`${prompt.length}/2000`}
          />
        </Grid.Col>
        <Grid.Col span={{ base: 12, md: 6 }}>
          <div style={{ position: 'relative' }}>
            <Textarea
              label="Enhanced Prompt"
              placeholder="Enhanced prompt will appear here..."
              value={enhancedPrompt}
              readOnly
              minRows={8}
              maxRows={12}
              autosize
            />
            <LoadingOverlay visible={isLoading} />
          </div>
        </Grid.Col>
      </Grid>
      <Group justify="flex-end" mt="md">
        <Button
          onClick={handleEnhance}
          disabled={isLoading || !prompt}
        >
          {isLoading ? "Enhancing..." : "Enhance"}
        </Button>
      </Group>
    </Paper>
  );
}; 