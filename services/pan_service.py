import re
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract

# -------------------- TEXT CLEANING --------------------
def clean_text(text):
    text = text.upper()
    text = re.sub(r'[^A-Z0-9\s:/-]', '', text)  # Keep valid chars only
    return text.strip()

# -------------------- IMAGE PREPROCESSING --------------------
def preprocess_image(img_path):
    img = Image.open(img_path).convert("L")  # Grayscale
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2)  # Increase contrast
    img = img.filter(ImageFilter.SHARPEN)  # Sharpen image
    return img

# -------------------- NORMALIZE DOB LINE --------------------
def normalize_date_line(line):
    # Replace common OCR misreads
    line = line.replace("I", "/").replace("|", "/").replace(".", "/")
    line = re.sub(r"\s+", "", line)  # remove all spaces
    return line

# -------------------- PAN EXTRACTION --------------------
def extract_pan_details(file_path: str):
    img = preprocess_image(file_path)
    text = pytesseract.image_to_string(img, lang="eng")

    lines = [clean_text(line) for line in text.split("\n") if line.strip()]
    pan, dob, name = None, None, None

    # --- PAN regex ---
    pan_pattern = re.compile(r"[A-Z]{5}[0-9]{4}[A-Z]{1}")
    for line in lines:
        candidate = line.replace(" ", "")
        match = pan_pattern.search(candidate)
        if match:
            pan = match.group()
            break

    # --- DOB regex ---
    dob_pattern = re.compile(r"(\d{2}[-/\\\s]?\d{2}[-/\\\s]?\d{4})")

    # First, try to find line containing DOB keyword
    for idx, line in enumerate(lines):
        if "DOB" in line or "DATE OF BIRTH" in line:
            possible_line = lines[idx + 1] if idx + 1 < len(lines) else line
            normalized_line = normalize_date_line(possible_line)
            match = dob_pattern.search(normalized_line)
            if match:
                date_str = match.group()
                # Convert to dd/mm/yyyy format
                date_str = re.sub(r"[-\\./\s]", "/", date_str)
                parts = re.split(r"/", date_str)
                if len(parts) == 3:
                    day, month, year = parts
                    # Zero-pad day and month if needed
                    day = day.zfill(2)
                    month = month.zfill(2)
                    dob = f"{day}/{month}/{year}"
                else:
                    dob = date_str  # fallback
                break

    # Fallback: scan all lines if not found
    if not dob:
        for line in lines:
            normalized_line = normalize_date_line(line)
            match = dob_pattern.search(normalized_line)
            if match:
                date_str = match.group()
                date_str = re.sub(r"[-\\./\s]", "/", date_str)
                parts = re.split(r"/", date_str)
                if len(parts) == 3:
                    day, month, year = parts
                    day = day.zfill(2)
                    month = month.zfill(2)
                    dob = f"{day}/{month}/{year}"
                else:
                    dob = date_str
                break
                
    # --- Name extraction (handle diff formats) ---
    for idx, line in enumerate(lines):
        # If line has "NAME" but not "FATHER" → take next line
        if "NAME" in line and "FATHER" not in line:
            if idx + 1 < len(lines):
                name = lines[idx + 1].title()
                break
        # Fallback: Sometimes Name is just above DOB
        if dob and idx + 1 < len(lines) and dob in line:
            possible_name = lines[idx - 1].title() if idx > 0 else None
            if possible_name and len(possible_name.split()) >= 2:
                name = possible_name
                break

    return {
        "Name": name,
        "Date of Birth": dob,
        "PAN": pan,
        "Raw OCR Lines": lines
    }