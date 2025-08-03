import os
import asyncio
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from agents import Agent, Runner, InputGuardrail, GuardrailFunctionOutput, set_tracing_disabled, set_default_openai_api
from agents.exceptions import InputGuardrailTripwireTriggered
from dotenv import load_dotenv

# Try to import LiteLLM model for web search capabilities
try:
    from agents.extensions.models.litellm_model import LitellmModel
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    print("LiteLLM not available - web search for best practices will be simulated")

load_dotenv()

# Configure for Python 3.9 compatibility with non-OpenAI providers
set_tracing_disabled(True)
set_default_openai_api("chat_completions")

# Set environment variables for LiteLLM
os.environ["OPENAI_API_KEY"] = os.environ.get("GROQ_API_KEY")
os.environ["OPENAI_BASE_URL"] = "https://api.groq.com/openai/v1"

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
    instructions="""You are an expert at analyzing user prompts and determining their intent, domain, and requirements.

Analyze the user's prompt and classify it according to:

1. **Intent Category** (choose one):
   - creative: Writing, art, storytelling, brainstorming, content creation
   - technical: Programming, engineering, troubleshooting, system design, app/software development
   - business: Strategy, marketing, sales, operations, management, entrepreneurship
   - academic: Research, education, analysis, scientific queries, studying
   - personal: Lifestyle, advice, personal development, planning, productivity habits
   - other: General questions that don't fit above categories

2. **Confidence**: How confident you are in this classification (0.0-1.0)

3. **Specific Domain**: More specific field based on context clues:
   - For technical: "web development", "mobile app development", "software engineering", "data science", "system administration"
   - For creative: "content writing", "graphic design", "storytelling", "marketing copy", "social media"
   - For business: "content marketing", "product management", "strategy consulting", "sales", "operations"
   - For academic: "research methodology", "data analysis", "literature review", "academic writing"
   - For personal: "productivity", "fitness", "personal finance", "life planning", "habit formation"

4. **Complexity Level**:
   - basic: Simple, straightforward requests (e.g., "make a list", "give me tips")
   - intermediate: Moderate complexity, some expertise needed (e.g., "build an app", "create a system")
   - advanced: Complex, requires deep expertise or multiple steps (e.g., "architect a solution", "design a comprehensive strategy")

5. **Requires Context**: Whether additional context/research would significantly improve the enhanced prompt

**Important Classification Rules**:
- If the user wants to "build", "create", "develop", "code", "make an app/website/system" → classify as TECHNICAL
- If the user wants to "use", "follow", "organize", "plan", "improve habits" → classify as PERSONAL
- Look for technical keywords: "app", "website", "code", "programming", "software", "system", "API", "database"
- Look for personal keywords: "organize", "plan", "habits", "productivity", "lifestyle", "routine"

Return ONLY a valid JSON object with your analysis in this exact format:
{
  "intent_category": "category_here",
  "confidence": 0.85,
  "specific_domain": "domain_here_or_null",
  "complexity_level": "level_here",
  "requires_context": true_or_false
}""",
    model="llama3-8b-8192"
)

