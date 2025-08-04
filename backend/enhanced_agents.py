import os
import asyncio
import json
import time
import random
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

from agents_framework import Agent, Runner, InputGuardrail, GuardrailFunctionOutput, set_tracing_disabled, set_default_openai_api, InputGuardrailTripwireTriggered, LITELLM_AVAILABLE, LitellmModel

load_dotenv()

# Configure for Python 3.9 compatibility with non-OpenAI providers
set_tracing_disabled(True)
set_default_openai_api("chat_completions")

# Set environment variables for LiteLLM
os.environ["OPENAI_API_KEY"] = os.environ.get("GROQ_API_KEY")
os.environ["OPENAI_BASE_URL"] = "https://api.groq.com/openai/v1"

# --- Rate Limiting Configuration ---
class RateLimitConfig:
    """Configuration for API rate limiting with exponential backoff"""
    MAX_RETRIES = 3
    BASE_DELAY = 1.0  # Base delay in seconds
    MAX_DELAY = 30.0  # Maximum delay in seconds
    BACKOFF_MULTIPLIER = 2.0
    JITTER_RANGE = 0.1  # Random jitter to prevent thundering herd

async def rate_limited_request(func, *args, **kwargs):
    """Execute a function with exponential backoff rate limiting"""
    delay = RateLimitConfig.BASE_DELAY
    
    for attempt in range(RateLimitConfig.MAX_RETRIES + 1):
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            error_str = str(e).lower()
            
            # Check if it's a rate limit error
            if "rate limit" in error_str or "too many requests" in error_str or "429" in error_str:
                if attempt < RateLimitConfig.MAX_RETRIES:
                    # Add jitter to prevent thundering herd
                    jitter = random.uniform(-RateLimitConfig.JITTER_RANGE, RateLimitConfig.JITTER_RANGE)
                    sleep_time = min(delay * (1 + jitter), RateLimitConfig.MAX_DELAY)
                    
                    print(f"⏳ Rate limit hit, retrying in {sleep_time:.1f}s (attempt {attempt + 1}/{RateLimitConfig.MAX_RETRIES + 1})")
                    await asyncio.sleep(sleep_time)
                    
                    # Exponential backoff
                    delay *= RateLimitConfig.BACKOFF_MULTIPLIER
                    continue
                else:
                    print(f"❌ Rate limit exceeded after {RateLimitConfig.MAX_RETRIES} retries")
                    raise e
            else:
                # Non-rate-limit error, re-raise immediately
                raise e
    
    # Should never reach here, but just in case
    raise Exception("Unexpected error in rate limiting logic")

# --- Enhanced Intent Classification Models ---

class IntentClassification(BaseModel):
    intent_category: str  # creative, technical, business, academic, personal, other, greeting, incomplete
    confidence: float  # 0.0 to 1.0
    specific_domain: Optional[str]  # programming, writing, marketing, research, etc.
    complexity_level: str  # basic, intermediate, advanced
    requires_context: bool  # whether additional context would be helpful
    # NEW: Enhanced 4D methodology fields
    input_complexity_score: float  # 0.0 to 1.0 - actual complexity of the input
    enhancement_recommended: bool  # whether full enhancement is appropriate
    suggested_action: str  # request_clarification, basic_enhancement, standard_enhancement, advanced_enhancement
    conversation_starter: Optional[str]  # personalized response for simple inputs
    input_type: str  # greeting, incomplete, minimal, substantial, complex

# --- Utility Functions ---

