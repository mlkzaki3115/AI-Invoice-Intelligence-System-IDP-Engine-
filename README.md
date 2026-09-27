# AI Invoice Intelligence System (IDP Engine)

An end-to-end Intelligent Document Processing (IDP) system engineered to ingest, extract, validate, and audit commercial invoices from documents and images. The pipeline pairs Multimodal Vision-Language Models (VLMs) with deterministic programmatic auditing rules to automate financial workflows, prevent double payments, and flag accounting discrepancies.

---


## 🌐 Live Demo

Experience the live deployed application here:  
👉 **[Launch AI Invoice Intelligence System Demo](https://ai-invoice-intelligence-system.streamlit.app/)**

---

## 📌 Overview

Manual invoice entry is time-consuming and error-prone. This application streamlines accounts payable tasks by:
* Ingesting single-page invoice documents in PDF, PNG, JPG, or JPEG format.
* Extracting vendor metadata, invoice numbers, billing dates, itemized rows, and grand totals.
* Verifying line-item math (`Unit Price × Quantity == Line Total`) and sum consistency.
* Flagging calculation mismatches with visual indicators for human review.
* Presenting extracted line items in an editable and interactive data table.

---

## 🛠️ Tech Stack

* **Language:** Python 3.9+
* **Framework:** Streamlit
* **AI & Vision:** Google Gemini API (`google-genai`)
* **Data Validation:** Pydantic
* **Document Processing:** Pillow (PIL), PyMuPDF / pdf2image
* **Environment Management:** python-dotenv

---

## 📂 Project Structure

```text
AI-INVOICE-INTELLIGENCE-SYSTEM/
│
├── schemas.py          # Pydantic schemas and strict data models
├── validator.py        # Arithmetic integrity checks and rule engine
├── ai_pipeline.py      # Multimodal extraction logic via Gemini API
├── app.py              # Streamlit user interface
├── requirements.txt    # Project dependencies
├── .env                # Local API credentials (git-ignored)
└── README.md           # Documentation

```

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone [https://github.com/mlkzaki3115/AI-Invoice-Intelligence-System-IDP-Engine-.git]
```

### 2. Set Up a Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt

```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE

```

---

## 💻 Running the Application

Launch the Streamlit web dashboard:

```bash
streamlit run app.py

```

The application will launch in your browser at `http://localhost:8501`.

---

## 🔍 Validation Logic

The application performs real-time arithmetic checks on all extracted figures:

* **Line Item Check:** `Quantity × Unit Price == Line Total`
* **Subtotal Check:** `Sum(Line Totals) == Subtotal`
* **Grand Total Check:** `Subtotal + Tax - Discount == Grand Total`
* **Date Sanity:** Verifies that the payment due date does not precede the invoice issue date.

---

## 📄 License

this project was developed as part of the Tech Master final project.

```

