from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import shutil, os, tempfile, logging
from services.pan_service import extract_and_verify  # Returns OCR text

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI()

def normalize(text: str) -> str:
    return (text or "").strip().upper()



@app.post("/upload")
async def upload_pan(
    identity_proof_front_image: UploadFile = File(...),
    first_name: str = Form(None),
    dob: str = Form(None),
    gender: str = Form(None),
):
    temp_path = None
    try:
        logger.info(f"Received upload request: file={identity_proof_front_image.filename}, first_name={first_name}, dob={dob}, gender={gender}")

        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(identity_proof_front_image.filename)[1]) as tmp:
            shutil.copyfileobj(identity_proof_front_image.file, tmp)
            temp_path = tmp.name
        logger.info(f"Saved temporary file at {temp_path}")

        # Call pan_service
        result = extract_and_verify(temp_path, expected_name=first_name, expected_dob=dob)

    except Exception as e:
        logger.error(f"OCR extraction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"OCR extraction failed: {str(e)}")

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
            logger.info(f"Temporary file removed: {temp_path}")

    return result
