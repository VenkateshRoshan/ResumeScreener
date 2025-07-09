from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any

import os

from main import process_resume_and_job

# App intialization
app = FastAPI(
    title = "Resume Match & Advisor API",
    description = "AI powered resume match and advisor API",
    version = "1.0.0"
)


@app.get("/health")
async def health_check(): # TODO: add health check as whehter LLM is accessible or not
    return {
        "status": "ok",
        "message": "API is running"
    } 

@app.post("/analyze")
async def analyze_resume(
    job_description: str = Form(...),
    resume_text: Optional[str] = Form(...),
    resume_file: Optional[UploadFile] = File(None)
):
    """
        Main Analysis Endpoint for Resume and Job Description
    """
    try:

        # Validate inputs
        if not job_description.strip():
            raise HTTPException(status_code=400, detail="Job description is required")
        if not resume_text.strip() and not resume_file:
            raise HTTPException(status_code=400, detail="Resume file or text is required")
        
        result = await process_resume_and_job(
            job_description = job_description,
            resume_text = resume_text,
            resume_file = resume_file
        )

        return {
            "status": "success",
            "message": "Resume analysis completed",
            "data": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)