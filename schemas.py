from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field


class LineItem(BaseModel):
    description: str = Field(
        description="Description or name of the product or service sold"
    )
    quantity: float = Field(
        default=1.0, ge=0, description="Quantity of items purchased"
    )
    unit_price: float = Field(
        default=0.0, ge=0, description="Price per unit"
    )
    total: float = Field(
        default=0.0, ge=0, description="Total amount for this specific line item as printed on the invoice"
    )


class InvoiceData(BaseModel):
    vendor_name: str = Field(
        default="Unknown", description="Name of the vendor, issuer, or supplier"
    )
    invoice_number: str = Field(
        default="Unknown", description="Unique invoice identifier or code"
    )
    issue_date: Optional[date] = Field(
        default=None, description="Invoice issue date in YYYY-MM-DD format"
    )
    due_date: Optional[date] = Field(
        default=None, description="Payment due date in YYYY-MM-DD format"
    )
    currency: str = Field(
        default="EGP", description="Currency symbol or 3-letter code (e.g., EGP, USD, EUR, SAR)"
    )

    items: List[LineItem] = Field(
        default_factory=list, description="List of line items extracted from the invoice table"
    )

    subtotal: float = Field(
        default=0.0, description="Subtotal amount before taxes and discounts"
    )
    tax_amount: float = Field(
        default=0.0, description="Sales tax, VAT, or total tax amount applied"
    )
    discount: float = Field(
        default=0.0, description="Applied discount value if specified"
    )
    total_amount: float = Field(
        default=0.0, description="Final grand total amount due for payment"
    )