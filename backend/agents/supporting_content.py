from .base_agent import BaseAgent
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class SupportingContentAgent(BaseAgent):
    """Agent that gathers context and supporting information to enrich the prompt"""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = input_data.get("prompt", "")
        intent_result = input_data.get("intent_classification", {})
        
        messages = [
            {
                "role": "system", 
                "content": """You are a supporting content agent. Your job is to identify what additional context, examples, or supporting information would make a prompt more effective.

Based on the user's prompt and its classified intent, suggest:
1. Missing context that should be added
2. Relevant examples or references
3. Clarifying questions that could improve the prompt
4. Background information that would be helpful
5. Specific details that would enhance the output

Respond in JSON format:
{
    "missing_context": ["list of missing context elements"],
    "suggested_examples": ["relevant examples to include"],
    "clarifying_questions": ["questions to make prompt clearer"],
    "background_info": ["useful background information"],
    "enhancement_suggestions": ["specific ways to improve the prompt"]
}"""
            },
            {
                "role": "user",
                "content": f"""Original prompt: {prompt}
                
Intent classification: {intent_result}

What supporting content would enhance this prompt?"""
            }
        ]
        
        try:
            response = await self.call_llm(messages, temperature=0.5, max_tokens=800)
            logger.info(f"Supporting content result: {response}")
            
            return {
                "agent": "supporting_content",
                "result": response,
                "success": True
            }
        except Exception as e:
            logger.error(f"Supporting content generation failed: {e}")
            return {
                "agent": "supporting_content",
                "result": f"Error: {str(e)}",
                "success": False
            }