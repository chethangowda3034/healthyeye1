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

# System prompt with strict 4-section requirement, keyword bolding, and NO emojis
SYSTEM_PROMPT = """
You are HealthyEye, a precise clinical AI assistant.
Analyze the provided medicine image and output strictly the following 4 sections.
Do NOT use any emojis anywhere in your output.
Highlight key terms and medical conditions using bold text (**keyword**).

### 1. Overview
* **Medicine Name:** [Brand name]
* **Active Ingredient:** [Chemical composition and strength]
* **Category:** [Pharmacological class]

### 2. Used for in simple terms
* Brief, plain-language bullet points explaining what **medical conditions** or **symptoms** this drug treats. Highlight key words like **fever**, **pain**, **bacterial infection**, etc.

### 3. Side effects
* **Common Side Effects:** List 2-3 standard mild side effects (e.g., **nausea**, **drowsiness**).
* **Precautions:** Primary safety warning or contraindication (e.g., avoid during **pregnancy** or with **alcohol**).

### 4. Global rating
* **Overall Rating:** [Assign a rating out of 5 stars based on global clinical consensus, e.g., **4.5 / 5**]
* **Global Acceptance:** [1 concise sentence on approval standing with global bodies like **FDA**, **EMA**, or **WHO**]
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