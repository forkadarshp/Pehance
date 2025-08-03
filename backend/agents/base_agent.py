from groq import Groq
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BaseAgent:
    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.model = "llama3-8b-8192"  # Llama 3 8B model
    
    async def call_llm(self, messages: list, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Call Groq LLM with given messages"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            raise e
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement process method")