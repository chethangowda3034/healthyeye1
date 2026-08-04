import os
import io
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from google import genai
from google.genai import types

app = FastAPI(title="HealthyEye API")

# Enable CORS for all origins (allows Vercel frontend to query Render backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini Client using system environment variable GEMINI_API_KEY
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    client = None
else:
    client = genai.Client(api_key=api_key)

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
def read_root():
    return {"status": "ok", "message": "HealthyEye API is running"}

@app.post("/analyze-medicine")
async def analyze_medicine(file: UploadFile = File(...)):
    if not client:
        raise HTTPException(
            status_code=500, 
            detail="GEMINI_API_KEY environment variable is not configured on the server."
        )

    try:
        # Read uploaded image bytes
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        # Call Gemini SDK
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[SYSTEM_PROMPT, image]
        )

        return {"success": True, "analysis": response.text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))