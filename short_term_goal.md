# Short-Term Goal: MVP Landing Page

## Objective

Create a simple, functional landing page that demonstrates the core value proposition of "Pehance." This serves as the first milestone towards the larger vision outlined in `end_goal.md`.

## Core Functionality

- A user visits the landing page.
- The page presents a clear and simple message window (e.g., a textarea).
- The user can input any prompt, including vague ones.
- Upon submission, the application processes the input and returns an enhanced version of the prompt.

## Key Components

1.  **Frontend:** A single landing page built with Next.js and Tailwind CSS, deployed on Vercel.
2.  **UI Elements:**
    - Prompt input area.
    - "Enhance" button.
    - Display area for the enhanced prompt.
3.  **Backend:** A multi-agent system responsible for prompt enhancement.
    - **Framework**: Python-based, using a framework like AgentScope or LangChain.
    - **LLM**: Groq with the Llama 3 8B model for high-speed inference.
    - **Deployment**: Hosted on a free-tier service (e.g., Render, Fly.io).
    - **Agent Architecture**:
      - **Intent Classifier Agent**: Identifies the user's goal.
      - **Supporting Content Agent**: Gathers context to enrich the prompt.
      - **Guardrail Agent**: Filters for safety, profanity, and relevance.
      - **Enhancer Agent**: Generates the final, improved prompt.