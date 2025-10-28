# # api/server.py

# from fastapi import FastAPI, UploadFile, File, Form, HTTPException
# from io import BytesIO
# from difflib import SequenceMatcher
# import logging
# from services.pan_service import extract_pan_details

# app = FastAPI(title="PAN OCR Verification API")

# # ------------------ Logging ------------------
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s [%(levelname)s] %(message)s"
# )
# logger = logging.getLogger(__name__)

# # ------------------ Helpers ------------------
# def normalize(text: str) -> str:
#     """Normalize string for consistent comparison."""
#     return (text or "").strip().upper().replace(" ", "").replace("-", "").replace("/", "")

# def similarity(a: str, b: str) -> float:
#     """Return similarity ratio between two strings (0-1)."""
#     return SequenceMatcher(None, normalize(a), normalize(b)).ratio()

# def field_match(extracted: str, entered: str, threshold: float = 0.85) -> dict:
#     """Return match result with similarity percentage."""
#     score = similarity(extracted, entered)
#     return {
#         "Entered": entered,
#         "Extracted": extracted,
#         "Similarity (%)": round(score * 100, 2),
#         "Match": score >= threshold
#     }

# # ------------------ API ------------------
# @app.post("/upload")
# async def upload_pan_card(
#                     identity_proof_front_image: UploadFile = File(...),
#                     first_name: str = Form(...),
#                     dob: str = Form(...),
#                     gender: str = Form(None)
# ):
#     """
#     Upload a PAN image + details to verify OCR extracted data.
#     """
#     logger.info(f"Received PAN OCR request: {identity_proof_front_image.filename}")

#     try:
#         # Read image bytes
#         image_bytes = await identity_proof_front_image.read()
#         pan_img = BytesIO(image_bytes)

#         # Extract details from image
#         extracted_data = extract_pan_details(image_bytes)
#         logger.info(f"OCR Extraction Completed: {extracted_data}")

#     except Exception as e:
#         logger.error(f"OCR Extraction Failed: {e}")
#         raise HTTPException(status_code=500, detail=f"OCR extraction failed: {str(e)}")

#     # ------------------ Matching ------------------
#     results = {
#         "First Name": field_match(extracted_data.get("Name", ""), first_name),
#         "Date of Birth": field_match(extracted_data.get("Date of Birth", ""), dob),
#         "Gender": {
#             "Entered": gender,
#             "Extracted": gender,   # Always true as gender is not in PAN
#             "Similarity (%)": 100,
#             "Match": True
#         }
#     }

#     all_matched = all([v["Match"] for v in results.values()])

#     message = (
#         "✅ All fields match successfully." if all_matched
#         else "❌ One or more fields did not match."
#     )

#     # ------------------ Response ------------------
#     return {
#         "status": all_matched,
#         "message": message,
#         "Entered Data": {
#             "First Name": first_name,
#             "Date of Birth": dob,
#             "Gender": gender
#         },
#         "Extracted Data": extracted_data,
#         "Match Results": results,
#         "All_Matched": all_matched
#     }



# server.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from io import BytesIO
from difflib import SequenceMatcher
from PIL import UnidentifiedImageError
import logging
from services.pan_service import extract_pan_details

app = FastAPI(title="PAN OCR Verification API")

# ------------------ Logging Configuration ------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ------------------ Helper Function ------------------
def string_similarity(a: str, b: str) -> float:
    """Return percentage similarity between two strings"""
    if not a or not b:
        logger.warning(f"⚠️ Empty string comparison detected — a='{a}', b='{b}'")
        return 0.0
    similarity = round(SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio() * 100, 2)
    logger.info(f"🔍 String similarity between '{a}' and '{b}' = {similarity}%")
    return similarity

# ------------------ Routes ------------------
@app.post("/upload")
async def upload_pan(
    first_name: str = Form(...),
    dob: str = Form(...),
    gender: str = Form(...),
    identity_proof_front_image: UploadFile = File(...)
):
    """
    PAN OCR Validation API:
    1. Extract PAN, Name, DOB from image using pan_service.py
    2. Compare with provided user details
    3. Return match status & confidence
    """
    logger.info("🚀 New /upload request received")

    try:
        logger.info(f"📥 Form Data - Name: {first_name}, DOB: {dob}, Gender: {gender}")
        logger.info(f"🖼️ Uploaded File Details - filename={identity_proof_front_image.filename}, content_type={identity_proof_front_image.content_type}")

        # Step 1: Read uploaded image
        image_bytes = await identity_proof_front_image.read()
        if not image_bytes:
            logger.error("❌ Empty image file received.")
            raise HTTPException(status_code=400, detail="Empty image file received")

        logger.info(f"✅ Image file read successfully — Size: {len(image_bytes)} bytes")

        # Step 2: Perform OCR extraction
        logger.info("🔎 Running PAN OCR extraction via extract_pan_details()...")
        extracted = extract_pan_details(image_bytes)
        logger.info(f"📤 OCR Extracted Data: {extracted}")

        # Step 3: Parse extracted fields
        extracted_name = extracted.get("Name", "")
        extracted_dob = extracted.get("Date of Birth", "")
        extracted_pan = extracted.get("PAN", "")
        raw_lines = extracted.get("Raw OCR Lines", [])

        logger.info(f"🧾 Extracted Name: {extracted_name}")
        logger.info(f"🧾 Extracted DOB: {extracted_dob}")
        logger.info(f"🧾 Extracted PAN: {extracted_pan}")
        logger.info(f"🧾 Raw OCR Lines: {raw_lines}")

        # Step 4: Compute similarities
        logger.info("📊 Computing field similarities...")
        name_similarity = string_similarity(first_name, extracted_name)
        dob_similarity = string_similarity(dob, extracted_dob)
        gender_match = True  # PAN doesn’t include gender textually

        logger.info(f"✅ Name similarity = {name_similarity}%")
        logger.info(f"✅ DOB similarity = {dob_similarity}%")
        logger.info(f"✅ Gender check (always True for PAN) = {gender_match}")

        # Step 5: Determine matching thresholds
        name_match = name_similarity >= 80
        dob_match = dob_similarity >= 90
        all_matched = name_match and dob_match and gender_match

        logger.info(f"🔐 Match Summary - Name: {name_match}, DOB: {dob_match}, Gender: {gender_match}, All Matched: {all_matched}")

        # Step 6: Build response
        if all_matched:
            message = "✅ All fields match successfully."
        else:
            message = "❌ OCR data mismatch — one or more fields did not match."

        response = {
            "status": True,  # OCR service call succeeded
            "message": message,
            "verified": all_matched,
            "data": {
                "panNumber": extracted_pan,
                "dob": extracted_dob,
                "name": extracted_name,
                "gender": gender,
                "contains": all_matched,
                "similarity": {
                    "name_similarity": f"{name_similarity}%",
                    "dob_similarity": f"{dob_similarity}%"
                },
                "raw_lines": raw_lines
            }
        }

        logger.info(f"📦 Final Response Payload: {response}")
        logger.info("✅ Request completed successfully.")
        return JSONResponse(content=response)

    except UnidentifiedImageError:
        logger.exception("❌ Invalid or corrupted image file.")
        raise HTTPException(status_code=400, detail="Invalid or corrupted image file")
    except Exception as e:
        logger.exception("💥 PAN OCR Processing Failed due to unexpected error.")
        raise HTTPException(status_code=500, detail=str(e))
