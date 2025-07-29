import re, os, shutil
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract

def clean_text(text):
    text = text.upper()
    text = re.sub(r'[^A-Z0-9\s:/-]', '', text)  # Keep valid chars only
    return text.strip()

def preprocess_image(img_path):
    img = Image.open(img_path).convert("L")  # Convert to grayscale
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2)
    img = img.filter(ImageFilter.SHARPEN)
    return img

def extract_pan_details(file_path: str):
    img = preprocess_image(file_path)
    text = pytesseract.image_to_string(img, lang="eng")

    lines = [clean_text(line) for line in text.split("\n") if line.strip()]
    pan, dob, name, father = None, None, None, None

    # PAN regex
    pan_pattern = re.compile(r"[A-Z]{5}[0-9]{4}[A-Z]{1}")

    for line in lines:
        candidate = clean_text(line.replace(" ", ""))
        if len(candidate) == 10:
            match = pan_pattern.search(candidate)
            if match:
                pan = match.group()
                break
        else:
            for word in candidate.split():
                if len(word) == 10:
                    match = pan_pattern.search(word)
                    if match:
                        pan = match.group()
                        break
        if pan:
            break

    # DOB regex
    dob_pattern = re.compile(r"(\d{2}[-/]\d{2}[-/]\d{4})")
    for line in lines:
        candidate = clean_text(line)
        match = dob_pattern.search(candidate)
        if match:
            dob = match.group().replace("/", "-")
            break

    # Name & Father Name extraction
    for idx, line in enumerate(lines):
        if "INCOME TAX" in line or "GOVT" in line:
            if idx + 1 < len(lines):
                name = lines[idx + 1].title()
            if idx + 2 < len(lines):
                father = lines[idx + 2].title()
            break

    return {
        "PAN": pan,
        "Name": name,
        "Father Name": father,
        "Date of Birth": dob,
        "Raw OCR Lines": lines
    }
