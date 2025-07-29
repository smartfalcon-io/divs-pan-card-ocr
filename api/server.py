from fastapi import FastAPI, UploadFile, File
import shutil, os
from services.pan_service import extract_pan_details

app = FastAPI()

@app.post("/upload")
async def upload_pan(file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = extract_pan_details(temp_path)

    os.remove(temp_path)
    return result
