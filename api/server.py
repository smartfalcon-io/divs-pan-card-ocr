from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import shutil, os, tempfile, logging
from services.pan_service import extract_pan_details

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/upload")
async def upload_pan(
    file: UploadFile = File(...),
    name: str = Form(...),
    father: str = Form(...),
    dob: str = Form(...)
):
    try:
        # Save uploaded file to a secure temp path
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_path = tmp.name

        logger.info(f"Saved uploaded file to {temp_path}")

        # Extract PAN details
        extracted = extract_pan_details(temp_path) or {}
        logger.info(f"Extracted Data: {extracted}")

    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        raise HTTPException(status_code=500, detail=f"OCR extraction failed: {str(e)}")

    finally:
        # Ensure temp file is removed
        if os.path.exists(temp_path):
            os.remove(temp_path)

    # Verification with normalization
    def normalize(s: str) -> str:
        return (s or "").strip().upper()

    verification = {
        "Name": normalize(extracted.get("Name")) == normalize(name),
        "Father Name": normalize(extracted.get("Father Name")) == normalize(father),
        "Date of Birth": normalize(extracted.get("Date of Birth")) == normalize(dob),
    }

    return {
        "Extracted Data": extracted,
        "Verification Result": verification
    }
