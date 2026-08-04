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

# Enhanced System Prompt for Deep Analysis and Global Ratings
SYSTEM_PROMPT = """
You are HealthyEye, an advanced clinical AI pharmacy assistant.
Carefully inspect the uploaded medicine image (label, strip, box, or bottle).

Generate a comprehensive, clinical-grade analysis structured strictly with the following detailed sections:

### 💊 1. Identification & Classification
* **Brand Name:** [Exact trade name]
* **Active Ingredient(s) & Strength:** [e.g., Paracetamol 650mg]
* **Pharmacological Class:** [e.g., Analgesic / Antipyretic]
* **Manufacturer / Origin:** [If visible or known]

### 🌍 2. Global Acceptance & Perception
* **Global Trust & Safety Rating:** [Assign a rating out of 5 ⭐ based on worldwide clinical consensus and WHO/FDA approval standing, e.g., 4.8/5 ⭐]
* **Worldwide Regulators Status:** [Mention approval status with major health authorities like US FDA, EMA, UK MHRA, CDSCO]
* **Global Usage Context:** [How widely it is prescribed/used globally]

### 🩺 3. Indications & Therapeutic Uses
* Detailed bullet points specifying exactly what medical conditions this drug is indicated for.

### ⚠️ 4. Clinical Safety Profile & Side Effects
* **Common Side Effects:**
* **Serious Adverse Reactions:**
* **Contraindications:** [Who should NOT take this]

### 📋 5. Administration & Dosage Guidelines
* Standard adult guidance, route of administration, and timing (e.g., post-meal).

Be precise, highly accurate, and objective. Avoid generic high-level summaries.
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

        # Using gemini-2.5-pro for higher accuracy and deeper domain knowledge
        response = client.models.generate_content(
            model="gemini-2.5-pro",
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