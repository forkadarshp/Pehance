from .base_agent import BaseAgent
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class GuardrailAgent(BaseAgent):
    """Agent that filters content for safety, profanity, and relevance"""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = input_data.get("prompt", "")
        enhanced_prompt = input_data.get("enhanced_prompt", "")
        
        messages = [
            {
                "role": "system",
                "content": """You are a content guardrail agent. Your job is to ensure content is safe, appropriate, and relevant.

Check for:
1. Harmful or dangerous content
2. Hate speech or discriminatory language
3. Adult/inappropriate content
4. Spam or irrelevant content
5. Potential security risks or malicious instructions
6. Privacy concerns

If content passes all checks, mark it as "safe". If issues are found, provide specific concerns and suggestions for improvement.

Respond in JSON format:
{
    "is_safe": true/false,
    "concerns": ["list of specific issues found"],
    "risk_level": "low/medium/high",
    "suggestions": ["ways to address issues"],
    "filtered_content": "cleaned version if needed"
}"""
            },
            {
                "role": "user",
                "content": f"""Check this content for safety and appropriateness:

Original prompt: {prompt}
Enhanced prompt: {enhanced_prompt}"""
            }
        ]
        
        try:
            response = await self.call_llm(messages, temperature=0.1, max_tokens=600)
            logger.info(f"Guardrail check result: {response}")
            
            return {
                "agent": "guardrail",
                "result": response,
                "success": True
            }
        except Exception as e:
            logger.error(f"Guardrail check failed: {e}")
            return {
                "agent": "guardrail",
                "result": f"Error: {str(e)}",
                "success": False
            }