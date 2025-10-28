# import cv2
# import numpy as np
# import pytesseract
# import re
# from PIL import Image
# from io import BytesIO

# # -------------------- TEXT CLEANING --------------------
# def clean_text(text):
#     text = text.upper()
#     text = re.sub(r'[^A-Z0-9\s:/-]', '', text)  # Keep valid chars only
#     return text.strip()

# # -------------------- ADVANCED IMAGE PREPROCESSING --------------------
# def preprocess_image(file_bytes):
#     # Convert bytes to NumPy array
#     nparr = np.frombuffer(file_bytes, np.uint8)
#     img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

#     # Resize
#     img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_LINEAR)

#     # Grayscale
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#     # Remove shadows / background
#     background = cv2.medianBlur(gray, 25)
#     diff = 255 - cv2.absdiff(gray, background)
#     norm = cv2.normalize(diff, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

#     # Denoise
#     denoised = cv2.fastNlMeansDenoising(norm, None, h=30)

#     # Binarize
#     thresh = cv2.adaptiveThreshold(
#         denoised, 255,
#         cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
#         cv2.THRESH_BINARY,
#         31, 2
#     )

#     # Morphological closing
#     kernel = np.ones((1, 1), np.uint8)
#     cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

#     # Invert
#     inverted = cv2.bitwise_not(cleaned)

#     # Convert to PIL image for pytesseract
#     pil_img = Image.fromarray(inverted)
#     return pil_img


# # -------------------- NORMALIZE DOB LINE --------------------
# def normalize_date_line(line):
#     line = line.replace("I", "/").replace("|", "/").replace(".", "/")
#     line = re.sub(r"\s+", "", line)
#     return line

# # -------------------- PAN EXTRACTION --------------------
# def extract_pan_details(file_path: str):
#     img = preprocess_image(file_path)
#     text = pytesseract.image_to_string(img, lang="eng")

#     lines = [clean_text(line) for line in text.split("\n") if line.strip()]
#     pan, dob, name = None, None, None

#     # --- PAN regex ---
#     pan_pattern = re.compile(r"[A-Z]{5}[0-9]{4}[A-Z]{1}")
#     for line in lines:
#         candidate = line.replace(" ", "")
#         match = pan_pattern.search(candidate)
#         if match:
#             pan = match.group()
#             break

#     # --- DOB regex ---
#     dob_pattern = re.compile(r"(\d{2}[-/\\\s]?\d{2}[-/\\\s]?\d{4})")

#     for idx, line in enumerate(lines):
#         if "DOB" in line or "DATE OF BIRTH" in line:
#             possible_line = lines[idx + 1] if idx + 1 < len(lines) else line
#             normalized_line = normalize_date_line(possible_line)
#             match = dob_pattern.search(normalized_line)
#             if match:
#                 date_str = match.group()
#                 date_str = re.sub(r"[-\\./\s]", "/", date_str)
#                 parts = re.split(r"/", date_str)
#                 if len(parts) == 3:
#                     day, month, year = parts
#                     day = day.zfill(2)
#                     month = month.zfill(2)
#                     dob = f"{day}/{month}/{year}"
#                 else:
#                     dob = date_str
#                 break

#     if not dob:
#         for line in lines:
#             normalized_line = normalize_date_line(line)
#             match = dob_pattern.search(normalized_line)
#             if match:
#                 date_str = match.group()
#                 date_str = re.sub(r"[-\\./\s]", "/", date_str)
#                 parts = re.split(r"/", date_str)
#                 if len(parts) == 3:
#                     day, month, year = parts
#                     day = day.zfill(2)
#                     month = month.zfill(2)
#                     dob = f"{day}/{month}/{year}"
#                 else:
#                     dob = date_str
#                 break

#     # --- Name extraction ---
#     for idx, line in enumerate(lines):
#         if "NAME" in line and "FATHER" not in line:
#             if idx + 1 < len(lines):
#                 name = lines[idx + 1].title()
#                 break
#         if dob and idx + 1 < len(lines) and dob in line:
#             possible_name = lines[idx - 1].title() if idx > 0 else None
#             if possible_name and len(possible_name.split()) >= 2:
#                 name = possible_name
#                 break

