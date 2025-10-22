from fastapi import APIRouter, FastAPI, UploadFile, File, Form, HTTPException
import logging
from services.pan_service import extract_pan_details

# Setup
router = APIRouter()
logger = logging.getLogger(__name__)
app = FastAPI(title="PAN OCR API")

@app.post("/upload")
async def parse_pan(
    name: str = Form(...),
    dob: str = Form(...),
    gender: str = Form(...),
    identity_proof_front_image: UploadFile = File(...)
):
    """
    Extract PAN details (Name, DOB, PAN) and validate them against user input.
    Gender is always considered verified (True).
    """
    logger.info("[INFO] Received PAN OCR request")
    logger.info(f"       → Name: {name}")
    logger.info(f"       → DOB: {dob}")
    logger.info(f"       → Gender: {gender}")
    logger.info(f"       → File: {identity_proof_front_image.filename}")

    try:
        # Read uploaded image
        pan_bytes = await identity_proof_front_image.read()
        logger.info(f"[INFO] Image size → {len(pan_bytes)} bytes")

        # Perform OCR extraction
        extracted = extract_pan_details(pan_bytes)
        logger.info("[INFO] PAN OCR processing completed successfully.")
        logger.debug(f"[DEBUG] Extracted Data: {extracted}")

    except Exception as e:
        logger.error(f"[ERROR] PAN OCR extraction failed: {e}")
        raise HTTPException(status_code=500, detail=f"OCR extraction failed: {str(e)}")

    # Helper function for normalization
    def normalize(s: str) -> str:
        return (s or "").strip().upper().replace(" ", "")

    # Verification logic
    verification = {
        "Name_Match": normalize(extracted.get("Name")) == normalize(name),
        "DOB_Match": normalize(extracted.get("Date of Birth")) == normalize(dob),
        "Gender_Match": True   # ✅ Always true as per your requirement
    }

    all_matched = all(verification.values())

    return {
        "status": True,
        "data": {
            "Extracted Data": extracted,
            "Verification": verification,
            "All_Matched": all_matched
        }
    }























# from fastapi import FastAPI, UploadFile, File, Form, HTTPException
# import shutil, os, tempfile, logging
# from services.pan_service import extract_pan_details

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# app = FastAPI()

# @app.post("/upload")
# async def upload_pan(
#     file: UploadFile = File(...),
#     name: str = Form(...),
#     # father: str = Form(...),
#     dob: str = Form(...)
# ):
#     try:
#         # Save uploaded file to a secure temp path
#         with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
#             shutil.copyfileobj(file.file, tmp)
#             temp_path = tmp.name

#         logger.info(f"Saved uploaded file to {temp_path}")

#         # Extract PAN details
#         extracted = extract_pan_details(temp_path) or {}
#         logger.info(f"Extracted Data: {extracted}")

#     except Exception as e:
#         logger.error(f"OCR extraction failed: {e}")
#         raise HTTPException(status_code=500, detail=f"OCR extraction failed: {str(e)}")

#     finally:
#         # Ensure temp file is removhttp://localhost:8085/api/ws-logs?req_id=92735b39-8a9b-4dfa-8d77-2c9fd0b76460ed
#         if os.path.exists(temp_path):
#             os.remove(temp_path)

#     # Verification with normalization
#     def normalize(s: str) -> str:
#         return (s or "").strip().upper()

#     verification = {
#         "Name": normalize(extracted.get("Name")) == normalize(name),
#         # "Father Name": normalize(extracted.get("Father Name")) == normalize(father),
#         "Date of Birth": normalize(extracted.get("Date of Birth")) == normalize(dob),
#     }

#     return {
#         "Extracted Data": extracted,
#         "Verification Result": verification
#     }
