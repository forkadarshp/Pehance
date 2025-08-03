from .intent_classifier import IntentClassifierAgent
from .supporting_content import SupportingContentAgent
from .guardrail import GuardrailAgent
from .enhancer import EnhancerAgent
from typing import Dict, Any
import logging
import json

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """Orchestrates the multi-agent prompt enhancement pipeline"""
    
    def __init__(self):
        self.intent_agent = IntentClassifierAgent()
        self.content_agent = SupportingContentAgent()
        self.guardrail_agent = GuardrailAgent()
        self.enhancer_agent = EnhancerAgent()
    
    async def enhance_prompt(self, prompt: str) -> Dict[str, Any]:
        """Run the full multi-agent enhancement pipeline"""
        results = {
            "original_prompt": prompt,
            "agent_results": {},
            "enhanced_prompt": "",
            "success": False,
            "error": None
        }
        
        try:
            # Stage 1: Intent Classification
            logger.info("Starting intent classification...")
            intent_result = await self.intent_agent.process({"prompt": prompt})
            results["agent_results"]["intent_classifier"] = intent_result
            
            if not intent_result["success"]:
                raise Exception(f"Intent classification failed: {intent_result['result']}")
            
            # Stage 2: Supporting Content Generation
            logger.info("Generating supporting content...")
            content_result = await self.content_agent.process({
                "prompt": prompt,
                "intent_classification": intent_result["result"]
            })
            results["agent_results"]["supporting_content"] = content_result
            
            if not content_result["success"]:
                raise Exception(f"Supporting content generation failed: {content_result['result']}")
            
            # Stage 3: Generate initial enhanced prompt for guardrail check
            logger.info("Generating initial enhanced prompt...")
            initial_enhanced = await self.enhancer_agent.process({
                "prompt": prompt,
                "intent_classification": intent_result["result"],
                "supporting_content": content_result["result"],
                "guardrail_check": {}
            })
            
            if not initial_enhanced["success"]:
                raise Exception(f"Initial enhancement failed: {initial_enhanced['result']}")
            
            # Stage 4: Guardrail Check
            logger.info("Running guardrail checks...")
            guardrail_result = await self.guardrail_agent.process({
                "prompt": prompt,
                "enhanced_prompt": initial_enhanced["result"]
            })
            results["agent_results"]["guardrail"] = guardrail_result
            
            if not guardrail_result["success"]:
                raise Exception(f"Guardrail check failed: {guardrail_result['result']}")
            
            # Check if content passed safety checks
            try:
                guardrail_data = json.loads(guardrail_result["result"])
                if not guardrail_data.get("is_safe", False):
                    logger.warning("Content failed safety checks")
                    results["error"] = "Content did not pass safety checks"
                    results["safety_concerns"] = guardrail_data.get("concerns", [])
                    return results
            except json.JSONDecodeError:
                logger.warning("Could not parse guardrail result, proceeding with caution")
            
            # Stage 5: Final Enhancement (with guardrail feedback)
            logger.info("Generating final enhanced prompt...")
            final_result = await self.enhancer_agent.process({
                "prompt": prompt,
                "intent_classification": intent_result["result"],
                "supporting_content": content_result["result"],
                "guardrail_check": guardrail_result["result"]
            })
            results["agent_results"]["enhancer"] = final_result
            
            if not final_result["success"]:
                raise Exception(f"Final enhancement failed: {final_result['result']}")
            
            results["enhanced_prompt"] = final_result["result"]
            results["success"] = True
            logger.info("Prompt enhancement pipeline completed successfully")
            
        except Exception as e:
            logger.error(f"Enhancement pipeline failed: {e}")
            results["error"] = str(e)
            results["success"] = False
        
        return results