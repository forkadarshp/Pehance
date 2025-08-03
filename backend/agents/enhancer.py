from .base_agent import BaseAgent
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class EnhancerAgent(BaseAgent):
    """Agent that generates the final, improved prompt"""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = input_data.get("prompt", "")
        intent_result = input_data.get("intent_classification", {})
        supporting_content = input_data.get("supporting_content", {})
        guardrail_result = input_data.get("guardrail_check", {})
        
        messages = [
            {
                "role": "system",
                "content": """You are a prompt enhancement agent. Your job is to create a significantly improved version of the user's prompt based on:

1. The classified intent and goals
2. Supporting content and context suggestions  
3. Safety and appropriateness guidelines
4. Best practices for prompt engineering

Create an enhanced prompt that:
- Is clear, specific, and well-structured
- Includes relevant context and examples
- Uses appropriate tone and style
- Provides clear instructions for desired output
- Is optimized for getting the best results from AI systems

Respond with just the enhanced prompt - no explanations or metadata, just the improved prompt text."""
            },
            {
                "role": "user", 
                "content": f"""Enhance this prompt using the analysis provided:

ORIGINAL PROMPT:
{prompt}

INTENT ANALYSIS:
{intent_result}

SUPPORTING CONTENT SUGGESTIONS:
{supporting_content}

SAFETY CHECK:
{guardrail_result}

Provide the enhanced prompt:"""
            }
        ]
        
        try:
            response = await self.call_llm(messages, temperature=0.7, max_tokens=1500)
            logger.info(f"Prompt enhancement completed")
            
            return {
                "agent": "enhancer",
                "result": response.strip(),
                "success": True
            }
        except Exception as e:
            logger.error(f"Prompt enhancement failed: {e}")
            return {
                "agent": "enhancer",
                "result": f"Error: {str(e)}",
                "success": False
            }