import streamlit as st
import pandas as pd
from PIL import Image

# Import models and logic from your separate project files
from schemas import InvoiceData
from validator import validate_invoice_data
from ai_pipeline import process_and_extract

st.set_page_config(layout="wide", page_title="AI Invoice Auditor")
st.title("📄 AI Invoice Auditor & Intelligence System")

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("1. Upload & Preview Invoice")
    uploaded_file = st.file_uploader(
        "Choose an invoice document (PDF or image)",
        type=["png", "jpg", "jpeg", "pdf", "webp", "tiff", "tif", "bmp", "jfif"]
    )
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            st.info("PDF document uploaded successfully")
        else:
            image = Image.open(uploaded_file).convert("RGB")
            st.image(image, use_container_width=True)

with col_right:
    st.subheader("2. Extracted Data & Auditing")
    if uploaded_file and st.button("🚀 Audit & Extract Data"):
        with st.spinner("AI is analyzing and auditing the invoice..."):
            try:
                # 1. Process & extract via ai_pipeline.py
                file_bytes = uploaded_file.getvalue()
                invoice_data, _ = process_and_extract(file_bytes, uploaded_file.name)

                # 2. Run algorithmic verification via validator.py
                validation = validate_invoice_data(invoice_data)

                # Store in session state to persist data across reruns
                st.session_state["invoice_data"] = invoice_data
                st.session_state["validation"] = validation
            except Exception as e:
                st.error(f"Error during processing: {str(e)}")

    if "invoice_data" in st.session_state and "validation" in st.session_state:
        data: InvoiceData = st.session_state["invoice_data"]
        validation = st.session_state["validation"]

        is_approved = validation.get("is_approved", validation.get("status") == "APPROVED")
        errors = validation.get("errors", [])
        warnings = validation.get("warnings", [])

        # Status alert banner
        if is_approved:
            st.success("✅ Invoice is 100% mathematically valid and compliant")
        else:
            st.error("⚠️ Invoice contains arithmetic errors requiring human review:")
            for err in errors:
                st.write(f"- {err}")

        for warn in warnings:
            st.warning(f"- {warn}")

        # Metadata fields
        st.text_input("Vendor Name", value=data.vendor_name)
        st.text_input("Invoice Number", value=data.invoice_number)

        # Line items breakdown
        st.markdown("**Extracted Items Table:**")
        if data.items:
            df = pd.DataFrame([item.model_dump() for item in data.items])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No items detected.")

        # Grand total metric
        st.metric("Total Amount", f"{data.total_amount:,.2f} {data.currency}")