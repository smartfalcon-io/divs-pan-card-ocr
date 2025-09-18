import re
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import pytesseract
import logging

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Set tesseract command path
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# -------------------- NORMALIZATION --------------------
def normalize_text(text: str) -> str:
    text = text.upper()  # uppercase
    text = re.sub(r'\s+', ' ', text)  # replace multiple spaces/newlines with single space
    text = re.sub(r'[^A-Z0-9\s:/-]', '', text)  # keep valid chars only
    return text.strip()

def normalize(text: str) -> str:
    if not text:
        return ""
    text = text.strip().upper()
    # Replace common separators with a standard one
    text = text.replace("/", "-")
    return text

# -------------------- IMAGE PREPROCESSING --------------------
def preprocess_image(img_path):
    logger.info(f"Preprocessing image: {img_path}")
    img = Image.open(img_path).convert("L")  # grayscale
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2)  # increase contrast
    img = img.filter(ImageFilter.SHARPEN)  # sharpen
    logger.info("Image preprocessing completed")
    return img




def extract_and_verify(image_path, expected_name=None, expected_dob=None):
    """
    Extract PAN card details from image and verify against given values.
    Returns OCR text, extracted PAN number, DOB, and verification results.
    """

    logger.info(f"Starting PAN OCR extraction for file: {image_path}")

    # Step 1: Read image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Invalid image path or file could not be opened.")

    # Step 2: Preprocessing
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    blur = cv2.medianBlur(thresh, 3)

    # Step 3: OCR
    extracted_text = pytesseract.image_to_string(blur)
    logger.info(f"OCR extraction completed. Raw text:\n{extracted_text}")

    # Step 4: Pattern matching
    pan_pattern = r"[A-Z]{5}[0-9]{4}[A-Z]"
    dob_pattern = r"\d{2}/\d{2}/\d{4}"

    pan_match = re.search(pan_pattern, extracted_text)
    dob_match = re.search(dob_pattern, extracted_text)

    pan_number = pan_match.group(0) if pan_match else None
    dob_extracted = dob_match.group(0) if dob_match else None

    # Step 5: Verification logic
    verification = {}
    contains = True
    message = "PAN verification successful."

    if expected_name:
        name_check = normalize(expected_name) in normalize(extracted_text)
        verification["Name"] = name_check
        if not name_check:
            contains = False
            message = f"Name '{expected_name}' not found."

    if expected_dob:
        dob_check = normalize(expected_dob) in normalize(extracted_text)
        verification["Date of Birth"] = dob_check
        if not dob_check:
            contains = False
            message = f"DOB '{expected_dob}' not found."

    verification["PAN Number Found"] = bool(pan_number)
    if not pan_number:
        contains = False
        message = "PAN number not detected."

    # Step 6: Return full structured response
    return {
        "status": contains,
        "message": message,
        "data": {
            "contains": contains,
            "ocr_text": extracted_text,
            "pan_number": pan_number,
            "dob_extracted": dob_extracted,
            "verification": verification
        }
    }
