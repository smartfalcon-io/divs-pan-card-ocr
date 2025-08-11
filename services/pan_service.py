import re
import requests
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract

# -------------------- TEXT CLEANING --------------------
def clean_text(text):
    text = text.upper()
    text = re.sub(r'[^A-Z0-9\s:/-]', '', text)  # Keep valid chars only
    return text.strip()

# -------------------- IMAGE PREPROCESSING --------------------
def preprocess_image(img_path):
    img = Image.open(img_path).convert("L")  # Convert to grayscale
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2)  # Increase contrast
    img = img.filter(ImageFilter.SHARPEN)  # Sharpen image
    return img

# -------------------- PAN EXTRACTION --------------------
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
        "Name": name,
        "Father Name": father,
        "Date of Birth": dob,
        "Raw OCR Lines": lines
    }


# -------------------- API & VERIFICATION --------------------
def verify_pan_details(api_url, extracted_data, expected_data):
    """
    api_url: str -> Your API endpoint
    extracted_data: dict -> Data from extract_pan_details()
    expected_data: dict -> Data to verify against
    """
    # Send to API
    try:
        response = requests.post(api_url, json=extracted_data)
        if response.status_code != 200:
            return {"status": "error", "message": f"API Error {response.status_code}", "api_response": response.text}

        api_result = response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

    # Verify with expected data
    verification = {}
    for key in ["Name", "Father Name", "Date of Birth"]:
        extracted_val = extracted_data.get(key, "").strip().upper() if extracted_data.get(key) else ""
        expected_val = expected_data.get(key, "").strip().upper() if expected_data.get(key) else ""
        verification[key] = expected_val in extracted_val if expected_val else False

    return {
        "status": "success",
        "verification": verification,
        "api_response": api_result
    }

