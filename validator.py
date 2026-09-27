import json
import os
from pathlib import Path
from typing import Any, Dict, List
from schemas import InvoiceData

STORAGE_FILE = Path("processed_invoices.json")


def load_recorded_invoices() -> List[Dict[str, Any]]:
    """Loads historical invoice records to perform deduplication checks."""
    if not STORAGE_FILE.exists():
        return []
    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return []


def save_invoice_record(invoice: InvoiceData, status: str) -> None:
    """Appends an approved or audited invoice record into persistent storage."""
    records = load_recorded_invoices()
    records.append({
        "vendor_name": invoice.vendor_name,
        "invoice_number": invoice.invoice_number,
        "total_amount": invoice.total_amount,
        "status": status,
    })
    with open(STORAGE_FILE, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=2)


def validate_invoice_data(invoice: InvoiceData, tolerance: float = 0.05) -> Dict[str, Any]:
    """
    Executes financial and logical validation rules against parsed invoice data:
    1. Row-level item arithmetic (Quantity * Unit Price == Line Total).
    2. Sum of line items versus Subtotal.
    3. Grand Total reconciliation (Subtotal + Tax - Discount == Total).
    4. Issue Date versus Due Date chronology.
    5. Deduplication against historical records.
    """
    errors: List[str] = []
    warnings: List[str] = []

    # 1. Line item arithmetic check
    for index, item in enumerate(invoice.items, start=1):
        expected_line_total = round(item.quantity * item.unit_price, 2)
        if abs(expected_line_total - item.total) > tolerance:
            errors.append(
                f"Line item {index} ('{item.description}') arithmetic mismatch: "
                f"Quantity ({item.quantity}) * Unit Price ({item.unit_price}) = {expected_line_total}, "
                f"but extracted total is {item.total}."
            )

    # 2. Items sum check against Subtotal
    sum_items_total = round(sum(item.total for item in invoice.items), 2)
    if invoice.subtotal > 0:
        if abs(sum_items_total - invoice.subtotal) > tolerance:
            errors.append(
                f"Subtotal discrepancy: Sum of individual items ({sum_items_total}) "
                f"does not match printed subtotal ({invoice.subtotal})."
            )
    else:
        # Fallback: Populate subtotal if not explicitly extracted
        invoice.subtotal = sum_items_total

    # 3. Grand Total calculation check
    expected_grand_total = round(invoice.subtotal + invoice.tax_amount - invoice.discount, 2)
    if abs(expected_grand_total - invoice.total_amount) > tolerance:
        errors.append(
            f"Grand Total mismatch: Calculated value ({expected_grand_total}) "
            f"differs from extracted total ({invoice.total_amount})."
        )

    # 4. Chronological validation
    if invoice.issue_date and invoice.due_date:
        if invoice.due_date < invoice.issue_date:
            warnings.append(
                f"Chronological anomaly: Due date ({invoice.due_date}) "
                f"is earlier than issue date ({invoice.issue_date})."
            )

    # 5. Duplicate detection
    records = load_recorded_invoices()
    is_duplicate = any(
        record.get("vendor_name", "").strip().lower() == invoice.vendor_name.strip().lower() and
        record.get("invoice_number", "").strip().lower() == invoice.invoice_number.strip().lower()
        for record in records
    )
    if is_duplicate:
        errors.append(
            f"Duplicate document: Invoice '{invoice.invoice_number}' "
            f"from vendor '{invoice.vendor_name}' has already been processed."
        )

    # Determine automated routing status
    is_approved = len(errors) == 0
    decision_status = "APPROVED" if is_approved else "NEEDS_REVIEW"

    return {
        "status": decision_status,
        "is_approved": is_approved,
        "errors": errors,
        "warnings": warnings,
        "calculations": {
            "sum_items_total": sum_items_total,
            "expected_grand_total": expected_grand_total,
        }
    }