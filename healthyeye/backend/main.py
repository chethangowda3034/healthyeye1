import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types

app = FastAPI(title="HealthyEye API")

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Read API key securely from Render Environment Variables
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    client = genai.Client(api_key=api_key)
else:
    client = None

SYSTEM_PROMPT = """
You are HealthyEye, an AI health assistant. 
Analyze the provided medicine image (tablet strip, syrup bottle, cream tube, or prescription).
Provide a concise, plain-language summary in bullet points:
1. Active Ingredients / Chemical Name
2. Common Purpose / What it treats
3. General Usage / Administration instructions
4. Key Warnings / Precautions

Keep language simple and easy for everyday consumers to understand.
"""

@app.get("/")
def health_check():
    return {
        "status": "ok", 
        "message": "HealthyEye API is running",
        "api_key_configured": api_key is not None
    }

@app.post("/analyze-medicine")
async def analyze_medicine(file: UploadFile = File(...)):
    # 1. Verify GEMINI_API_KEY presence
    if not client:
        raise HTTPException(
            status_code=500, 
            detail="GEMINI_API_KEY environment variable is missing on Render."
        )

    try:
        # 2. Read raw image file bytes
        file_bytes = await file.read()

        # 3. Format image for Gemini using types.Part.from_bytes
        image_part = types.Part.from_bytes(
            data=file_bytes,
            mime_type=file.content_type or "image/jpeg"
        )

        # 4. Generate analysis
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[SYSTEM_PROMPT, image_part]
        )

        return {
            "success": True, 
            "analysis": response.text
        }

    except Exception as e:
        print(f"Backend Exception Error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Gemini API Error: {str(e)}"
        )