def parse_intent_json(text: str) -> IntentClassification:
    """Parse JSON response from intent classifier with enhanced 4D methodology fields"""
    try:
        # Try to find JSON in the response
        text = text.strip()
        
        # Look for JSON object in the text
        start_idx = text.find('{')
        end_idx = text.rfind('}') + 1
        
        if start_idx != -1 and end_idx > start_idx:
            json_text = text[start_idx:end_idx]
            data = json.loads(json_text)
            
            return IntentClassification(
                intent_category=data.get("intent_category", "other"),
                confidence=float(data.get("confidence", 0.5)),
                specific_domain=data.get("specific_domain"),
                complexity_level=data.get("complexity_level", "basic"),
                requires_context=bool(data.get("requires_context", True)),
                # NEW: Enhanced fields with smart defaults
                input_complexity_score=float(data.get("input_complexity_score", 0.5)),
                enhancement_recommended=bool(data.get("enhancement_recommended", True)),
                suggested_action=data.get("suggested_action", "standard_enhancement"),
                conversation_starter=data.get("conversation_starter"),
                input_type=data.get("input_type", "minimal")
            )
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        print(f"Failed to parse intent JSON: {e}")
        print(f"Raw text: {text}")
    
    # Fallback to default classification with conservative enhancement
    return IntentClassification(
        intent_category="other",
        confidence=0.5,
        specific_domain=None,
        complexity_level="basic",
        requires_context=False,
        input_complexity_score=0.3,
        enhancement_recommended=False,
        suggested_action="request_clarification",
        conversation_starter="I'd be happy to help! Could you provide more details about what you'd like me to help you with?",
        input_type="incomplete"
    )

# --- Guardrail Definition ---

async def safety_guardrail(ctx, agent, input_data):
    # Simple keyword-based check without external dependencies
    blocklist = ["hack", "illegal", "harmful", "violence", "exploit", "bypass"]
    is_flagged = any(word in input_data.lower() for word in blocklist)
    
    return GuardrailFunctionOutput(
        output_info={"flagged": is_flagged, "reason": "Contains potentially harmful content" if is_flagged else "Safe"},
        tripwire_triggered=is_flagged,
    )

# --- Agent Definitions ---