#     return {
#         "Name": name,
#         "Date of Birth": dob,
#         "PAN": pan,
#         "Raw OCR Lines": lines
#     }




















# # import re
# # from PIL import Image, ImageEnhance, ImageFilter
# # import pytesseract

# # # -------------------- TEXT CLEANING --------------------
# # def clean_text(text):
# #     text = text.upper()
# #     text = re.sub(r'[^A-Z0-9\s:/-]', '', text)  # Keep valid chars only
# #     return text.strip()

# # # -------------------- IMAGE PREPROCESSING --------------------
# # def preprocess_image(img_path):
# #     img = Image.open(img_path).convert("L")  # Grayscale
# #     enhancer = ImageEnhance.Contrast(img)
# #     img = enhancer.enhance(2)  # Increase contrast
# #     img = img.filter(ImageFilter.SHARPEN)  # Sharpen image
# #     return img

# # # -------------------- NORMALIZE DOB LINE --------------------
# # def normalize_date_line(line):
# #     # Replace common OCR misreads
# #     line = line.replace("I", "/").replace("|", "/").replace(".", "/")
# #     line = re.sub(r"\s+", "", line)  # remove all spaces
# #     return line

# # # -------------------- PAN EXTRACTION --------------------
# # def extract_pan_details(file_path: str):
# #     img = preprocess_image(file_path)
# #     text = pytesseract.image_to_string(img, lang="eng")

# #     lines = [clean_text(line) for line in text.split("\n") if line.strip()]
# #     pan, dob, name = None, None, None

# #     # --- PAN regex ---
# #     pan_pattern = re.compile(r"[A-Z]{5}[0-9]{4}[A-Z]{1}")
# #     for line in lines:
# #         candidate = line.replace(" ", "")
# #         match = pan_pattern.search(candidate)
# #         if match:
# #             pan = match.group()
# #             break

# #     # --- DOB regex ---
# #     dob_pattern = re.compile(r"(\d{2}[-/\\\s]?\d{2}[-/\\\s]?\d{4})")

# #     # First, try to find line containing DOB keyword
# #     for idx, line in enumerate(lines):
# #         if "DOB" in line or "DATE OF BIRTH" in line:
# #             possible_line = lines[idx + 1] if idx + 1 < len(lines) else line
# #             normalized_line = normalize_date_line(possible_line)
# #             match = dob_pattern.search(normalized_line)
# #             if match:
# #                 date_str = match.group()
# #                 # Convert to dd/mm/yyyy format
# #                 date_str = re.sub(r"[-\\./\s]", "/", date_str)
# #                 parts = re.split(r"/", date_str)
# #                 if len(parts) == 3:
# #                     day, month, year = parts
# #                     # Zero-pad day and month if needed
# #                     day = day.zfill(2)
# #                     month = month.zfill(2)
# #                     dob = f"{day}/{month}/{year}"
# #                 else:
# #                     dob = date_str  # fallback
# #                 break

# #     # Fallback: scan all lines if not found
# #     if not dob:
# #         for line in lines:
# #             normalized_line = normalize_date_line(line)
# #             match = dob_pattern.search(normalized_line)
# #             if match:
# #                 date_str = match.group()
# #                 date_str = re.sub(r"[-\\./\s]", "/", date_str)
# #                 parts = re.split(r"/", date_str)
# #                 if len(parts) == 3:
# #                     day, month, year = parts
# #                     day = day.zfill(2)
# #                     month = month.zfill(2)
# #                     dob = f"{day}/{month}/{year}"
# #                 else:
# #                     dob = date_str
# #                 break
                
# #     # --- Name extraction (handle diff formats) ---
# #     for idx, line in enumerate(lines):
# #         # If line has "NAME" but not "FATHER" → take next line
# #         if "NAME" in line and "FATHER" not in line:
# #             if idx + 1 < len(lines):
# #                 name = lines[idx + 1].title()
# #                 break
# #         # Fallback: Sometimes Name is just above DOB
# #         if dob and idx + 1 < len(lines) and dob in line:
# #             possible_name = lines[idx - 1].title() if idx > 0 else None
# #             if possible_name and len(possible_name.split()) >= 2:
# #                 name = possible_name
# #                 break

