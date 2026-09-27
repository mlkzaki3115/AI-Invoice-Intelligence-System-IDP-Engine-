import io
import os
import time
from pathlib import Path
from typing import Tuple
from PIL import Image, ImageOps
import fitz  # PyMuPDF
from dotenv import load_dotenv
from google import genai
from google.genai import types

try:
    import fitz  # PyMuPDF: no system Poppler dependency needed for PDF-to-image conversion
except ImportError:  # pragma: no cover - dependency is installed in the project environment
    fitz = None

from schemas import InvoiceData

# 1. تحميل مفتاح الـ API
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    api_key = api_key.strip().strip("'").strip('"')

if not api_key:
    raise ValueError(f"لم يتم العثور على GEMINI_API_KEY في ملف .env: {env_path}")

# إعداد SDK المستقر
client = genai.Client(api_key=api_key)
MODEL_CANDIDATES = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.1-flash-lite-preview",
]


def build_generation_config() -> types.GenerateContentConfig:
    """Create a compatible JSON generation config for the current Google GenAI SDK."""
    return types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=0.1,
    )


def generate_invoice_response(prompt: str, image: Image.Image):
    """Try multiple supported Gemini models and retry transient API overloads."""
    last_error = None

    for attempt, model_name in enumerate(MODEL_CANDIDATES, start=1):
        try:
            print(f"[*] محاولة استخراج البيانات عبر نموذج Gemini: {model_name} ({attempt}/{len(MODEL_CANDIDATES)})")
            return client.models.generate_content(
                model=model_name,
                contents=[prompt, image],
                config=build_generation_config(),
            )
        except Exception as exc:  # pragma: no cover - depends on live API availability
            last_error = exc
            message = str(exc).lower()
            if "503" in message or "429" in message or "high demand" in message or "quota" in message or "unavailable" in message:
                time.sleep(2 * attempt)
                continue
            raise

    raise last_error


def convert_file_to_image(file_bytes: bytes, filename: str) -> Image.Image:
    """Accepts any valid image format or PDF and converts it into a standard RGB PIL Image."""
    # Check if the file is a PDF
    if filename.lower().endswith(".pdf") or file_bytes.startswith(b"%PDF"):
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        if len(doc) == 0:
            raise ValueError("The provided PDF file is empty.")

        # Rasterize first page to high-res image
        page = doc[0]
        pix = page.get_pixmap(dpi=200)
        return Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")

    # For all other image formats (PNG, JPG, TIFF, WEBP, BMP, etc.)
    try:
        image = Image.open(io.BytesIO(file_bytes))

        # Auto-rotate based on EXIF metadata (e.g., photos taken by smartphones)
        image = ImageOps.exif_transpose(image)

        # Standardize to 3-channel RGB (handles RGBA, grayscale, CMYK, palettes)
        return image.convert("RGB")

    except Exception as exc:
        raise ValueError(
            f"Unable to process file '{filename}' as an image: {str(exc)}"
        )

def extract_invoice_from_image(image: Image.Image) -> InvoiceData:
    """استخراج بيانات الفاتورة وإرجاعها كـ Pydantic Model مدعوم ومضمون."""
    prompt = """
    You are an expert financial auditor and invoice OCR extraction engine.
    Extract the invoice data strictly from the provided image and return ONLY valid JSON that matches the following schema.

    Required JSON fields:
    {
      "vendor_name": "string",
      "invoice_number": "string",
      "issue_date": "YYYY-MM-DD or null",
      "due_date": "YYYY-MM-DD or null",
      "currency": "string",
      "items": [
        {
          "description": "string",
          "quantity": "number",
          "unit_price": "number",
          "total": "number"
        }
      ],
      "subtotal": "number",
      "tax_amount": "number",
      "discount": "number",
      "total_amount": "number"
    }

    Critical Instructions:
    1. Read the invoice text exactly as it appears, without inventing missing information.
    2. Keep numeric values as real numbers, not strings.
    3. Normalize any dates to ISO format YYYY-MM-DD.
    4. If a field is missing or unclear, use a safe default value such as null or 0.0.
    5. Return only valid JSON with no markdown, no explanations, and no extra text.
    """

    response = generate_invoice_response(prompt, image)
    return InvoiceData.model_validate_json(response.text)


def process_and_extract(file_bytes: bytes, filename: str) -> Tuple[InvoiceData, Image.Image]:
    image = convert_file_to_image(file_bytes, filename)
    extracted_data = extract_invoice_from_image(image)
    return extracted_data, image


if __name__ == "__main__":
    test_image_path = "test_invoices/sample.png"
    if os.path.exists(test_image_path):
        with open(test_image_path, "rb") as f:
            data, _ = process_and_extract(f.read(), "sample.png")
            print("\n--- Extraction Successful ---")
            print(data.model_dump_json(indent=2))
    else:
        print(f"الملف غير موجود في: {test_image_path}")