# 1. Enhanced Intent Classifier Agent with 4D Methodology
intent_classifier_agent = Agent(
    name="Enhanced Intent Classifier",
    instructions="""You are Lyra's precision intent classifier implementing advanced 4D methodology. Your mission: intelligently analyze user input to prevent over-enhancement syndrome and ensure proportional responses.

**CRITICAL 4D INPUT ANALYSIS RULES:**

## **1. DECONSTRUCT - Input Analysis**
Analyze these dimensions:
- **Input Length**: Character count and word complexity
- **Intent Clarity**: How clear the user's goal is
- **Context Depth**: Amount of meaningful detail provided
- **Conversation Type**: Greeting vs. task vs. question

## **2. DIAGNOSE - Complexity Assessment** 
Calculate precise complexity scores:

**INPUT TYPE CLASSIFICATION:**
- **greeting** (0.0-0.2): "hi", "hello", "hey", single greetings
- **incomplete** (0.1-0.3): Single words, fragments, "help me"
- **minimal** (0.2-0.5): Basic requests without context, "write something"
- **substantial** (0.4-0.8): Detailed requests with specifics, clear goals
- **complex** (0.7-1.0): Multi-part requests, expert-level detail, comprehensive needs

**COMPLEXITY SCORING FORMULA:**
- Length factor: (character_count / 100) * 0.3
- Detail factor: (specificity_level / 5) * 0.4  
- Intent clarity: (clarity_score / 5) * 0.3
- Final score: Min(1.0, sum of factors)

## **3. DEVELOP - Enhancement Decision Logic**

**ENHANCEMENT PATHWAY ROUTING:**
- **input_complexity_score < 0.3**: Route to "request_clarification"
- **input_complexity_score 0.3-0.5**: Route to "basic_enhancement" 
- **input_complexity_score 0.5-0.7**: Route to "standard_enhancement"
- **input_complexity_score > 0.7**: Route to "advanced_enhancement"

**CONVERSATION STARTERS** (for simple inputs):
- Greeting: "Hello! I'm here to help enhance your prompts. What would you like to create today?"
- Incomplete: "I'd be happy to help! Could you share more details about what you need?"
- Minimal: "To create the best prompt for you, could you tell me more about [specific area]?"

## **4. DELIVER - Smart Classification**

**INTENT CATEGORIES** (with complexity awareness):
- **creative**: Writing, art, storytelling (check for creative specifics)
- **technical**: Programming, engineering (check for technical depth)  
- **business**: Strategy, marketing, operations (check for business context)
- **academic**: Research, education, analysis (check for academic rigor)
- **personal**: Lifestyle, advice, development (check for personal context)
- **greeting**: Simple greetings, social interactions
- **incomplete**: Fragments needing clarification
- **other**: Unclear or uncategorizable requests

**CRITICAL ANTI-OVER-ENHANCEMENT RULES:**
1. **Greeting Detection**: Any input primarily consisting of greetings → complexity_score ≤ 0.2
2. **Fragment Detection**: Incomplete thoughts or single words → enhancement_recommended = false
3. **Context Requirement**: Only recommend context for complexity_score > 0.4
4. **Enhancement Threshold**: Only recommend full enhancement for complexity_score > 0.5

**EXAMPLES WITH SCORING:**

INPUT: "hi" 
OUTPUT: {
  "intent_category": "greeting",
  "confidence": 0.95,
  "specific_domain": null,
  "complexity_level": "basic", 
  "requires_context": false,
  "input_complexity_score": 0.1,
  "enhancement_recommended": false,
  "suggested_action": "request_clarification",
  "conversation_starter": "Hello! I'm here to help enhance your prompts. What would you like to create today?",
  "input_type": "greeting"
}

INPUT: "help me write"
OUTPUT: {
  "intent_category": "creative",
  "confidence": 0.6,
  "specific_domain": "writing",
  "complexity_level": "basic",
  "requires_context": false,
  "input_complexity_score": 0.3,
  "enhancement_recommended": true,
  "suggested_action": "basic_enhancement", 
  "conversation_starter": "I'd be happy to help with your writing! To create the best prompt, could you tell me: What type of writing? Who's your audience? What's the purpose?",
  "input_type": "minimal"
}

INPUT: "Create a comprehensive marketing strategy for a SaaS startup targeting small businesses with integration challenges"
OUTPUT: {
  "intent_category": "business",
  "confidence": 0.9,
  "specific_domain": "marketing strategy",
  "complexity_level": "advanced", 
  "requires_context": true,
  "input_complexity_score": 0.8,
  "enhancement_recommended": true,
  "suggested_action": "advanced_enhancement",
  "conversation_starter": null,
  "input_type": "complex"
}

**MANDATE**: Return ONLY valid JSON with ALL required fields. Be precise with complexity scoring to prevent over-enhancement.""",
    model="llama3-8b-8192"
)

# 2. Supporting Content Agent (Domain Context Provider)
supporting_content_agent = Agent(
    name="Supporting Content Agent", 
    instructions="""You are Lyra's domain context specialist. Provide focused, relevant domain knowledge based on intent analysis.

**DOMAIN CONTEXT PROVISION**:

**For Technical Domains**:
- Web/mobile development: Modern frameworks, best practices, architecture patterns
- Software engineering: Design patterns, development methodologies, code quality
- Data science: Tools, methodologies, analysis approaches

**For Creative Domains**:
- Writing: Structure techniques, style guides, audience considerations
- Design: Visual principles, user experience, current trends
- Marketing content: Persuasion techniques, brand voice, conversion focus

**For Business Domains**:
- Strategy: Frameworks (SWOT, OKRs), market analysis, competitive positioning
- Marketing: Customer acquisition, metrics, campaign optimization
- Operations: Process improvement, efficiency, scalability

**For Personal Domains**:
- Productivity: Systems (GTD, Pomodoro), habit formation, time management
- Planning: Goal-setting frameworks, decision-making models
- Development: Evidence-based approaches, tracking methods

**SMART CONTEXT RULES**:
- Match context precision to complexity level
- For basic requests: Minimal, focused context only
- For intermediate/advanced: Comprehensive domain knowledge
- Always relate context directly to the user's specific request

**OUTPUT FORMAT**:
## Domain Context
[Focused domain knowledge relevant to the specific request]

## Key Considerations
- [2-3 most important factors for this domain/request type]

## Implementation Notes
- [Practical guidance specific to the user's intent and complexity level]

**CRITICAL**: Provide concise, actionable context. Avoid generic advice. Focus on what specifically helps optimize THIS user's prompt.""",
    model="llama3-8b-8192"
)

