# from fastapi import APIRouter, FastAPI, UploadFile, File, Form, HTTPException
# import logging
# from services.pan_service import extract_pan_details
# from io import BytesIO

# # Setup
# router = APIRouter()
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s  [%(levelname)s] %(message)s"
# )
# logger = logging.getLogger(__name__)
# app = FastAPI(title="PAN OCR API")

# # @app.post("/upload")
# # async def parse_pan(
# #     name: str = Form(...),
# #     dob: str = Form(...),
# #     gender: str = Form(...),
# #     identity_proof_front_image: UploadFile = File(...)
# # ):
# #     """
# #     Extract PAN details (Name, DOB, PAN) and validate them against user input.
# #     Gender is always considered verified (True).
# #     """
# #     logger.info("[INFO] Received PAN OCR request")
# #     logger.info(f"       → Name: {name}")
# #     logger.info(f"       → DOB: {dob}")
# #     logger.info(f"       → Gender: {gender}")
# #     logger.info(f"       → File: {identity_proof_front_image.filename}")

# #     try:
# #         # Read uploaded image
# #         pan_bytes = await identity_proof_front_image.read()
# #         logger.info(f"[INFO] Image size → {len(pan_bytes)} bytes")

# #         # Perform OCR extraction
# #         pan_img = BytesIO(pan_bytes)
# #         extracted = extract_pan_details(pan_img)
# #         logger.info("[INFO] PAN OCR processing completed successfully.")
# #         logger.debug(f"[DEBUG] Extracted Data: {extracted}")

# #     except Exception as e:
# #         logger.error(f"[ERROR] PAN OCR extraction failed: {e}")
# #         raise HTTPException(status_code=500, detail=f"OCR extraction failed: {str(e)}")

# #     # Helper function for normalization
# #     def normalize(s: str) -> str:
# #         return (s or "").strip().upper().replace(" ", "")

# #     # Verification logic
# #     verification = {
# #         "Name_Match": normalize(extracted.get("Name")) == normalize(name),
# #         "DOB_Match": normalize(extracted.get("Date of Birth")) == normalize(dob),
# #         "Gender_Match": True   # ✅ Always true as per your requirement
# #     }

# #     all_matched = all(verification.values())

# #     return {
# #         "status": True,
# #         "data": {
# #             "Extracted Data": extracted,
# #             "Verification": verification,
# #             "All_Matched": all_matched
# #         }
# #     }


# @app.post("/upload")
# async def parse_pan(identity_proof_front_image: UploadFile = File(...)):
#     """
#     Extract PAN details (Name, DOB, PAN) from the uploaded image.
#     """
#     logger.info(f"[INFO] Received PAN OCR request → File: {identity_proof_front_image.filename}")

#     try:
#         # Read uploaded image
#         pan_bytes = await identity_proof_front_image.read()
#         logger.info(f"[INFO] Image size → {len(pan_bytes)} bytes")

#         # Perform OCR extraction
#         pan_img = BytesIO(pan_bytes)
#         extracted = extract_pan_details(pan_bytes)
#         logger.info("[INFO] PAN OCR processing completed successfully.")
#         logger.debug(f"[DEBUG] Extracted Data: {extracted}")

#     except Exception as e:
#         logger.error(f"[ERROR] PAN OCR extraction failed: {e}")
#         raise HTTPException(status_code=500, detail=f"OCR extraction failed: {str(e)}")

#     return {
#         "status": True,
#         "data": extracted
#     }


















from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from io import BytesIO
from difflib import SequenceMatcher
import logging
from services.pan_service import extract_pan_details

app = FastAPI(title="PAN OCR Verification API")

# ------------------ Logging ------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ------------------ Helpers ------------------
def normalize(text: str) -> str:
    """Normalize string for consistent comparison."""
    return (text or "").strip().upper().replace(" ", "").replace("-", "").replace("/", "")

def similarity(a: str, b: str) -> float:
    """Return similarity ratio between two strings (0-1)."""
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()

def field_match(extracted: str, entered: str, threshold: float = 0.85) -> dict:
    """Return match result with similarity percentage."""
    score = similarity(extracted, entered)
    return {
        "Entered": entered,
        "Extracted": extracted,
        "Similarity (%)": round(score * 100, 2),
        "Match": score >= threshold
    }

# ------------------ API ------------------
@app.post("/upload")
async def upload_pan_card(
    name: str = Form(...),
    dob: str = Form(...),
    gender: str = Form(...),
    identity_proof_front_image: UploadFile = File(...)
):
    """
    Upload a PAN image + details to verify OCR extracted data.
    """
    logger.info(f"Received PAN OCR request: {identity_proof_front_image.filename}")

    try:
        # Read image bytes
        image_bytes = await identity_proof_front_image.read()
        pan_img = BytesIO(image_bytes)

        # Extract details from image
        extracted_data = extract_pan_details(image_bytes)
        logger.info(f"OCR Extraction Completed: {extracted_data}")

    except Exception as e:
        logger.error(f"OCR Extraction Failed: {e}")
        raise HTTPException(status_code=500, detail=f"OCR extraction failed: {str(e)}")

    # ------------------ Matching ------------------
    results = {
        "Name": field_match(extracted_data.get("Name", ""), name),
        "Date of Birth": field_match(extracted_data.get("Date of Birth", ""), dob),
        "Gender": {
            "Entered": gender,
            "Extracted": gender,   # Always true as gender is not in PAN
            "Similarity (%)": 100,
            "Match": True
        }
    }

    all_matched = all([v["Match"] for v in results.values()])

    message = (
        "✅ All fields match successfully." if all_matched
        else "❌ One or more fields did not match."
    )

    # ------------------ Response ------------------
    return {
        "status": True,
        "message": message,
        "Entered Data": {
            "Name": name,
            "Date of Birth": dob,
            "Gender": gender
        },
        "Extracted Data": extracted_data,
        "Match Results": results,
        "All_Matched": all_matched
    }
