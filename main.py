from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any

from schemas import InvoiceData
from ai_pipeline import process_and_extract, convert_file_to_image, extract_invoice_from_image
from validator import validate_invoice_data, save_invoice_record

app = FastAPI(
    title="AI Document Intelligence API",
    description="Automated invoice extraction, arithmetic validation, and auditing pipeline.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SaveRequest(BaseModel):
    invoice: InvoiceData
    status: str = "APPROVED"


@app.get("/")
def health_check() -> Dict[str, str]:
    """Health check endpoint to verify backend operational readiness."""
    return {"status": "healthy", "service": "AI Document Intelligence Engine"}


@app.post("/api/v1/process-invoice")
async def process_invoice_endpoint(file: UploadFile = File(...)):
    valid_extensions = (".png", ".jpg", ".jpeg", ".pdf", ".webp", ".tiff", ".jfif")
    if not file.filename or not file.filename.lower().endswith(valid_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Accepted formats: {', '.join(valid_extensions)}",
        )

    try:
        contents = await file.read()
        extracted_data, _ = process_and_extract(contents, file.filename)
        validation_report = validate_invoice_data(extracted_data)

        return {
            "success": True,
            "filename": file.filename,
            "data": extracted_data.model_dump(),
            "validation": validation_report,
        }
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(err)}")

@app.post("/api/v1/save-invoice")
def save_invoice_endpoint(payload: SaveRequest) -> Dict[str, Any]:
    """Persists verified or human-reviewed invoice data into system records."""
    try:
        save_invoice_record(payload.invoice, payload.status)
        return {"success": True, "message": "Invoice successfully committed to storage."}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Storage operation failed: {str(exc)}")
