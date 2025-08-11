from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
from enhanced_agents import orchestrate_enhancement, InputGuardrailTripwireTriggered
from image_agent import process_image, ImageAgent
from response_agent import format_response, detect_content_format, OutputFormat

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Agent orchestration is handled by the enhanced_agents module


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# Pehance Models
class PromptEnhanceRequest(BaseModel):
    prompt: str
    mode: str = "single"  # "single" or "multi" - defaults to single turn
    image_data: Optional[str] = None  # Base64 encoded image
    preferred_format: Optional[str] = "auto_detect"  # Output format preference

class ImageUploadRequest(BaseModel):
    image_data: str  # Base64 encoded image
    analysis_type: str = "comprehensive"  # comprehensive, text_extraction, quick_description

class ImageProcessResponse(BaseModel):
    success: bool
    description: str
    extracted_text: Optional[str] = None
    analysis: Dict[str, Any] = {}
    suggestions: List[str] = []

class ResponseFormatRequest(BaseModel):
    content: str
    target_format: str = "auto_detect"  # rich_text, code_blocks, markdown, plain_text, auto_detect
    enhance_quality: bool = True

class ResponseFormatResponse(BaseModel):
    formatted_content: str
    detected_format: str
    metadata: Dict[str, Any] = {}
    code_blocks: List[Dict] = []

class PromptEnhanceResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_prompt: str
    enhanced_prompt: str
    agent_results: Dict[str, Any]
    success: bool
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    mode: str = "single"  # Mode used for enhancement
    # NEW: Additional fields for 4D methodology tracking
    enhancement_type: Optional[str] = None  # clarification_request, basic_enhancement, standard_enhancement, advanced_enhancement
    enhancement_ratio: Optional[float] = None
    complexity_score: Optional[float] = None
    models_used: Optional[Dict[str, Optional[str]]] = None  # Track which models were used for each step

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Model testing endpoint
@api_router.get("/test-models")
async def test_models():
    """Test all available models and return their availability status with performance metrics"""
    try:
        from enhanced_agents import ModelConfig
        
        # Test all model tiers
        models_to_test = [
            # Tier 1: Ultra-Fast
            ModelConfig.ULTRA_FAST_MODEL,
            # Tier 2: Balanced
            ModelConfig.BALANCED_MODEL,
            ModelConfig.BALANCED_ALT,
            # Tier 3: High-Reasoning
            ModelConfig.REASONING_MODEL,
            ModelConfig.REASONING_ALT,
            # Tier 4: Specialized
            ModelConfig.ADVANCED_REASONING,
            ModelConfig.CREATIVE_MODEL,
            ModelConfig.ADVANCED_COMPLEX,
            # Safety
            ModelConfig.SAFETY_MODEL,
            ModelConfig.SAFETY_FALLBACK,
            # Fallback
            ModelConfig.LEGACY_FALLBACK
        ]
        
        results = {}
        available_count = 0
        total_models = len(models_to_test)
        
        def get_model_tier(model_name: str) -> str:
            """Determine the tier of a given model"""
            if model_name == ModelConfig.ULTRA_FAST_MODEL:
                return "Tier 1: Ultra-Fast"
            elif model_name in [ModelConfig.BALANCED_MODEL, ModelConfig.BALANCED_ALT]:
                return "Tier 2: Balanced"
            elif model_name in [ModelConfig.REASONING_MODEL, ModelConfig.REASONING_ALT]:
                return "Tier 3: High-Reasoning"
            elif model_name in [ModelConfig.ADVANCED_REASONING, ModelConfig.CREATIVE_MODEL, ModelConfig.ADVANCED_COMPLEX]:
                return "Tier 4: Specialized"
            elif model_name in [ModelConfig.SAFETY_MODEL, ModelConfig.SAFETY_FALLBACK]:
                return "Safety Models"
            elif model_name == ModelConfig.LEGACY_FALLBACK:
                return "Legacy Fallback"
            else:
                return "Unknown"
        
        for model in models_to_test:
            try:
                is_available = await ModelConfig.test_model_availability(model)
                performance = ModelConfig.MODEL_PERFORMANCE.get(model, "Unknown")
                features = ModelConfig.MODEL_FEATURES.get(model, [])
                
                if is_available:
                    available_count += 1
                
                results[model] = {
                    "available": is_available,
                    "status": "✅ Available" if is_available else "❌ Not Available",
                    "performance_tokens_sec": performance,
                    "features": features,
                    "tier": get_model_tier(model)
                }
            except Exception as e:
                results[model] = {
                    "available": False,
                    "status": f"❌ Error: {str(e)}",
                    "performance_tokens_sec": "Unknown",
                    "features": [],
                    "tier": "Unknown"
                }
        
        return {
            "success": True,
            "models": results,
            "summary": {
                "total_models": total_models,
                "available_models": available_count,
                "availability_rate": f"{(available_count/total_models)*100:.1f}%",
                "recommended_fast": ModelConfig.ULTRA_FAST_MODEL,
                "recommended_reasoning": ModelConfig.REASONING_MODEL,
                "recommended_creative": ModelConfig.CREATIVE_MODEL,
                "safety_model": ModelConfig.SAFETY_MODEL
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Model testing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Model testing error: {str(e)}")

# Simple test endpoint for debugging
@api_router.post("/test-groq")
async def test_groq(request: PromptEnhanceRequest):
    """Simple test endpoint to verify Groq API connectivity"""
    try:
        from groq import Groq
        import os
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": request.prompt}],
            max_tokens=100,
            timeout=15
        )
        
        return {
            "success": True,
            "response": response.choices[0].message.content,
            "model": "llama3-8b-8192"
        }
    except Exception as e:
        logger.error(f"Groq test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Groq API error: {str(e)}")

# Image processing endpoint
@api_router.post("/process-image", response_model=ImageProcessResponse)
async def process_image_endpoint(request: ImageUploadRequest):
    """
    Process uploaded image and extract meaningful information for prompt enhancement
    """
    try:
        # Validate image data
        is_valid, error_msg = ImageAgent.validate_image_base64(request.image_data)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Process the image
        result = await process_image(request.image_data, request.analysis_type)
        
        # Generate suggestions based on the analysis
        suggestions = []
        if result.analysis.get("requires_user_description"):
            suggestions = [
                "Describe what you see in the image to get better enhancement",
                "Tell me what you want to accomplish with this image content",
                "Mention any specific text or elements you'd like me to focus on"
            ]
        elif result.extracted_text:
            suggestions = [
                "Enhance this extracted text into a comprehensive prompt",
                "Create a tutorial based on this content",
                "Transform this into step-by-step instructions"
            ]
        else:
            suggestions = [
                "Create a detailed prompt based on this image analysis",
                "Generate creative content inspired by this image",
                "Build documentation from this visual content"
            ]
        
        return ImageProcessResponse(
            success=True,
            description=result.description,
            extracted_text=result.extracted_text,
            analysis=result.analysis,
            suggestions=suggestions
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Image processing error: {str(e)}")

# Response formatting endpoint
@api_router.post("/format-response", response_model=ResponseFormatResponse)
async def format_response_endpoint(request: ResponseFormatRequest):
    """
    Format response content with enhanced styling and structure
    """
    try:
        # Format the response
        result = await format_response(
            request.content,
            request.target_format,
            request.enhance_quality
        )
        
        return ResponseFormatResponse(
            formatted_content=result.formatted_content,
            detected_format=result.detected_format.value,
            metadata=result.metadata,
            code_blocks=result.code_blocks
        )
        
    except Exception as e:
        logger.error(f"Response formatting failed: {e}")
        raise HTTPException(status_code=500, detail=f"Response formatting error: {str(e)}")

# Enhanced multi-modal prompt enhancement endpoint
@api_router.post("/enhance-multimodal", response_model=PromptEnhanceResponse)
async def enhance_multimodal_prompt(request: PromptEnhanceRequest):
    """
    Enhanced prompt enhancement with multi-modal support (text + image)
    """
    try:
        combined_prompt = request.prompt
        image_analysis = None
        
        # Validate prompt when no image provided
        if (not request.prompt or not request.prompt.strip()) and not request.image_data:
            raise HTTPException(status_code=400, detail="Either prompt or image_data is required")

        # Process image if provided
        if request.image_data:
            print("🖼️ Processing image input...")
            
            # Validate and process image
            is_valid, error_msg = ImageAgent.validate_image_base64(request.image_data)
            if not is_valid:
                raise HTTPException(status_code=400, detail=f"Invalid image: {error_msg}")
            
            # Process image to extract meaningful information
            image_result = await process_image(request.image_data, "comprehensive")
            image_analysis = {
                "description": image_result.description,
                "extracted_text": image_result.extracted_text,
                "analysis": image_result.analysis
            }
            
            # Combine text prompt with image analysis
            if image_result.description:
                if request.prompt.strip():
                    combined_prompt = f"""User Request: {request.prompt}

Image Analysis: {image_result.description}

{f"Extracted Text from Image: {image_result.extracted_text}" if image_result.extracted_text else ""}

Please enhance this prompt taking into account both the user's text request and the visual information provided in the image."""
                else:
                    combined_prompt = f"""Based on this image analysis: {image_result.description}

{f"Extracted Text: {image_result.extracted_text}" if image_result.extracted_text else ""}

Please create an enhanced prompt that helps the user accomplish their goals with this image content."""
        
        # Run the enhanced multi-agent enhancement pipeline
        result = await orchestrate_enhancement(combined_prompt, mode=request.mode)
        
        # Format the response if preferred format is specified
        enhanced_prompt = result["enhanced_prompt"]
        format_metadata = {}
        
        if request.preferred_format and request.preferred_format != "auto_detect":
            print(f"🎨 Formatting response as: {request.preferred_format}")
            format_result = await format_response(enhanced_prompt, request.preferred_format, True)
            enhanced_prompt = format_result.formatted_content
            format_metadata = {
                "formatted": True,
                "format_type": format_result.detected_format.value,
                "format_metadata": format_result.metadata
            }
        
        # Create response object with multi-modal enhancements
        response = PromptEnhanceResponse(
            original_prompt=request.prompt,
            enhanced_prompt=enhanced_prompt,
            agent_results={
                **result,
                "image_analysis": image_analysis,
                "format_metadata": format_metadata,
                "multimodal": request.image_data is not None
            },
            success=True,
            error=None,
            mode=request.mode,
            enhancement_type=result.get("enhancement_type"),
            enhancement_ratio=result.get("enhancement_ratio"),
            complexity_score=result.get("complexity_score"),
            models_used=result.get("models_used")
        )
        
        # Store in database for analytics
        await db.prompt_enhancements.insert_one(response.dict())
        
        return response
        
    except InputGuardrailTripwireTriggered as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Content safety check failed: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Multi-modal enhancement error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Content format detection endpoint
class DetectFormatRequest(BaseModel):
    content: str

class DetectFormatResponse(BaseModel):
    detected_format: str
    confidence: str
    suggestions: Dict[str, str]

@api_router.post("/detect-format", response_model=DetectFormatResponse)
async def detect_content_format_endpoint(request: DetectFormatRequest):
    """
    Auto-detect the most appropriate format for content
    """
    try:
        detected_format = detect_content_format(request.content)
        return DetectFormatResponse(
            detected_format=detected_format,
            confidence="high",  # Could be enhanced with confidence scoring
            suggestions={
                "rich_text": "Best for instructional and explanatory content",
                "code_blocks": "Best for technical content with code",
                "markdown": "Best for structured documentation",
                "plain_text": "Best for simple, unformatted content"
            }
        )
    except Exception as e:
        logger.error(f"Format detection failed: {e}")
        raise HTTPException(status_code=500, detail="Format detection error")
@api_router.post("/enhance", response_model=PromptEnhanceResponse)
async def enhance_prompt(request: PromptEnhanceRequest):
    """
    Enhanced prompt enhancement using sophisticated 4D methodology multi-agent system:
    1. Intent Classifier - identifies user's goal, domain, complexity, and routes appropriately
    2. Supporting Content - gathers domain-specific context (when needed)
    3. Best Practices - applies 4-D methodology (scaled to complexity)
    4. Dynamic Enhancer - generates proportionally enhanced prompt (prevents over-enhancement)
    
    Supports two modes:
    - single: Always provides enhanced prompt directly (no follow-up questions)
    - multi: Allows conversational follow-ups when needed
    """
    try:
        # Validate prompt
        if not request.prompt or not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")

        # Run the enhanced multi-agent enhancement pipeline with mode awareness
        result = await orchestrate_enhancement(request.prompt, mode=request.mode)
        
        # Create response object with the enhanced result structure
        response = PromptEnhanceResponse(
            original_prompt=request.prompt,
            enhanced_prompt=result["enhanced_prompt"], 
            agent_results=result,
            success=True,
            error=None,
            mode=request.mode,
            enhancement_type=result.get("enhancement_type"),
            enhancement_ratio=result.get("enhancement_ratio"),
            complexity_score=result.get("complexity_score"),
            models_used=result.get("models_used")
        )
        
        # Store in database for analytics
        await db.prompt_enhancements.insert_one(response.dict())
        
        return response
        
    except InputGuardrailTripwireTriggered as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Content safety check failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in enhance_prompt: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