# 3. Best Practices Agent (4-D Methodology Specialist)
def create_best_practices_agent():
    """Create a best practices agent implementing the 4-D methodology"""
    if LITELLM_AVAILABLE and os.environ.get("GROQ_API_KEY"):
        try:
            model = LitellmModel(
                model="groq/llama3-8b-8192", 
                api_key=os.environ.get("GROQ_API_KEY")
            )
        except Exception:
            model = "llama3-8b-8192"
    else:
        model = "llama3-8b-8192"
    
    return Agent(
        name="Best Practices Agent",
        instructions="""You are Lyra's 4-D methodology specialist. Provide proven optimization techniques based on request complexity and type.

## THE 4-D METHODOLOGY

### 1. DECONSTRUCT
- Extract core intent, key entities, and context
- Identify output requirements and constraints  
- Map what's provided vs. what's missing

### 2. DIAGNOSE
- Audit for clarity gaps and ambiguity
- Check specificity and completeness
- Assess structure and complexity needs

### 3. DEVELOP
- Select optimal techniques based on request type:
  - **Creative** → Multi-perspective + tone emphasis
  - **Technical** → Constraint-based + precision focus
  - **Business** → Systematic frameworks + ROI focus
  - **Academic** → Few-shot examples + clear structure
  - **Personal** → Context layering + practical steps
  - **Other/Basic** → Clarity enhancement + minimal structure

### 4. DELIVER
- Construct optimized prompt
- Format for AI platform compatibility
- Include clear success criteria

## OPTIMIZATION TECHNIQUES BY COMPLEXITY

**BASIC MODE** (Simple/casual requests):
- Add role clarity if beneficial
- Improve specificity without over-engineering
- Ensure clear output format
- Keep enhancements proportional to input

**INTERMEDIATE MODE** (Detailed requests):
- Apply full 4-D methodology
- Add systematic structure
- Include context and constraints
- Specify deliverables and success criteria

**ADVANCED MODE** (Complex/professional):
- Comprehensive optimization
- Multiple perspective analysis
- Advanced prompting techniques
- Professional-grade structuring

## OPERATING PRINCIPLES

**Foundation Techniques**: Role assignment, context layering, output specs, task decomposition
**Advanced Techniques**: Chain-of-thought, few-shot learning, multi-perspective analysis, constraint optimization

**OUTPUT**: Provide optimization guidance specific to the analyzed request complexity and intent category.

Format as:
## 4-D Analysis
- **Deconstruct**: [What's provided vs. what's missing]
- **Diagnose**: [Key issues to address]
- **Develop**: [Recommended optimization techniques]
- **Deliver**: [Structure and format guidance]

## Optimization Techniques
- [Specific techniques for this request type and complexity]

## Success Criteria
- [How to measure optimization effectiveness]""",
        model=model
    )

best_practices_agent = create_best_practices_agent()

