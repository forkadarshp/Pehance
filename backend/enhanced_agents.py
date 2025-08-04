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

# --- Intent Classification Models ---

class IntentClassification(BaseModel):
    intent_category: str  # creative, technical, business, academic, personal, other
    confidence: float  # 0.0 to 1.0
    specific_domain: Optional[str]  # programming, writing, marketing, research, etc.
    complexity_level: str  # basic, intermediate, advanced
    requires_context: bool  # whether additional context would be helpful

# --- Utility Functions ---

def parse_intent_json(text: str) -> IntentClassification:
    """Parse JSON response from intent classifier with fallbacks"""
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
                complexity_level=data.get("complexity_level", "intermediate"),
                requires_context=bool(data.get("requires_context", True))
            )
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        print(f"Failed to parse intent JSON: {e}")
        print(f"Raw text: {text}")
    
    # Fallback to default classification
    return IntentClassification(
        intent_category="other",
        confidence=0.5,
        specific_domain=None,
        complexity_level="intermediate",
        requires_context=True
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

# 1. Intent Classifier Agent
intent_classifier_agent = Agent(
    name="Intent Classifier",
    instructions="""You are a precision intent classifier. Analyze user input and classify intelligently based on actual content depth and complexity, not assumptions.

**CRITICAL CLASSIFICATION RULES**:

1. **Length & Depth Analysis**:
   - Single words or greetings ("hi", "hello") = "other" category, basic complexity
   - Short phrases without specifics = basic complexity
   - Detailed requests with requirements = intermediate/advanced complexity

2. **Intent Categories**:
   - **creative**: Writing, art, storytelling, brainstorming, content creation
   - **technical**: Programming, engineering, system design, app/software development
   - **business**: Strategy, marketing, sales, operations, management
   - **academic**: Research, education, analysis, scientific queries
   - **personal**: Lifestyle, advice, personal development, planning, habits
   - **other**: Greetings, simple questions, unclear requests

3. **Complexity Assessment**:
   - **basic**: Greetings, simple questions, single-word prompts, casual conversation
   - **intermediate**: Specific requests with some detail, moderate expertise needed
   - **advanced**: Complex multi-part requests, detailed specifications, expert-level work

4. **Smart Domain Detection**:
   - Only assign specific domains when there are clear technical terms or context clues
   - For ambiguous or casual inputs, leave domain as null
   - Don't assume complex domains from simple requests

5. **Context Requirements**:
   - Basic/casual inputs rarely need additional context
   - Complex technical or business requests benefit from context

**EXAMPLES**:
- "hi" → other, basic, null domain, no context needed
- "help me" → other, basic, null domain, minimal context
- "build a todo app" → technical, intermediate, "web development", context helpful
- "create comprehensive marketing strategy for SaaS startup" → business, advanced, "marketing strategy", context needed

Return ONLY valid JSON:
{
  "intent_category": "category",
  "confidence": 0.8,
  "specific_domain": "domain_or_null",
  "complexity_level": "basic|intermediate|advanced",
  "requires_context": true_or_false
}""",
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

# 3. Best Practices Agent (with web search capabilities if available)
def create_best_practices_agent():
    """Create a best practices agent with web search if LiteLLM is available"""
    if LITELLM_AVAILABLE and os.environ.get("GROQ_API_KEY"):
        # Use LiteLLM with Groq for web search capabilities
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
        instructions="""You are a master-level prompt optimization specialist. Your expertise covers the latest and most effective prompt engineering techniques based on current research and proven methodologies.

Your task is to provide universal prompt optimization best practices that improve ANY prompt, regardless of domain or intent.

**CORE OPTIMIZATION PRINCIPLES TO INCLUDE**:

1. **Foundation Techniques** (Universal Application):
   - Role assignment with specific expertise levels and credentials
   - Context layering with relevant background information
   - Clear output specifications and format requirements
   - Task decomposition for complex requests
   - Constraint definition and boundary setting

2. **Advanced Optimization Methods**:
   - Chain-of-thought reasoning structures for problem-solving
   - Few-shot learning with relevant examples
   - Multi-perspective analysis for comprehensive coverage
   - Constraint optimization for precise requirements
   - Systematic frameworks and methodologies

3. **Platform Compatibility Best Practices**:
   - Structured sections for optimal AI comprehension
   - Clear conversation starters and context setting
   - Logical reasoning frameworks
   - Universal formatting that works across ChatGPT, Claude, Gemini, and others

4. **Prompt Structure Optimization**:
   - Opening with clear role and expertise definition
   - Context section with relevant background
   - Specific task breakdown and requirements
   - Output format specifications
   - Success criteria and quality markers

5. **Clarity and Precision Techniques**:
   - Elimination of ambiguous language
   - Specific terminology and technical precision
   - Clear success metrics and evaluation criteria
   - Explicit constraint definition
   - Actionable instruction formatting

6. **Advanced Prompting Strategies**:
   - Template-based approaches for consistency
   - Iterative refinement techniques
   - Error prevention through constraint setting
   - Quality assurance through specific requirements
   - Scalable prompt architecture

**CURRENT RESEARCH INSIGHTS** (Include Latest Findings):
- Most effective role assignment patterns
- Optimal context-to-instruction ratios
- Best practices for output format specification
- Common prompt failure modes and prevention
- Platform-specific optimization techniques

Format your response as:
## Universal Prompt Optimization Best Practices

### Foundation Techniques (Always Apply)
- [Core principles that improve any prompt]

### Advanced Optimization Methods
- [Sophisticated techniques for complex prompts]

### Structure and Clarity Principles
- [How to organize prompts for maximum effectiveness]

### Platform Compatibility Guidelines
- [Universal formatting and structure principles]

### Quality Assurance Techniques
- [Methods to ensure consistent, high-quality outputs]

### Common Pitfalls to Avoid
- [Frequent mistakes that reduce prompt effectiveness]

**Focus**: Provide actionable, universal principles that can be applied to enhance any prompt, regardless of specific use case or domain.""",
        model=model
    )

best_practices_agent = create_best_practices_agent()

# 4. Dynamic Enhancer Agent Creator
def create_dynamic_enhancer_instructions(intent_data: IntentClassification, supporting_context: str = "", best_practices: str = ""):
    base_instructions = """You are a master-level AI prompt optimization specialist. Your mission: transform any user input into precision-crafted prompts that unlock AI's full potential.

Use the proven 4-D METHODOLOGY for optimization:"""
    
    # Add intent-specific optimization techniques
    intent_specific = {
        "creative": """
**CREATIVE OPTIMIZATION TECHNIQUES**:
- Multi-perspective analysis + tone emphasis
- Role assignment with creative expertise (e.g., "Act as an award-winning creative director...")
- Context layering with inspiration sources and style references
- Output specifications for format, tone, and creative constraints
- Few-shot examples when beneficial for style guidance""",
        
        "technical": """
**TECHNICAL OPTIMIZATION TECHNIQUES**:
- Constraint-based + precision focus approach
- Role assignment with technical expertise (e.g., "Act as a senior software engineer with 10+ years experience...")
- Task decomposition for complex implementations
- Chain-of-thought reasoning for problem-solving
- Systematic frameworks and structured methodologies
- Precise technical specifications and environment details""",
        
        "business": """
**BUSINESS OPTIMIZATION TECHNIQUES**:
- Systematic frameworks + constraint optimization
- Role assignment with business expertise (e.g., "Act as a strategic business consultant...")
- Multi-perspective analysis for stakeholder considerations
- Context layering with market conditions and objectives
- Clear success metrics and deliverable specifications""",
        
        "academic": """
**ACADEMIC OPTIMIZATION TECHNIQUES**:
- Few-shot examples + clear structure approach
- Role assignment with academic expertise (e.g., "Act as a research specialist with PhD-level expertise...")
- Chain-of-thought reasoning for research methodology
- Systematic frameworks for academic rigor
- Precise citation and evidence requirements""",
        
        "personal": """
**PERSONAL OPTIMIZATION TECHNIQUES**:
- Context layering + practical implementation focus
- Role assignment with advisory expertise (e.g., "Act as a certified productivity coach...")
- Task decomposition for actionable steps
- Clear structure with motivational elements
- Constraint optimization for personal circumstances"""
    }
    
    complexity_guidance = {
        "basic": "BASIC MODE: Apply core techniques, quick optimization, deliver ready-to-use prompt.",
        "intermediate": "DETAIL MODE: Comprehensive optimization with targeted improvements and enhanced structure.",
        "advanced": "EXPERT MODE: Full 4-D methodology with advanced techniques, systematic frameworks, and precision optimization."
    }
    
    # Construct advanced dynamic instructions
    dynamic_instructions = f"""{base_instructions}

**CURRENT REQUEST ANALYSIS**:
- Intent Category: {intent_data.intent_category.upper()}
- Specific Domain: {intent_data.specific_domain or 'General'}
- Complexity Level: {intent_data.complexity_level.upper()}
- Confidence: {intent_data.confidence:.1%}

**OPTIMIZATION MODE**: {complexity_guidance.get(intent_data.complexity_level, "")}

{intent_specific.get(intent_data.intent_category, "")}

**4-D METHODOLOGY APPLICATION**:

1. **DECONSTRUCT** (Analysis Complete):
   - Core intent: {intent_data.intent_category} in {intent_data.specific_domain or 'general'} domain
   - Complexity: {intent_data.complexity_level} level requirement
   - Context provided: {len(supporting_context)} chars of domain knowledge
   - Best practices available: {len(best_practices)} chars of optimization guidance

2. **DIAGNOSE** (Issues to Address):
   - Clarity gaps: Vague or ambiguous requests
   - Specificity needs: Add precise requirements and constraints
   - Structure requirements: Organize for optimal AI comprehension
   - Missing context: Add role definition and clear deliverables

3. **DEVELOP** (Optimization Techniques):
   - Apply {intent_data.intent_category}-specific optimization methods
   - Implement appropriate role assignment and expertise level
   - Add context layering and structured formatting
   - Include output specifications and success criteria

4. **DELIVER** (Final Output):
   - Construct precision-crafted prompt ready for immediate use
   - Format optimally for AI platforms (ChatGPT, Claude, Gemini compatible)
   - Include clear structure and logical flow

**SUPPORTING DOMAIN CONTEXT**:
{supporting_context}

**UNIVERSAL OPTIMIZATION BEST PRACTICES**:
{best_practices}

**CRITICAL OPTIMIZATION REQUIREMENTS**:

**Foundation Techniques** (Always Apply):
- Role assignment with specific expertise level
- Context layering with relevant background
- Clear output specifications and format requirements
- Task decomposition when complexity demands it

**Advanced Techniques** (For Intermediate/Advanced):
- Chain-of-thought reasoning structure when beneficial
- Few-shot examples or templates when appropriate
- Multi-perspective analysis for comprehensive coverage
- Constraint optimization for precise requirements

**Platform Optimization**:
- Use structured sections for clear organization
- Include conversation starters when beneficial
- Apply logical reasoning frameworks
- Ensure compatibility across AI platforms

**OUTPUT MANDATE**:
Transform the user's basic prompt into a precision-crafted, professional-grade prompt that:
- Eliminates ambiguity and adds crucial specificity
- Includes expert role definition and context
- Specifies clear deliverables and success criteria
- Applies proven optimization techniques
- Ready for immediate use on any AI platform

**CRITICAL**: Output ONLY the optimized prompt. No explanations, meta-commentary, or questions. The result must be a complete, standalone, professional-grade prompt ready for immediate deployment."""
    
    return dynamic_instructions

# --- Multi-Agent Orchestration Function ---

async def orchestrate_enhancement(user_prompt: str):
    """
    Orchestrates the multi-agent enhancement process with rate limiting:
    1. Classify intent
    2. Generate supporting content with domain knowledge
    3. Create dynamically enhanced prompt
    """
    
    # Step 1: Classify Intent with rate limiting
    print("🎯 Classifying intent...")
    intent_result = await rate_limited_request(Runner.run, intent_classifier_agent, user_prompt)
    intent_data = parse_intent_json(intent_result.final_output)
    
    print(f"Intent: {intent_data.intent_category} ({intent_data.confidence:.1%} confidence)")
    print(f"Domain: {intent_data.specific_domain}")
    print(f"Complexity: {intent_data.complexity_level}")
    print(f"Needs context: {intent_data.requires_context}")
    
    # Step 2: Generate Supporting Content (if needed) with rate limiting
    supporting_context = ""
    research_performed = False
    
    if intent_data.requires_context and intent_data.complexity_level in ["intermediate", "advanced"]:
        print("🔍 Gathering supporting context...")
        
        # Generate supporting content with domain knowledge
        support_prompt = f"""
        Intent Analysis: {intent_data.dict()}
        Original Prompt: {user_prompt}
        
        Please provide comprehensive supporting context for this {intent_data.intent_category} prompt in the {intent_data.specific_domain or 'general'} domain. 
        
        Focus on:
        - Current best practices and industry standards
        - Relevant frameworks, tools, and methodologies
        - Common challenges and proven solutions
        - Key considerations for {intent_data.complexity_level} level implementation
        
        Provide detailed context that will help create a much more effective enhanced prompt.
        """
        
        support_result = await rate_limited_request(Runner.run, supporting_content_agent, support_prompt)
        supporting_context = support_result.final_output
        research_performed = True
        print(f"Context gathered: {len(supporting_context)} characters")
    
    # Step 3: Generate Best Practices (if needed) with rate limiting
    best_practices_context = ""
    if intent_data.complexity_level in ["intermediate", "advanced"]:
        print("🔍 Gathering best practices...")
        best_practices_prompt = f"""
        Intent Analysis: {intent_data.dict()}
        Original Prompt: {user_prompt}
        
        Please provide the most current and effective prompt writing best practices that should be applied universally, regardless of the specific intent or domain.
        """
        best_practices_result = await rate_limited_request(Runner.run, best_practices_agent, best_practices_prompt)
        best_practices_context = best_practices_result.final_output
        print(f"Best practices gathered: {len(best_practices_context)} characters")
    
    # Step 4: Create Dynamic Enhancer Agent
    print("✨ Enhancing prompt with dynamic context...")
    dynamic_instructions = create_dynamic_enhancer_instructions(intent_data, supporting_context, best_practices_context)
    
    enhancer_agent = Agent(
        name="Dynamic Prompt Enhancer",
        instructions=dynamic_instructions,
        model="llama3-8b-8192",
        input_guardrails=[InputGuardrail(guardrail_function=safety_guardrail)]
    )
    
    # Step 5: Generate Enhanced Prompt with rate limiting
    enhancement_result = await rate_limited_request(Runner.run, enhancer_agent, user_prompt)
    
    return {
        "enhanced_prompt": enhancement_result.final_output,
        "intent_analysis": intent_data.dict(),
        "supporting_context_length": len(supporting_context),
        "best_practices_length": len(best_practices_context),
        "web_research_performed": research_performed,
        "best_practices_applied": bool(best_practices_context),
        "process_steps": ["intent_classification", "knowledge_research", "best_practices_gathering", "dynamic_enhancement"] if best_practices_context else ["intent_classification", "knowledge_research", "dynamic_enhancement"]
    }