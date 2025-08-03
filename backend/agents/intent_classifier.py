from .base_agent import BaseAgent
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class IntentClassifierAgent(BaseAgent):
    """Agent that classifies the intent and goal of the user's prompt"""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = input_data.get("prompt", "")
        
        messages = [
            {
                "role": "system",
                "content": """You are an intent classifier. Your job is to analyze user prompts and identify:
1. The main goal/intent of the user
2. The domain/category (e.g., creative writing, business, technical, educational, etc.)
3. The desired output type (e.g., email, story, code, explanation, etc.)
4. The tone/style preference (formal, casual, creative, professional, etc.)
5. The complexity level (simple, intermediate, advanced)

Respond in JSON format with these fields:
{
    "intent": "main goal description",
    "domain": "category",
    "output_type": "desired format",
    "tone": "preferred tone",
    "complexity": "level",
    "confidence": 0.95
}"""
            },
            {
                "role": "user",
                "content": f"Classify the intent of this prompt: {prompt}"
            }
        ]
        
        try:
            response = await self.call_llm(messages, temperature=0.3, max_tokens=500)
            logger.info(f"Intent classification result: {response}")
            
            return {
                "agent": "intent_classifier",
                "result": response,
                "success": True
            }
        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            return {
                "agent": "intent_classifier", 
                "result": f"Error: {str(e)}",
                "success": False
            }