# #     return {
# #         "Name": name,
# #         "Date of Birth": dob,
# #         "PAN": pan,
# #         "Raw OCR Lines": lines
# #     }



# # pan_service.py
# import cv2
# import numpy as np
# import pytesseract
# import re
# from PIL import Image
# from io import BytesIO

# # -------------------- TEXT CLEANING --------------------
# def clean_text(text: str) -> str:
#     text = text.upper()
#     text = re.sub(r'[^A-Z0-9\s:/-]', '', text)
#     return text.strip()

# # -------------------- IMAGE PREPROCESSING --------------------
# def preprocess_image(file_bytes: bytes, min_width: int = 1000) -> Image.Image:
#     """
#     Preprocess PAN image for OCR with automatic resizing and thresholding.
#     """
#     # Convert bytes to OpenCV image
#     nparr = np.frombuffer(file_bytes, np.uint8)
#     img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

#     # Resize if too small
#     height, width = img.shape[:2]
#     if width < min_width:
#         scale = min_width / width
#         img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)

#     # Grayscale
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#     # Remove noise & improve contrast
#     gray = cv2.GaussianBlur(gray, (3, 3), 0)

#     # Sharpen
#     kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
#     gray = cv2.filter2D(gray, -1, kernel)

#     # Threshold
#     _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

#     return Image.fromarray(thresh)

# # -------------------- NORMALIZE DOB --------------------
# def normalize_date_line(line: str) -> str:
#     line = line.replace("I", "/").replace("|", "/").replace(".", "/")
#     line = re.sub(r"\s+", "", line)
#     return line

# # -------------------- NAME EXTRACTION --------------------
# def extract_name(lines, dob=None):
#     """
#     Robust extraction of probable Name from OCR lines.
#     """
#     keywords_to_ignore = ['DOB', 'DATE OF BIRTH', 'FATHER', 'SIGNATURE', 'INCOMETAX', 'PERMANENT', 'ACCOUNT', 'NUMBER', 'CARD', 'PAN']
#     name = None

#     # 1️⃣ Look for line before DOB
#     if dob:
#         for i, line in enumerate(lines):
#             if dob.replace('/', '') in line.replace('/', ''):
#                 if i > 0:
#                     candidate = lines[i-1].title()
#                     if 2 <= len(candidate.split()) <= 4:
#                         return candidate

#     # 2️⃣ Look after "PERMANENT ACCOUNT NUMBER CARD"
#     for i, line in enumerate(lines):
#         combined_line = line.replace(' ', '').upper()
#         if 'PERMANENTACCOUNTNUMBERCARD' in combined_line:
#             # Take next lines as candidate
#             for j in range(i+1, min(i+4, len(lines))):
#                 candidate = lines[j].title()
#                 if all(kw not in candidate.upper() for kw in keywords_to_ignore) and 2 <= len(candidate.split()) <= 4:
#                     return candidate

#     # 3️⃣ Fallback: longest line ignoring keywords
#     candidates = [line.title() for line in lines if all(kw not in line.upper() for kw in keywords_to_ignore)]
#     if candidates:
#         name = max(candidates, key=lambda x: len(x))
#     return name

# # -------------------- PAN DETAILS EXTRACTION --------------------
# def extract_pan_details(file_bytes: bytes) -> dict:
#     """
#     Extract PAN, Name, DOB from PAN image bytes.
#     """
#     img = preprocess_image(file_bytes)

#     # OCR using Tesseract
#     custom_config = r'--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/'
#     raw_text = pytesseract.image_to_string(img, lang='eng', config=custom_config)

#     lines = [clean_text(line) for line in raw_text.split("\n") if line.strip()]

#     pan, dob, name = None, None, None

#     # --- PAN extraction ---
#     pan_pattern = re.compile(r"[A-Z]{5}[0-9]{4}[A-Z]{1}")
#     for line in lines:
#         candidate = line.replace(" ", "")
#         match = pan_pattern.search(candidate)
#         if match:
#             pan = match.group()
#             break

#     # --- DOB extraction ---
#     dob_pattern = re.compile(r"\d{2}/\d{2}/\d{4}")
#     for idx, line in enumerate(lines):
#         normalized_line = normalize_date_line(line)
#         match = dob_pattern.search(normalized_line)
#         if match:
#             dob = match.group()
#             break

