import base64
import io
import asyncio
import json
from typing import Optional, Dict, Any
from PIL import Image
import logging
from agents_framework import Agent, Runner
from enhanced_agents import select_model_for_task, rate_limited_request, ModelConfig

logger = logging.getLogger(__name__)

class ImageProcessingResult:
    """Result of image processing operation"""
    def __init__(self, description: str, extracted_text: str = "", analysis: Dict[str, Any] = None):
        self.description = description
        self.extracted_text = extracted_text
        self.analysis = analysis or {}

class ImageAgent:
    """Specialized agent for processing images and converting them to meaningful text input"""
    
    @staticmethod
    async def process_image_base64(image_base64: str, analysis_type: str = "comprehensive") -> ImageProcessingResult:
        """
        Process a base64 encoded image and extract meaningful information
        
        Args:
            image_base64: Base64 encoded image string
            analysis_type: Type of analysis to perform (comprehensive, text_extraction, quick_description)
            
        Returns:
            ImageProcessingResult with description and extracted information
        """
        try:
            # Validate and process the base64 image
            if not image_base64 or not isinstance(image_base64, str):
                raise ValueError("Invalid base64 image data")
            
            # Clean base64 string (remove data URL prefix if present)
            if image_base64.startswith('data:image'):
                image_base64 = image_base64.split(',')[1]
            
            # Select the best available vision model
            vision_models = [
                ModelConfig.BALANCED_MODEL,  # llama-4-scout supports image input
                ModelConfig.ADVANCED_REASONING,  # llama-4-maverick supports image input
                ModelConfig.REASONING_MODEL  # fallback
            ]
            
            selected_model = await ModelConfig.get_best_available_model(vision_models)
            
            # Check if selected model supports image input
            model_features = ModelConfig.MODEL_FEATURES.get(selected_model, [])
            supports_vision = "image_input" in model_features
            
            if supports_vision:
                return await ImageAgent._process_with_vision_model(image_base64, selected_model, analysis_type)
            else:
                logger.warning(f"Model {selected_model} doesn't support vision, falling back to description-based processing")
                return await ImageAgent._process_without_vision(image_base64, selected_model, analysis_type)
                
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            return ImageProcessingResult(
                description="Unable to process image. Please describe the image content in text.",
                analysis={"error": str(e), "fallback_required": True}
            )
    
    @staticmethod
    async def _process_with_vision_model(image_base64: str, model: str, analysis_type: str) -> ImageProcessingResult:
        """Process image using vision-capable model"""
        try:
            print(f"🖼️ Processing image with vision model: {model}")
            
            # Create analysis prompt based on type
            prompts = {
                "comprehensive": """Analyze this image comprehensively and provide:

1. **Visual Description**: What do you see in the image? Include objects, people, text, colors, composition, style.

2. **Content Analysis**: 
   - What appears to be the main subject or focus?
   - Is this a screenshot, diagram, photo, artwork, document, etc.?
   - Are there any text elements, UI elements, or interface components?

3. **Context Extraction**: 
   - What context or information can be derived from this image?
   - Is this related to technology, business, education, creative work, etc.?
   - What might the user want to do with this image content?

4. **Text Extraction**: If there's any readable text in the image, extract it accurately.

5. **Actionable Insights**: Based on the image content, what kind of tasks or prompts might be relevant?

Provide a detailed analysis that would help understand what the user might want to accomplish with this image.""",

                "text_extraction": """Focus on extracting and transcribing any text visible in this image. This includes:

1. **Text Content**: Extract all readable text, maintaining formatting and structure where possible
2. **Text Classification**: Is this code, documentation, UI text, handwritten notes, printed material, etc.?  
3. **Context**: What type of document or interface does this text appear to be from?
4. **Clarity Assessment**: Is the text clear and complete, or are there parts that are unclear/cut off?

If there's no readable text, describe what type of visual content this is instead.""",

                "quick_description": """Provide a concise but informative description of this image that would help someone understand what it contains and its potential relevance for creating prompts or instructions."""
            }
            
            prompt = prompts.get(analysis_type, prompts["comprehensive"])
            
            # Create vision agent
            vision_agent = Agent(
                name="Image Analysis Specialist",
                instructions=f"""You are an expert image analysis specialist. {prompt}
                
**CRITICAL**: Provide detailed, accurate analysis that converts visual information into actionable text that can be used for prompt enhancement.""",
                model=model
            )
            
            # For vision models, we need to format the input properly
            # Note: This is a simplified approach - actual implementation may vary by model
            image_input = f"Image (base64): {image_base64[:100]}..." # Truncated for display
            
            result = await rate_limited_request(Runner.run, vision_agent, image_input)
            
            # Parse the result to extract different components
            analysis_text = result.final_output
            
            # Try to extract text content if mentioned in the analysis
            extracted_text = ImageAgent._extract_text_from_analysis(analysis_text)
            
            return ImageProcessingResult(
                description=analysis_text,
                extracted_text=extracted_text,
                analysis={
                    "model_used": model,
                    "analysis_type": analysis_type,
                    "supports_vision": True,
                    "processing_method": "vision_model"
                }
            )
            
        except Exception as e:
            logger.error(f"Vision model processing failed: {e}")
            # Fallback to description-based processing
            return await ImageAgent._process_without_vision(image_base64, model, analysis_type)
    
    @staticmethod
    async def _process_without_vision(image_base64: str, model: str, analysis_type: str) -> ImageProcessingResult:
        """Process image without direct vision support - use metadata and provide structured response"""
        try:
            print(f"🖼️ Processing image without vision support using model: {model}")
            
            # Try to get basic image metadata
            try:
                # Decode base64 and get basic image info
                image_data = base64.b64decode(image_base64)
                image = Image.open(io.BytesIO(image_data))
                width, height = image.size
                format_type = image.format or "Unknown"
                mode = image.mode
                
                metadata = f"Image metadata: {width}x{height} pixels, format: {format_type}, mode: {mode}"
            except Exception as e:
                metadata = "Unable to extract image metadata"
                logger.warning(f"Metadata extraction failed: {e}")
            
            # Create a structured response based on analysis type
            if analysis_type == "text_extraction":
                description = f"""I can see that you've uploaded an image, but I need vision capabilities to extract text from it. 

{metadata}

To help you with text extraction, please:
1. If this contains text you'd like to transcribe, you can type it out or describe what kind of text it contains
2. If this is a screenshot of code, documentation, or interface, describe what you're trying to accomplish
3. Let me know what specific text content you need help with

I can then help you create an enhanced prompt based on that information."""

            elif analysis_type == "quick_description":
                description = f"""I can see you've uploaded an image ({metadata}), but I need to understand more about what you'd like to do with it.

Could you describe:
- What the image contains (screenshot, photo, diagram, etc.)
- What you're trying to accomplish with this image
- Any specific text or elements you'd like me to focus on

This will help me create an enhanced prompt tailored to your needs."""

            else:  # comprehensive
                description = f"""I can see you've uploaded an image for analysis. While I cannot directly view the image content, I can help you create powerful prompts based on what you're trying to accomplish.

{metadata}

To provide the best assistance, please describe:

1. **Image Content**: What does the image show? (screenshot, photo, diagram, document, code, etc.)
2. **Your Goal**: What do you want to do with this image or its content?
3. **Specific Elements**: Are there particular text, code, or visual elements you want to focus on?
4. **Desired Output**: What kind of response or action are you looking for?

With this information, I can create a comprehensive, enhanced prompt that will help you achieve your goals effectively."""

            return ImageProcessingResult(
                description=description,
                extracted_text="",
                analysis={
                    "model_used": model,
                    "analysis_type": analysis_type,
                    "supports_vision": False,
                    "processing_method": "metadata_only",
                    "requires_user_description": True
                }
            )
            
        except Exception as e:
            logger.error(f"Fallback processing failed: {e}")
            return ImageProcessingResult(
                description="I can see you've uploaded an image, but I'm having trouble processing it. Could you describe what the image contains and what you'd like to accomplish? This will help me create an enhanced prompt for you.",
                analysis={"error": str(e), "processing_method": "error_fallback"}
            )
    
    @staticmethod
    def _extract_text_from_analysis(analysis_text: str) -> str:
        """Extract any mentioned text content from the analysis"""
        try:
            # Look for common patterns where text might be mentioned
            text_indicators = [
                "text content:", "extracted text:", "readable text:", 
                "text reads:", "text says:", "contains the text:"
            ]
            
            extracted_parts = []
            lines = analysis_text.split('\n')
            
            capturing = False
            for line in lines:
                line_lower = line.lower().strip()
                
                # Check if this line indicates text content
                if any(indicator in line_lower for indicator in text_indicators):
                    capturing = True
                    continue
                
                # If we're capturing and find actual text content
                if capturing and line.strip():
                    # Stop capturing if we hit another section
                    if line.startswith('#') or line.startswith('**') or line.startswith('##'):
                        break
                    extracted_parts.append(line.strip())
            
            return '\n'.join(extracted_parts) if extracted_parts else ""
            
        except Exception as e:
            logger.warning(f"Text extraction from analysis failed: {e}")
            return ""

    @staticmethod
    def validate_image_base64(image_base64: str) -> tuple[bool, str]:
        """
        Validate base64 image data
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not image_base64:
                return False, "No image data provided"
            
            # Clean base64 string
            if image_base64.startswith('data:image'):
                image_base64 = image_base64.split(',')[1]
            
            # Try to decode and validate as image
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data))
            
            # Check reasonable size limits (e.g., not larger than 10MB)
            if len(image_data) > 10 * 1024 * 1024:
                return False, "Image too large (max 10MB)"
            
            # Check reasonable dimensions
            width, height = image.size
            if width > 4000 or height > 4000:
                return False, "Image dimensions too large (max 4000x4000)"
            
            return True, "Valid image"
            
        except Exception as e:
            return False, f"Invalid image data: {str(e)}"

# Factory function for easy import
async def process_image(image_base64: str, analysis_type: str = "comprehensive") -> ImageProcessingResult:
    """
    Main entry point for image processing
    
    Args:
        image_base64: Base64 encoded image
        analysis_type: Type of analysis to perform
        
    Returns:
        ImageProcessingResult with extracted information
    """
    return await ImageAgent.process_image_base64(image_base64, analysis_type)