from fastapi import FastAPI, UploadFile, File, Form
import shutil, os
from services.pan_service import extract_pan_details

app = FastAPI()

@app.post("/upload")
async def upload_pan(
    file: UploadFile = File(...),
    name: str = Form(...),
    father: str = Form(...),
    dob: str = Form(...)
):
    # Save uploaded file temporarily
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract data from image
    extracted = extract_pan_details(temp_path)

    # Remove temp file
    os.remove(temp_path)

    # Verification
    verification = {
    "Name": (extracted.get("Name") or "").upper() == name.upper(),
    "Father Name": (extracted.get("Father Name") or "").upper() == father.upper(),
    "Date of Birth": (extracted.get("Date of Birth") or "").upper() == dob.upper()
}

    return {
        "Extracted Data": extracted,
        "Verification Result": verification
    }