#     # --- Name extraction ---
#     name = extract_name(lines, dob)

#     return {
#         "Name": name,
#         "Date of Birth": dob,
#         "PAN": pan,
#         "Raw OCR Lines": lines
#     }




import cv2
import numpy as np
import pytesseract
import re
import logging
from PIL import Image
from typing import Dict, Optional

# -------------------- Logging Setup --------------------
logger = logging.getLogger(__name__)

# -------------------- CLEAN TEXT --------------------
def clean_text(text: str) -> str:
    text = text.upper()
    text = re.sub(r"[^A-Z0-9\s:/-]", "", text)
    text = re.sub(r"\s+", " ", text)
    cleaned = text.strip()
    logger.debug(f"🧹 Cleaned text: '{text}' → '{cleaned}'")
    return cleaned

# -------------------- CLEAN NAME CANDIDATE --------------------
def clean_name_candidate(text: str) -> str:
    text = text.upper()
    text = re.sub(r"[^A-Z\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    cleaned = text.strip()
    logger.debug(f"👤 Cleaned name candidate: '{text}' → '{cleaned}'")
    return cleaned

# -------------------- ROTATION CORRECTION --------------------
def detect_and_correct_rotation(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    try:
        osd = pytesseract.image_to_osd(gray)
        rotation = int(re.search(r"Rotate: (\d+)", osd).group(1))
        logger.info(f"🧭 Detected image rotation: {rotation}°")

        if rotation == 90:
            img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
            logger.info("🔄 Rotated image 90° counterclockwise")
        elif rotation == 180:
            img = cv2.rotate(img, cv2.ROTATE_180)
            logger.info("🔄 Rotated image 180°")
        elif rotation == 270:
            img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
            logger.info("🔄 Rotated image 90° clockwise")
        else:
            logger.info("✅ No rotation needed")
    except Exception as e:
        logger.warning(f"⚠️ Rotation detection failed: {e}")
    return img

# -------------------- IMAGE PREPROCESSING --------------------
def preprocess_image(file_bytes: bytes):
    logger.info("🖼️ Starting image preprocessing...")
    nparr = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        logger.error("❌ Invalid image file")
        raise ValueError("Invalid image file")

    logger.info(f"✅ Image decoded successfully (shape={img.shape})")

    img = detect_and_correct_rotation(img)
    img = cv2.resize(img, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_LINEAR)
    logger.info("🔍 Image resized and enhanced")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    logger.info("🎨 Converted image to grayscale")

    denoised = cv2.fastNlMeansDenoising(gray, None, 30, 7, 21)
    logger.info("🧼 Applied denoising filter")

    thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 31, 2
    )
    logger.info("⚙️ Applied adaptive thresholding")

    inverted = cv2.bitwise_not(thresh)
    logger.info("🔁 Inverted image colors for OCR")

    logger.info("✅ Image preprocessing completed successfully")
    return Image.fromarray(inverted)

# -------------------- NORMALIZE DATE --------------------
def normalize_date_line(line: str):
    normalized = line.replace("I", "/").replace("|", "/").replace(".", "/")
    normalized = re.sub(r"\s+", "", normalized)
    logger.debug(f"📅 Normalized date line: '{line}' → '{normalized}'")
    return normalized

# -------------------- MAIN EXTRACTION --------------------
def extract_pan_details(file_bytes: bytes) -> Dict[str, Optional[str]]:
    logger.info("🚀 Starting PAN details extraction...")
    pil_img = preprocess_image(file_bytes)

    ocr_configs = ["--psm 6", "--psm 4", "--psm 3", "--psm 11"]
    all_lines = []

    # OCR multiple times with different configurations
    for config in ocr_configs:
        logger.info(f"🔎 Running Tesseract OCR with config: {config}")
        try:
            text = pytesseract.image_to_string(pil_img, lang="eng", config=config)
            lines = [clean_text(line) for line in text.split("\n") if line.strip()]
            logger.info(f"✅ Extracted {len(lines)} lines with config {config}")
            all_lines.extend(lines)
        except Exception as e:
            logger.warning(f"⚠️ OCR failed for config {config}: {e}")

    lines = list(dict.fromkeys(all_lines))  # remove duplicates
    logger.info(f"🧾 Total unique OCR lines: {len(lines)}")
    logger.debug(f"📜 OCR Lines: {lines}")

    name, dob, pan = None, None, None

    # --- PAN NUMBER EXTRACTION ---
    logger.info("🆔 Searching for PAN number pattern...")
    pan_pattern = re.compile(r"[A-Z]{5}[0-9]{4}[A-Z]")
    for line in lines:
        match = pan_pattern.search(line.replace(" ", ""))
        if match:
            pan = match.group()
            logger.info(f"✅ PAN detected: {pan}")
            break
    if not pan:
        logger.warning("⚠️ PAN number not found in OCR text")

    # --- DOB EXTRACTION ---
    logger.info("📅 Searching for Date of Birth...")
    dob_pattern = re.compile(r"(\d{2}[-/\.\s]?\d{2}[-/\.\s]?\d{4})")
    for i, line in enumerate(lines):
        if "DOB" in line or "DATE OF BIRTH" in line:
            next_line = lines[i + 1] if i + 1 < len(lines) else line
            match = dob_pattern.search(normalize_date_line(next_line))
            if match:
                parts = re.split(r"[-/\.]", match.group())
                if len(parts) == 3:
                    day, month, year = parts
                    dob = f"{day.zfill(2)}/{month.zfill(2)}/{year}"
                else:
                    dob = match.group()
                logger.info(f"✅ DOB found: {dob}")
                break

    if not dob:
        logger.info("🔁 Secondary search for DOB in other lines...")
        for line in lines:
            match = dob_pattern.search(line)
            if match:
                parts = re.split(r"[-/\.]", match.group())
                if len(parts) == 3:
                    day, month, year = parts
                    dob = f"{day.zfill(2)}/{month.zfill(2)}/{year}"
                else:
                    dob = match.group()
                logger.info(f"✅ DOB found (fallback): {dob}")
                break
    if not dob:
        logger.warning("⚠️ DOB not found in OCR text")

    # --- NAME EXTRACTION ---
    logger.info("👤 Searching for Name patterns...")
    possible_names = []

    for idx, line in enumerate(lines):
        # After "NAME"
        if "NAME" in line and "FATHER" not in line:
            for j in range(1, 3):
                if idx + j < len(lines):
                    candidate = clean_name_candidate(lines[idx + j])
                    if 2 <= len(candidate.split()) <= 4 and len(candidate) > 5:
                        possible_names.append(candidate)
                        logger.info(f"✅ Name candidate (after NAME): {candidate}")

        # Before "FATHER"
        elif "FATHER" in line and idx > 0:
            prev_line = clean_name_candidate(lines[idx - 1])
            if 2 <= len(prev_line.split()) <= 4 and len(prev_line) > 5:
                possible_names.append(prev_line)
                logger.info(f"✅ Name candidate (before FATHER): {prev_line}")

    # Near DOB line (fallback)
    if not possible_names and dob:
        logger.info("🔁 Fallback: searching near DOB line...")
        for i, line in enumerate(lines):
            if dob in line and i >= 2:
                prev_line = clean_name_candidate(lines[i - 2])
                if 2 <= len(prev_line.split()) <= 4 and len(prev_line) > 5:
                    possible_names.append(prev_line)
                    logger.info(f"✅ Fallback name candidate near DOB: {prev_line}")
                    break

    # Pick best name
    if possible_names:
        best_candidate = max(possible_names, key=len)
        name_words = best_candidate.split()
        if len(name_words) > 4:
            best_candidate = " ".join(name_words[:4])
        name = best_candidate.title()
        logger.info(f"🏷️ Final chosen name: {name}")
    else:
        logger.warning("⚠️ No valid name candidates found")

    result = {
        "Name": name if name else "Name not found",
        "Date of Birth": dob if dob else "DOB not found",
        "PAN": pan if pan else "PAN not found",
        "Raw OCR Lines": lines
    }

    logger.info(f"📦 Extraction result: {result}")
    logger.info("✅ PAN details extraction completed successfully")
    return result
