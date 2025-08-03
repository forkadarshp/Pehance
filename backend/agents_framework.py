"""
Simplified agents framework implementation to match the interface
"""
import asyncio
import os
from groq import Groq
from typing import Dict, Any, List, Callable, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

# Global configuration
_tracing_disabled = False
_default_openai_api = "chat_completions"

def set_tracing_disabled(disabled: bool):
    global _tracing_disabled
    _tracing_disabled = disabled

def set_default_openai_api(api: str):
    global _default_openai_api
    _default_openai_api = api

class GuardrailFunctionOutput:
    def __init__(self, output_info: Dict[str, Any], tripwire_triggered: bool = False):
        self.output_info = output_info
        self.tripwire_triggered = tripwire_triggered

class InputGuardrailTripwireTriggered(Exception):
    pass

class InputGuardrail:
    def __init__(self, guardrail_function: Callable):
        self.guardrail_function = guardrail_function
    
    async def check(self, ctx, agent, input_data: str) -> GuardrailFunctionOutput:
        return await self.guardrail_function(ctx, agent, input_data)

class AgentResult:
    def __init__(self, final_output: str, success: bool = True):
        self.final_output = final_output
        self.success = success

class Agent:
    def __init__(self, name: str, instructions: str, model: str = "llama3-8b-8192", input_guardrails: List[InputGuardrail] = None):
        self.name = name
        self.instructions = instructions
        self.model = model
        self.input_guardrails = input_guardrails or []
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    async def process(self, input_text: str) -> str:
        # Check guardrails first
        for guardrail in self.input_guardrails:
            result = await guardrail.check(None, self, input_text)
            if result.tripwire_triggered:
                raise InputGuardrailTripwireTriggered("Input guardrail triggered")
        
        # Prepare messages
        messages = [
            {"role": "system", "content": self.instructions},
            {"role": "user", "content": input_text}
        ]
        
        try:
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in agent {self.name}: {e}")
            raise e

class Runner:
    @staticmethod
    async def run(agent: Agent, input_text: str) -> AgentResult:
        try:
            output = await agent.process(input_text)
            return AgentResult(final_output=output, success=True)
        except Exception as e:
            logger.error(f"Runner error for agent {agent.name}: {e}")
            if isinstance(e, InputGuardrailTripwireTriggered):
                raise e
            return AgentResult(final_output=f"Error: {str(e)}", success=False)

# For LiteLLM compatibility
try:
    from litellm import LitellmModel
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    
    class LitellmModel:
        def __init__(self, model: str, api_key: str):
            self.model = model
            self.api_key = api_key