# 2. Supporting Content Agent (with research capabilities)
supporting_content_agent = Agent(
    name="Supporting Content Agent",
    instructions="""You are a research and context specialist. Your job is to provide relevant supporting information based on the user's intent classification and specific domain.

Based on the intent analysis provided, you should provide relevant context and best practices:

1. **For Technical Intents**: 
   - **Software Development**: Provide frameworks, tools, programming languages, architecture patterns
   - **Web Development**: Include frontend/backend technologies, databases, deployment strategies
   - **Mobile App Development**: Cover platform-specific considerations, development tools, app store guidelines
   - **Data Science**: Include libraries, methodologies, data processing techniques
   - Focus on implementation details, code structure, and technical best practices

2. **For Creative Intents**:
   - **Content Writing**: Include writing techniques, style guides, audience targeting
   - **Graphic Design**: Cover design principles, tools, trends, and visual hierarchy
   - **Marketing Copy**: Include persuasion techniques, conversion optimization, brand voice
   - Focus on creative processes, inspiration sources, and effective creative strategies

3. **For Business Intents**:
   - **Strategy Consulting**: Include frameworks (SWOT, Porter's 5 Forces), market analysis
   - **Product Management**: Cover user research, roadmapping, feature prioritization
   - **Marketing**: Include campaign strategies, metrics, customer acquisition
   - Focus on business objectives, ROI measurement, and stakeholder considerations

4. **For Academic Intents**:
   - **Research Methodology**: Include study design, data collection, analysis methods
   - **Academic Writing**: Cover citation styles, paper structure, peer review process
   - **Data Analysis**: Include statistical methods, research tools, interpretation techniques
   - Focus on academic rigor, evidence-based approaches, and scholarly standards

5. **For Personal Intents**:
   - **Productivity**: Include time management systems, habit formation, goal setting
   - **Life Planning**: Cover goal-setting frameworks, decision-making models
   - **Fitness/Health**: Include evidence-based approaches, tracking methods
   - Focus on personal development, sustainable practices, and practical implementation

**Critical Domain-Specific Guidelines**:
- If domain is "web development" or "mobile app development" → Focus on TECHNICAL implementation, not productivity advice
- If domain is "productivity" → Focus on personal systems and habits, not software development
- If domain is "software engineering" → Include code architecture, best practices, development processes
- If domain is "content marketing" → Include strategy, audience analysis, content planning

**Important**: Match the context to the SPECIFIC DOMAIN, not just the general intent category. A "todo list" request in "web development" domain needs technical implementation context, while in "productivity" domain needs personal organization context.

Format your response as:
## Research Summary
[Your analysis and key findings specific to the domain]

## Key Insights
- [Domain-specific insights and considerations]

## Best Practices
- [Relevant best practices for this specific domain]

## Technical/Implementation Context (if technical domain)
- [Specific technologies, frameworks, tools, and implementation approaches]

## Relevant Context
[Additional domain-specific context that would improve prompt enhancement]""",
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
    Orchestrates the multi-agent enhancement process:
    1. Classify intent
    2. Generate supporting content with domain knowledge
    3. Create dynamically enhanced prompt
    """
    
    # Step 1: Classify Intent
    print("🎯 Classifying intent...")
    intent_result = await Runner.run(intent_classifier_agent, user_prompt)
    intent_data = parse_intent_json(intent_result.final_output)
    
    print(f"Intent: {intent_data.intent_category} ({intent_data.confidence:.1%} confidence)")
    print(f"Domain: {intent_data.specific_domain}")
    print(f"Complexity: {intent_data.complexity_level}")
    print(f"Needs context: {intent_data.requires_context}")
    
    # Step 2: Generate Supporting Content (if needed)
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
        
        support_result = await Runner.run(supporting_content_agent, support_prompt)
        supporting_context = support_result.final_output
        research_performed = True
        print(f"Context gathered: {len(supporting_context)} characters")
    
    # Step 3: Generate Best Practices (if needed)
    best_practices_context = ""
    if intent_data.complexity_level in ["intermediate", "advanced"]:
        print("🔍 Gathering best practices...")
        best_practices_prompt = f"""
        Intent Analysis: {intent_data.dict()}
        Original Prompt: {user_prompt}
        
        Please provide the most current and effective prompt writing best practices that should be applied universally, regardless of the specific intent or domain.
        """
        best_practices_result = await Runner.run(best_practices_agent, best_practices_prompt)
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
    
    # Step 5: Generate Enhanced Prompt
    enhancement_result = await Runner.run(enhancer_agent, user_prompt)
    
    return {
        "enhanced_prompt": enhancement_result.final_output,
        "intent_analysis": intent_data.dict(),
        "supporting_context_length": len(supporting_context),
        "best_practices_length": len(best_practices_context),
        "web_research_performed": research_performed,
        "best_practices_applied": bool(best_practices_context),
        "process_steps": ["intent_classification", "knowledge_research", "best_practices_gathering", "dynamic_enhancement"] if best_practices_context else ["intent_classification", "knowledge_research", "dynamic_enhancement"]
    }

# --- FastAPI Application ---

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class PromptRequest(BaseModel):
    prompt: str

@app.post("/enhance")
async def enhance_prompt(request: PromptRequest):
    try:
        result = await orchestrate_enhancement(request.prompt)
        return result
    except InputGuardrailTripwireTriggered:
        return {
            "enhanced_prompt": "This prompt violates our safety guidelines and cannot be processed.",
            "intent_analysis": {"intent_category": "blocked", "confidence": 1.0},
            "supporting_context_length": 0,
            "best_practices_length": 0,
            "web_research_performed": False,
            "best_practices_applied": False,
            "process_steps": ["safety_block"]
        }
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "agents": ["intent_classifier", "supporting_content", "best_practices", "dynamic_enhancer"],
        "research_method": "knowledge_based",
        "best_practices_search": "enabled" if LITELLM_AVAILABLE else "knowledge_based"
    } 