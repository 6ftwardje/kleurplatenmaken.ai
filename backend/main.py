from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
from dotenv import load_dotenv
from PIL import Image
import io
import base64
from pathlib import Path
import openai
import logging
import requests

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize OpenAI client with API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.error("OPENAI_API_KEY not found in environment variables")
    raise ValueError("OPENAI_API_KEY environment variable is required")

client = openai.OpenAI(api_key=api_key)
logger.info("OpenAI client initialized successfully")

# Initialize FastAPI app
app = FastAPI(title="Kleurplatenmaken.ai API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
logger.info(f"Upload directory created/verified at: {UPLOAD_DIR}")

def encode_image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 string."""
    try:
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    except Exception as e:
        logger.error(f"Error encoding image to base64: {str(e)}")
        raise

def download_image(url: str) -> bytes:
    """Download image from URL."""
    try:
        logger.info(f"Downloading image from URL: {url}")
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except Exception as e:
        logger.error(f"Error downloading image: {str(e)}")
        raise

def generate_coloring_page(image: Image.Image, difficulty: str) -> Image.Image:
    """Generate a coloring page using OpenAI's Vision API and DALL-E."""
    try:
        logger.info(f"Starting coloring page generation with difficulty: {difficulty}")
        
        # Convert image to base64
        base64_image = encode_image_to_base64(image)
        logger.debug("Image successfully converted to base64")
        
        # First, analyze the image using Vision API
        logger.info("Sending image to GPT-4 Vision for analysis")
        try:
            vision_response = client.chat.completions.create(
                model="gpt-4-vision-preview-v2",  # Updated model name
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Analyze this image and describe it in detail. Focus on the main elements, shapes, and lines that would make a good coloring page. Consider the difficulty level: {difficulty}. For easy, keep it simple with basic shapes. For medium, add more details. For hard, include intricate patterns and details."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            # Get the image description
            image_description = vision_response.choices[0].message.content
            logger.info("Received image analysis from GPT-4 Vision")
            logger.debug(f"Image description: {image_description}")
            
        except Exception as e:
            logger.error(f"Error in GPT-4 Vision API call: {str(e)}")
            # Fallback to DALL-E directly if Vision API fails
            image_description = f"Create a {difficulty} difficulty coloring page based on the uploaded image. For {difficulty} difficulty, {'keep it simple with basic shapes' if difficulty == 'easy' else 'add moderate detail and patterns' if difficulty == 'medium' else 'include intricate patterns and detailed elements'}."
            logger.info("Using fallback description for DALL-E")
        
        # Generate the coloring page using DALL-E
        logger.info("Sending request to DALL-E for image generation")
        dalle_response = client.images.generate(
            model="dall-e-3",
            prompt=f"Create a detailed coloring page based on this description: {image_description}. Make it a black and white line drawing suitable for coloring. The lines should be clear and distinct. For {difficulty} difficulty level, adjust the complexity accordingly. Use only black lines on white background, no shading or grayscale.",
            n=1,
            size="1024x1024",
            quality="standard",
            style="natural"
        )
        
        # Get the image URL from DALL-E response
        image_url = dalle_response.data[0].url
        logger.info("Received image URL from DALL-E")
        
        # Download the image
        logger.info("Downloading generated image")
        image_data = download_image(image_url)
        
        # Convert to PIL Image
        result_image = Image.open(io.BytesIO(image_data))
        logger.info("Successfully generated coloring page")
        return result_image
        
    except Exception as e:
        logger.error(f"Error in generate_coloring_page: {str(e)}")
        raise

@app.get("/")
async def read_root():
    return {"message": "Welcome to Kleurplatenmaken.ai API"}

@app.post("/convert")
async def convert_image(
    file: UploadFile = File(...),
    difficulty: str = "medium"  # easy, medium, hard
):
    try:
        logger.info(f"Received conversion request for file: {file.filename} with difficulty: {difficulty}")
        
        # Validate file type
        if not file.content_type.startswith("image/"):
            logger.error(f"Invalid file type: {file.content_type}")
            raise HTTPException(status_code=400, detail="File must be an image")

        # Read and validate image
        contents = await file.read()
        logger.debug(f"Read {len(contents)} bytes from uploaded file")
        
        image = Image.open(io.BytesIO(contents))
        logger.debug(f"Successfully opened image with size: {image.size}")
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            logger.debug(f"Converting image from {image.mode} to RGB")
            image = image.convert('RGB')
        
        # Generate coloring page using OpenAI
        logger.info("Starting coloring page generation")
        coloring_page = generate_coloring_page(image, difficulty)
        
        # Save the coloring page
        output_path = UPLOAD_DIR / f"coloring_page_{difficulty}_{file.filename}"
        coloring_page.save(output_path, "PNG")
        logger.info(f"Saved coloring page to: {output_path}")
        
        return FileResponse(output_path)

    except Exception as e:
        logger.error(f"Error in convert_image endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 