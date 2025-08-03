"use client";

import { Box, Group, Text } from "@mantine/core";
import { IconBolt } from "@tabler/icons-react";

export const Header = () => {
  return (
    <Box
      component="header"
      py="md"
      px="xl"
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        right: 0,
        zIndex: 20,
      }}
    >
      <Group>
        <IconBolt size={24} />
        <Text size="lg" fw={700}>
          Pehance
        </Text>
      </Group>
    </Box>
  );
}; 