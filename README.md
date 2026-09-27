# AI Invoice Intelligence System (IDP Engine)

An end-to-end Intelligent Document Processing (IDP) system engineered to ingest, extract, validate, and audit commercial invoices from documents and images. The pipeline pairs Multimodal Vision-Language Models (VLMs) with deterministic programmatic auditing rules to automate financial workflows, prevent double payments, and flag accounting discrepancies.

---

## Live Demo & Resources

* **Interactive Web Application:** [Live Streamlit App](https://www.google.com/search?q=https://your-streamlit-app-link.streamlit.app&utm_source=gemini)
* **API Documentation (Swagger):** [Interactive API Docs](https://www.google.com/search?q=https://your-api-domain.com/docs&utm_source=gemini)
* **Demonstration Video / Walkthrough:** [Demo Video Link](https://www.google.com/search?q=https://youtube.com/your-demo-video-link&utm_source=gemini)

---

## System Architecture

```
[ Input: Any Image / PDF Document ]
                │
                ▼
[ Ingestion & Format Normalization ]
   ├── In-Memory Rasterization (PyMuPDF)
   ├── Byte-Level Image Decoding & EXIF Transposition (Pillow)
   └── Format-Agnostic Dynamic Ingestion (.png, .jpg, .webp, .tiff, .pdf, .heic)
                │
                ▼
[ Vision-Language Contextual Extraction ]
   ├── Schema Enforcement & Strict Typing (Pydantic v2)
   └── Spatial & Tabular Entity Extraction (Multimodal LLM)
                │
                ▼
[ Algorithmic Financial Auditing Engine ]
   ├── Line Item Arithmetic: (Qty × Unit Price == Line Total)
   ├── Accumulation Check: (Σ Line Totals == Subtotal)
   ├── Ledger Balancing: (Subtotal + Tax - Discounts == Grand Total)
   ├── Temporal Verification: (Due Date ≥ Issue Date)
   └── Duplicate Prevention Engine: (Vendor + Invoice Number Fingerprint)
                │
                ▼
[ Verification Workflow & Persistence ]
   ├── Status Routing: APPROVED vs. NEEDS_REVIEW
   ├── REST API Service Layer (FastAPI)
   └── Interactive HITL Dashboard & Data Export (Streamlit)

```

---

## Core Capabilities

* **Format-Agnostic Ingestion:** Dynamic file handler decodes all standard and raw document formats (`PDF`, `PNG`, `JPG`, `JPEG`, `WEBP`, `TIFF`, `BMP`, `HEIC`) directly from memory streams, avoiding OS-dependent utilities.
* **Deterministic Structured Extraction:** Enforces a rigid schema for invoice entities—including header attributes, party identification, and itemized matrices—eliminating unstructured text parsing.
* **Multi-Tiered Rule Validation:** Programmatically audits arithmetic balance across every line item and total field, catching subtle calculation errors and pricing anomalies before persistence.
* **Duplicate Invoice Detection:** Cross-references incoming identifiers against a local transaction ledger to eliminate duplicate invoicing and double payment risks.
* **Human-in-the-Loop (HITL) Workflow:** Automatically classifies outputs into review states (`APPROVED` or `NEEDS_REVIEW`) and exposes field-level error messages to operators.

---

## Repository Structure

```text
├── main.py                 # FastAPI REST service & application entrypoint
├── schemas.py              # Pydantic data contracts (InvoiceData, LineItem, AuditReport)
├── ai_pipeline.py          # Multimodal ingestion, image transformation & extraction logic
├── validator.py            # Mathematical auditing, business rules & deduplication logic
├── app.py                  # Streamlit HITL dashboard with live verification interface
├── evaluate.py             # Automated benchmarking suite & evaluation metrics
├── processed_invoices.json # Local audit ledger for duplicate prevention & records
├── test_invoices/          # Test dataset covering edge-case and baseline invoices
└── requirements.txt        # Pinned runtime dependencies

```

---

## Getting Started

### 1. Prerequisites

* Python 3.10 or higher
* Valid API credentials for your chosen Multimodal VLM provider (e.g., Gemini API or OpenAI API)

### 2. Environment Setup

```bash
# Clone the repository
git clone https://github.com/your-username/ai-invoice-intelligence.git
cd ai-invoice-intelligence

# Initialize virtual environment
python -m venv venv

# Activate environment
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

```

### 3. Environment Variables

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY="your_api_key_here"

```

---

## Usage

### Running the API Backend

```bash
uvicorn main:app --reload --port 8000

```

* **Interactive Documentation (Swagger):** `[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)`
* **Alternative API Schema (ReDoc):** `[http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)`

### Running the Streamlit Interface

```bash
streamlit run app.py

```

### Running the Evaluation Suite

```bash
python evaluate.py

```

---

## API Reference

### 1. Process Document

* **Endpoint:** `POST /api/v1/process-invoice`
* **Content-Type:** `multipart/form-data`
* **Request Parameter:** `file` (Binary document or image)

**Example Response:**

```json
{
  "success": true,
  "filename": "invoice_US001.pdf",
  "data": {
    "vendor_name": "East Repair Inc.",
    "invoice_number": "US-001",
    "issue_date": "2019-02-11",
    "due_date": "2019-02-26",
    "items": [
      {
        "description": "Front and rear brake cables",
        "quantity": 1.0,
        "unit_price": 100.0,
        "total": 100.0
      },
      {
        "description": "New set of pedal arms",
        "quantity": 2.0,
        "unit_price": 15.0,
        "total": 30.0
      }
    ],
    "subtotal": 145.0,
    "tax_amount": 9.06,
    "discount": 0.0,
    "total_amount": 154.06
  },
  "validation": {
    "status": "APPROVED",
    "is_approved": true,
    "errors": [],
    "warnings": []
  }
}

```

### 2. Save Verified Record

* **Endpoint:** `POST /api/v1/save-invoice`
* **Content-Type:** `application/json`
* **Payload:** Structured `InvoiceData` payload to commit to the persistence ledger.