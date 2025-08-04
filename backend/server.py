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

# Pehance Enhancement Endpoint
@api_router.post("/enhance", response_model=PromptEnhanceResponse)
async def enhance_prompt(request: PromptEnhanceRequest):
    """
    Enhanced prompt enhancement using sophisticated 4D methodology multi-agent system:
    1. Intent Classifier - identifies user's goal, domain, complexity, and routes appropriately
    2. Supporting Content - gathers domain-specific context (when needed)
    3. Best Practices - applies 4-D methodology (scaled to complexity)
    4. Dynamic Enhancer - generates proportionally enhanced prompt (prevents over-enhancement)
    """
    try:
        # Run the enhanced multi-agent enhancement pipeline
        result = await orchestrate_enhancement(request.prompt)
        
        # Create response object with the enhanced result structure
        response = PromptEnhanceResponse(
            original_prompt=request.prompt,
            enhanced_prompt=result["enhanced_prompt"], 
            agent_results=result,
            success=True,
            error=None,
            enhancement_type=result.get("enhancement_type"),
            enhancement_ratio=result.get("enhancement_ratio"),
            complexity_score=result.get("complexity_score")
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
