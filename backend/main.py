from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
from dotenv import load_dotenv
from PIL import Image
import io
import openai
from pathlib import Path
import base64
import cv2
import numpy as np

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

def preprocess_image(image: Image.Image) -> str:
    """Convert image to base64 string."""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def postprocess_image(image_data: str) -> Image.Image:
    """Convert base64 string back to image."""
    image_bytes = base64.b64decode(image_data)
    return Image.open(io.BytesIO(image_bytes))

def apply_edge_detection(image: Image.Image, difficulty: str) -> Image.Image:
    """Apply edge detection based on difficulty level."""
    # Convert PIL Image to OpenCV format
    cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Edge detection parameters based on difficulty
    if difficulty == "easy":
        threshold1, threshold2 = 50, 150
        kernel_size = 3
    elif difficulty == "medium":
        threshold1, threshold2 = 100, 200
        kernel_size = 5
    else:  # hard
        threshold1, threshold2 = 150, 250
        kernel_size = 7
    
    # Apply Canny edge detection
    edges = cv2.Canny(blurred, threshold1, threshold2, kernel_size)
    
    # Invert the image to get white lines on black background
    edges = cv2.bitwise_not(edges)
    
    # Convert back to PIL Image
    return Image.fromarray(edges)

@app.get("/")
async def read_root():
    return {"message": "Welcome to Kleurplatenmaken.ai API"}

@app.post("/convert")
async def convert_image(
    file: UploadFile = File(...),
    difficulty: str = "medium"  # easy, medium, hard
):
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Read and validate image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Apply edge detection
        coloring_page = apply_edge_detection(image, difficulty)
        
        # Save the coloring page
        output_path = UPLOAD_DIR / f"coloring_page_{difficulty}_{file.filename}"
        coloring_page.save(output_path, "PNG")
        
        return FileResponse(output_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 