# 4. Dynamic Enhancer Agent Creator (4-D Implementation)
def create_dynamic_enhancer_instructions(intent_data: IntentClassification, supporting_context: str = "", best_practices: str = ""):
    """Creates dynamic instructions implementing the full 4-D methodology"""
    
    base_instructions = """You are Lyra, a master-level AI prompt optimization specialist. Your mission: transform any user input into precision-crafted prompts that unlock AI's full potential using the proven 4-D METHODOLOGY.

## THE 4-D METHODOLOGY

### 1. DECONSTRUCT
- Extract core intent, key entities, and context
- Identify output requirements and constraints  
- Map what's provided vs. what's missing

### 2. DIAGNOSE
- Audit for clarity gaps and ambiguity
- Check specificity and completeness
- Assess structure and complexity needs

### 3. DEVELOP
- Select optimal techniques based on request type
- Assign appropriate AI role/expertise
- Enhance context and implement logical structure

### 4. DELIVER
- Construct optimized prompt
- Format based on AI tool compatibility
- Provide ready-to-use, professional-grade result"""

    # Complexity-based approach selection
    complexity_modes = {
        "basic": """
**BASIC MODE ACTIVATION**
- User input appears to be casual/simple (greeting, basic question, minimal detail)
- Apply lightweight enhancement: improve clarity without over-engineering
- Focus on making the request actionable while maintaining proportionality
- Add minimal structure and role clarity if genuinely beneficial""",
        
        "intermediate": """
**INTERMEDIATE MODE ACTIVATION**
- User input shows specific intent with moderate detail
- Apply systematic 4-D methodology with targeted improvements
- Add appropriate role assignment, context, and structure
- Include clear deliverables and success criteria""",
        
        "advanced": """
**ADVANCED MODE ACTIVATION**
- User input demonstrates complex, professional-level requirements
- Apply comprehensive 4-D methodology with advanced techniques
- Multiple perspective analysis, systematic frameworks
- Professional-grade structuring with detailed specifications"""
    }

    # Intent-specific optimization techniques
    intent_techniques = {
        "creative": "Multi-perspective analysis + tone emphasis + inspiration context",
        "technical": "Constraint-based + precision focus + implementation details", 
        "business": "Systematic frameworks + ROI focus + stakeholder considerations",
        "academic": "Few-shot examples + clear structure + evidence requirements",
        "personal": "Context layering + practical steps + sustainable approaches",
        "other": "Clarity enhancement + minimal structure + proportional improvements"
    }

    # Current analysis summary
    analysis_summary = f"""
**CURRENT REQUEST ANALYSIS**:
- Intent: {intent_data.intent_category.upper()}
- Domain: {intent_data.specific_domain or 'General'}
- Complexity: {intent_data.complexity_level.upper()} 
- Confidence: {intent_data.confidence:.1%}
- Context Available: {len(supporting_context) > 0}
- Best Practices Available: {len(best_practices) > 0}

**OPTIMIZATION APPROACH**: {intent_techniques.get(intent_data.intent_category, "General enhancement")}
"""

    # Construct the complete instructions
    full_instructions = f"""{base_instructions}

{analysis_summary}

{complexity_modes.get(intent_data.complexity_level, "")}

**SUPPORTING DOMAIN CONTEXT**:
{supporting_context if supporting_context else "No specific domain context provided."}

**OPTIMIZATION GUIDANCE**:
{best_practices if best_practices else "Apply standard 4-D methodology principles."}

**CRITICAL OUTPUT REQUIREMENTS**:

1. **Apply 4-D Methodology**:
   - DECONSTRUCT: What's the core intent vs. what's missing?
   - DIAGNOSE: What clarity/specificity issues need addressing?
   - DEVELOP: What optimization techniques fit this request type?
   - DELIVER: How should the final prompt be structured?

2. **Maintain Proportionality**:
   - For basic requests: Enhance clarity without over-complicating
   - For intermediate requests: Add structure and context appropriately  
   - For advanced requests: Apply comprehensive optimization techniques

3. **Ensure Platform Compatibility**:
   - Structure for optimal AI comprehension
   - Include clear conversation starters when beneficial
   - Format for universal AI platform use (ChatGPT, Claude, Gemini)

4. **Professional Standards**:
   - Role assignment when beneficial
   - Clear output specifications  
   - Actionable instructions
   - Success criteria when appropriate

**CRITICAL MANDATE**: 
Output ONLY the optimized prompt. No meta-commentary, explanations, or questions. The result must be a complete, standalone, professional-grade prompt ready for immediate deployment on any AI platform.

**SPECIAL INSTRUCTION FOR BASIC/CASUAL INPUTS**:
If the user input is very simple (like "hi" or single words), provide a friendly, conversational response that gently encourages more specific input rather than creating an overly complex prompt. Keep the enhancement proportional to the input complexity."""

    return full_instructions

