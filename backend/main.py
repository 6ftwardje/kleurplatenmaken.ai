from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
from dotenv import load_dotenv
from PIL import Image
import io
import openai
from pathlib import Path

# Load environment variables
load_dotenv()

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
        
        # Save original image
        original_path = UPLOAD_DIR / f"original_{file.filename}"
        image.save(original_path)

        # TODO: Implement AI conversion logic here
        # For now, we'll just return the original image
        return FileResponse(original_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 