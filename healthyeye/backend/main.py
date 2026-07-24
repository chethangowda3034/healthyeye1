import os
import json
import io
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from PIL import Image
from google import genai
from google.genai import types

from database import init_db, SessionLocal, Medicine
from seed_data import seed_database  # This is your list of dictionaries
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from Vercel & mobile devices
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 1. Initialize SQLite Database Tables
init_db()

# 2. Seed Database Function
import json

import json
from database import init_db, SessionLocal, Medicine
from seed_data import seed_database

# Initialize SQLite tables
init_db()

def seed_db():
    db = SessionLocal()
    try:
        count = db.query(Medicine).count()
        print(f"--- DB CHECK: Found {count} items ---")
        
        if count == 0:
            print(f"--- SEEDING: Adding {len(seed_database)} items ---")
            for item in seed_database:
                formatted_item = dict(item)
                for key, val in formatted_item.items():
                    if isinstance(val, list):
                        formatted_item[key] = ", ".join(val)
                
                med = Medicine(**formatted_item)
                db.add(med)  # Inside the loop!
            
            db.commit()      # Commit after adding all items!
            print("--- SUCCESS: Seeded database! ---")
    except Exception as e:
        print(f"--- ERROR Seeding DB: {e} ---")
        db.rollback()
    finally:
        db.close()

seed_db()

# 3. Create FastAPI App
app = FastAPI(title="HealthyEye API (Gemini Powered)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/medicines")
def list_medicines(db: Session = Depends(get_db)):
    return db.query(Medicine).all()

@app.post("/analyze-medicine")
async def analyze_medicine(file: UploadFile = File(...)):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500, 
            detail="GEMINI_API_KEY environment variable is not set."
        )

    client = genai.Client(api_key=api_key)

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        system_instruction = """
        You are HealthyEye, a friendly, minimal healthcare assistant for identifying medicine packaging.
        Examine the uploaded image. Read all text on the packaging or bottle.
        
        Return your analysis strictly as a valid JSON object with these exact keys:
        {
            "medicine_name": "Name and dosage of identified medicine",
            "purpose": "One clear sentence explaining what this medicine treats",
            "timing": "Clear instructions in BOLD language e.g. TAKE AFTER FOOD - MORNING AND NIGHT",
            "precautions": "Key things to avoid or be careful about",
            "home_remedy": "A suitable Indian home remedy alternative or complementary relief (e.g. ginger tea, steam inhalation)",
            "disclaimer": "HealthyEye provides information only, not medical advice. Always consult a doctor."
        }
        Return ONLY raw JSON. No conversational filler, extra text, or markdown code blocks.
        """

        prompt = "Identify this medicine image and provide structured usage instructions."

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[image, prompt],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )

        data = json.loads(response.text.strip())
        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")