def create_basic_enhancement_instructions(intent_data: IntentClassification, user_prompt: str):
    """Creates lightweight enhancement instructions for basic/simple inputs"""
    
    return f"""You are a helpful AI assistant focused on proportional prompt enhancement. 

**CURRENT REQUEST ANALYSIS**:
- Intent: {intent_data.intent_category}
- Input Type: {intent_data.input_type}
- Complexity Score: {intent_data.input_complexity_score:.2f}
- Enhancement Mode: BASIC (Proportional)

**YOUR TASK**: 
Provide a light enhancement of the user's request that:
1. Maintains the original intent and tone
2. Adds minimal but helpful structure if beneficial
3. Keeps the response proportional to input complexity
4. Avoids over-engineering simple requests

**ENHANCEMENT PRINCIPLES**:
- For very simple inputs: Add clarity without complexity
- Preserve the user's natural communication style
- Only add structure if it genuinely helps
- Keep enhancements minimal and focused

**CRITICAL**: Output only the enhanced prompt. No explanations or meta-commentary.

Original input complexity: {intent_data.input_complexity_score:.2f}/1.0
Enhancement should be proportional to this complexity level."""

# --- Multi-Agent Orchestration Function ---

async def orchestrate_enhancement(user_prompt: str):
    """
    Enhanced orchestration implementing 4D methodology with smart routing:
    1. Classify intent with precision complexity detection
    2. Route to appropriate enhancement pathway
    3. Apply proportional enhancement based on complexity
    4. Prevent over-enhancement syndrome
    """
    
    # Step 1: Enhanced Intent Classification with 4D methodology
    print("🎯 Analyzing user input with 4D methodology...")
    intent_result = await rate_limited_request(Runner.run, intent_classifier_agent, user_prompt)
    intent_data = parse_intent_json(intent_result.final_output)
    
    print(f"Intent: {intent_data.intent_category} ({intent_data.confidence:.1%} confidence)")
    print(f"Domain: {intent_data.specific_domain or 'None specified'}")
    print(f"Complexity Score: {intent_data.input_complexity_score:.2f}")
    print(f"Input Type: {intent_data.input_type}")
    print(f"Suggested Action: {intent_data.suggested_action}")
    
    # Step 2: Smart Enhancement Routing Based on 4D Analysis
    if intent_data.suggested_action == "request_clarification":
        print("📝 Routing to clarification response (preventing over-enhancement)")
        
        # Return a conversational response asking for more details
        clarification_response = intent_data.conversation_starter or \
            "I'd be happy to help enhance your prompt! Could you share more details about what you'd like to create or improve? The more specific you are, the better I can tailor the enhancement to your needs."
        
        return {
            "enhanced_prompt": clarification_response,
            "intent_analysis": intent_data.dict(),
            "enhancement_type": "clarification_request",
            "supporting_context_length": 0,
            "methodology_guidance_length": 0,
            "domain_research_performed": False,
            "4d_methodology_applied": True,  # 4D was applied to determine clarification needed
            "process_steps": ["intent_classification", "clarification_routing"],
            "enhancement_ratio": round(len(clarification_response) / len(user_prompt), 1),
            "complexity_score": intent_data.input_complexity_score
        }
    
    elif intent_data.suggested_action == "basic_enhancement":
        print("⚡ Applying basic enhancement (proportional to input complexity)")
        
        # For basic enhancement, skip context gathering but apply light improvement
        basic_instructions = create_basic_enhancement_instructions(intent_data, user_prompt)
        
        basic_enhancer = Agent(
            name="Basic Prompt Enhancer",
            instructions=basic_instructions,
            model="llama3-8b-8192"
        )
        
        enhancement_result = await rate_limited_request(Runner.run, basic_enhancer, user_prompt)
        
        return {
            "enhanced_prompt": enhancement_result.final_output,
            "intent_analysis": intent_data.dict(),
            "enhancement_type": "basic_enhancement",
            "supporting_context_length": 0,
            "methodology_guidance_length": 0,
            "domain_research_performed": False,
            "4d_methodology_applied": True,
            "process_steps": ["intent_classification", "basic_enhancement"],
            "enhancement_ratio": round(len(enhancement_result.final_output) / len(user_prompt), 1),
            "complexity_score": intent_data.input_complexity_score
        }
    
    else:
        # Standard or Advanced Enhancement - use existing sophisticated pipeline
        print(f"🚀 Applying {intent_data.suggested_action} with full multi-agent system")
        
        # Step 3: Smart Context Generation (only for standard/advanced)
        supporting_context = ""
        research_performed = False
        
        if intent_data.requires_context and intent_data.input_complexity_score > 0.4:
            print("🔍 Gathering domain-specific context...")
            
            support_prompt = f"""
            Intent Analysis: {intent_data.dict()}
            Original User Input: "{user_prompt}"
            
            Provide focused, relevant context for this {intent_data.intent_category} request in the {intent_data.specific_domain or 'general'} domain.
            
            Match context depth to complexity level: {intent_data.complexity_level}
            Complexity Score: {intent_data.input_complexity_score:.2f}
            """
            
            support_result = await rate_limited_request(Runner.run, supporting_content_agent, support_prompt)
            supporting_context = support_result.final_output
            research_performed = True
            print(f"Context gathered: {len(supporting_context)} characters")
        else:
            print("📝 Skipping context gathering - input complexity doesn't warrant it")
        
        # Step 4: 4-D Methodology Guidance (scaled to complexity)
        best_practices_context = ""
        methodology_applied = False
        
        if intent_data.input_complexity_score > 0.5:
            print("⚡ Applying 4-D methodology guidance...")
            methodology_prompt = f"""
            Intent Analysis: {intent_data.dict()}
            Original User Input: "{user_prompt}"
            
            Apply 4-D methodology analysis for this {intent_data.complexity_level} complexity {intent_data.intent_category} request.
            Complexity Score: {intent_data.input_complexity_score:.2f}
            
            Scale the depth of analysis to match the input complexity.
            """
            
            methodology_result = await rate_limited_request(Runner.run, best_practices_agent, methodology_prompt) 
            best_practices_context = methodology_result.final_output
            methodology_applied = True
            print(f"4-D methodology guidance: {len(best_practices_context)} characters")
        else:
            print("📝 Using proportional enhancement - minimal 4-D methodology")
        
        # Step 5: Create Sophisticated Dynamic Enhancer with Anti-Over-Enhancement
        print("✨ Crafting proportionally optimized prompt...")
        dynamic_instructions = create_dynamic_enhancer_instructions(intent_data, supporting_context, best_practices_context)
        
        enhancer_agent = Agent(
            name="Lyra - Proportional Enhancement Specialist",
            instructions=dynamic_instructions,
            model="llama3-8b-8192",
            input_guardrails=[InputGuardrail(guardrail_function=safety_guardrail)]
        )
        
        # Step 6: Generate Enhanced Prompt with Proportionality Controls
        enhancement_result = await rate_limited_request(Runner.run, enhancer_agent, user_prompt)
        
        # Determine process steps based on what was actually performed
        process_steps = ["intent_classification"]
        if research_performed:
            process_steps.append("domain_context_research")
        if methodology_applied:
            process_steps.append("4d_methodology_application")
        process_steps.append("proportional_prompt_optimization")
        
        enhancement_ratio = round(len(enhancement_result.final_output) / len(user_prompt), 1)
        
        return {
            "enhanced_prompt": enhancement_result.final_output,
            "intent_analysis": intent_data.dict(),
            "enhancement_type": intent_data.suggested_action,
            "supporting_context_length": len(supporting_context),
            "methodology_guidance_length": len(best_practices_context),
            "domain_research_performed": research_performed,
            "4d_methodology_applied": methodology_applied,
            "process_steps": process_steps,
            "enhancement_ratio": enhancement_ratio,
            "complexity_score": intent_data.input_complexity_score
        }