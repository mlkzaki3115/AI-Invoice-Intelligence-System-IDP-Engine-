import streamlit as st
import requests
import pandas as pd

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Invoice Intelligence System",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI Invoice Intelligence & Auditing System")
st.caption("Human-in-the-Loop Document Processing, Arithmetic Auditing, and Verification")

# 1. Sidebar - File Upload & Connection
with st.sidebar:
    st.header("Upload Document")
    uploaded_file = st.file_uploader(
        "Choose an invoice (PNG, JPG, PDF, WEBP, TIFF, JFIF)",
        type=[".png", ".jpg", ".jpeg", ".pdf",".webp",".tiff","jfif"]
    )
    
    st.markdown("---")
    st.subheader("System Status")
    try:
        health_resp = requests.get(f"{API_BASE_URL}/", timeout=3)
        if health_resp.status_code == 200:
            st.success("Backend API Connected (Port 8000)")
        else:
            st.error("API responded with an error")
    except requests.exceptions.RequestException:
        st.error("Cannot connect to FastAPI server. Ensure `uvicorn main:app --reload` is running.")

# Initialize session state for extracted invoice and editing
if "invoice_response" not in st.session_state:
    st.session_state.invoice_response = None

# Trigger Extraction Pipeline
if uploaded_file and st.sidebar.button("Run AI Extraction", type="primary", use_container_width=True):
    with st.spinner("Analyzing document layout, extracting entities, and executing math audits..."):
        try:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            response = requests.post(f"{API_BASE_URL}/api/v1/process-invoice", files=files, timeout=60)
            
            if response.status_code == 200:
                st.session_state.invoice_response = response.json()
                st.toast("Extraction completed successfully!", icon="✅")
            else:
                st.error(f"API Error ({response.status_code}): {response.text}")
        except Exception as e:
            st.error(f"Failed to connect to extraction endpoint: {str(e)}")

# 2. Main Workspace (Split Screen)
if st.session_state.invoice_response:
    payload = st.session_state.invoice_response
    raw_data = payload.get("data", {})
    validation = payload.get("validation", {})
    
    # Header Status Banner
    status = validation.get("status", "NEEDS_REVIEW")
    if status == "APPROVED":
        st.success("### Status: APPROVED (All arithmetic and logical checks passed)")
    else:
        st.error("### Status: NEEDS REVIEW (Discrepancies flagged during automated audit)")

    # Display Validation Messages
    errors = validation.get("errors", [])
    warnings = validation.get("warnings", [])
    
    if errors:
        with st.expander("🚨 Validation Errors Detected", expanded=True):
            for err in errors:
                st.markdown(f"- :red[{err}]")

    if warnings:
        with st.expander("⚠️ System Warnings", expanded=False):
            for warn in warnings:
                st.markdown(f"- :orange[{warn}]")

    col_left, col_right = st.columns([1, 1.2])

    # Left Column: Original Document Viewer
    with col_left:
        st.subheader("Original Document")
        if uploaded_file:
            if uploaded_file.type.startswith("image/"):
                st.image(uploaded_file, use_container_width=True, caption=payload.get("filename"))
            else:
                st.info(f"Uploaded file: {payload.get('filename')} (PDF rendering preview)")

    # Right Column: Extracted Entities & Editable Form (HITL)
    with col_right:
        st.subheader("Extracted Metadata & Line Items")
        with st.form("invoice_edit_form"):
            c1, c2 = st.columns(2)
            vendor_name = c1.text_input("Vendor / Company", value=raw_data.get("vendor_name", ""))
            invoice_num = c2.text_input("Invoice Number", value=raw_data.get("invoice_number", ""))
            
            c3, c4 = st.columns(2)
            issue_date = c3.text_input("Issue Date", value=raw_data.get("issue_date") or "")
            due_date = c4.text_input("Due Date", value=raw_data.get("due_date") or "")

            st.markdown("#### Line Items")
            items = raw_data.get("items", [])
            df_items = pd.DataFrame(items) if items else pd.DataFrame(columns=["description", "quantity", "unit_price", "total"])
            
            edited_items_df = st.data_editor(
                df_items,
                num_rows="dynamic",
                use_container_width=True
            )

            st.markdown("#### Totals Breakdown")
            t1, t2, t3 = st.columns(3)
            subtotal = t1.number_input("Subtotal", value=float(raw_data.get("subtotal", 0.0)), step=0.01)
            tax_amount = t2.number_input("Tax / VAT", value=float(raw_data.get("tax_amount", 0.0)), step=0.01)
            discount = t3.number_input("Discount", value=float(raw_data.get("discount", 0.0)), step=0.01)
            
            total_amount = st.number_input(
                "Grand Total",
                value=float(raw_data.get("total_amount", 0.0)),
                step=0.01
            )

            col_submit, col_export = st.columns([1, 1])
            with col_submit:
                save_submitted = st.form_submit_button("Approve & Commit Record", type="primary", use_container_width=True)

        # Handle Save & Persistence via Member 2's Save Endpoint
        if save_submitted:
            updated_items = edited_items_df.to_dict(orient="records")
            final_invoice = {
                "vendor_name": vendor_name,
                "invoice_number": invoice_num,
                "issue_date": issue_date or None,
                "due_date": due_date or None,
                "items": updated_items,
                "subtotal": subtotal,
                "tax_amount": tax_amount,
                "discount": discount,
                "total_amount": total_amount
            }

            save_payload = {
                "invoice": final_invoice,
                "status": "APPROVED"
            }

            with st.spinner("Saving committed record..."):
                save_resp = requests.post(f"{API_BASE_URL}/api/v1/save-invoice", json=save_payload)
                if save_resp.status_code == 200:
                    st.success("Record saved to database/storage!")
                else:
                    st.error(f"Failed to save: {save_resp.text}")

        # JSON Export / Download
        st.download_button(
            label="Download Structured JSON",
            data=pd.Series(raw_data).to_json(indent=2),
            file_name=f"{invoice_num or 'invoice'}_extracted.json",
            mime="application/json"
        )
else:
    st.info("Upload an invoice from the left sidebar and click 'Run AI Extraction' to get started.")