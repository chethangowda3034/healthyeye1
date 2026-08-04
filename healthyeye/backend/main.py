import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types

app = FastAPI(title="HealthyEye API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    client = genai.Client(api_key=api_key)
else:
    client = None

# Streamlined, high-density prompt
SYSTEM_PROMPT = """
You are HealthyEye. Analyze the medicine image and provide a highly concise, punchy breakdown. 

Keep answers brief (1-2 sentences max per point):

### 💊 Medicine Overview
* **Name & Strength:** [Brand + Active Ingredient + Dose]
* **Category:** [Pharmacological class]

### 🌍 Global Trust & Acceptance
* **Safety Rating:** [e.g., 4.7/5 ⭐ based on global clinical consensus]
* **Regulatory Status:** [Approval status: e.g., FDA / EMA / WHO approved]

### 🩺 Primary Uses
* [2-3 quick bullet points on key conditions treated]

### ⚠️ Key Warnings
* **Side Effects:** [Top 2-3 common side effects]
* **Caution:** [Primary contraindication/who should avoid]

### 📋 How to Take
* [Single-sentence standard adult dosage & timing rule]
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
    if not client:
        raise HTTPException(
            status_code=500, 
            detail="GEMINI_API_KEY environment variable is missing on Render."
        )

    try:
        file_bytes = await file.read()

        image_part = types.Part.from_bytes(
            data=file_bytes,
            mime_type=file.content_type or "image/jpeg"
        )

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
            detail=f"Analysis Error: {str(e)}"
        )