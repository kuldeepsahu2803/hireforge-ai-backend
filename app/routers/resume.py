from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import base64
import google.generativeai as genai
import json
import os

router = APIRouter()

class ResumeExtractRequest(BaseModel):
    pdf_base64: str
    user_id: str

@router.post("/extract-resume")
async def extract_resume(req: ResumeExtractRequest):
    try:
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-2.0-flash")

        pdf_bytes = base64.b64decode(req.pdf_base64)

        prompt = """
        Extract the following information from this resume PDF and return 
        ONLY a valid JSON object with these exact keys:
        {
          "fullname": "",
          "email": "",
          "phone": "",
          "location": "",
          "linkedinurl": "",
          "githuburl": "",
          "portfoliourl": "",
          "experiencelevel": "",
          "targetroles": [],
          "summary": ""
        }
        
        Rules:
        - experiencelevel must be one of: fresher, junior, mid, senior
        - targetroles must be an array of strings
        - If a field is not found, use empty string or empty array
        - Return ONLY the JSON, no markdown, no explanation
        """

        response = model.generate_content([
            {"mime_type": "application/pdf", "data": pdf_bytes},
            prompt
        ])

        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()

        extracted = json.loads(text)
        return extracted

    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail="Could not parse resume content")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
