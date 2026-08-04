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

# Updated Prompt: Strict everyday language for conditions treated
SYSTEM_PROMPT = """
You are HealthyEye. Analyze the medicine image and output strictly the following 4 sections.
Do NOT use any emojis anywhere in your output.
Highlight key terms using bold text (**keyword**).

CRITICAL LANGUAGE RULE FOR SECTION 2:
Do NOT use complex biological or medical jargon (e.g., avoid "antipyretic", "rhinitis", "analgesic", "upper respiratory tract infection"). 
Use simple, direct everyday words that anyone can understand immediately (e.g., **fever**, **cough**, **cold**, **sneezing**, **runny nose**, **headache**, **body pain**, **stomach ache**).

### 1. Overview
* **Medicine Name:** [Brand name]
* **Active Ingredient:** [Chemical name and strength]
* **Category:** [Simple functional category, e.g., Pain reliever, Antibiotic]

### 2. Used for in simple terms
* List 2-4 direct everyday symptoms or uses:
  * Treats **[symptom/condition in simple terms, e.g., cold]**
  * Relieves **[symptom/condition in simple terms, e.g., sneezing and runny nose]**

### 3. Side effects
* **Common Side Effects:** 2-3 common mild effects using simple language (e.g., **drowsiness**, **dry mouth**, **upset stomach**).
* **Caution:** Primary safety warning (e.g., do not take with **alcohol** or if **pregnant**).

### 4. Global rating
* **Overall Rating:** [Rating out of 5, e.g., **4.5 / 5**]
* **Global Acceptance:** [1 short sentence on approval status by agencies like **FDA**, **EMA**, or **WHO**]
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