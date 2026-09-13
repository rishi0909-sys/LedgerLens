from typing import List, Optional
from pydantic import BaseModel
from faker import Faker
import random
from datetime import datetime, timedelta

from .entities import Company, Vendor

class Invoice(BaseModel):
    invoice_id: str
    vendor_id: str
    company_id: str
    amount: float
    tax_amount: float
    date_issued: datetime
    due_date: datetime
    description: str
    is_anomaly: bool = False
    anomaly_type: Optional[str] = None

def generate_normal_invoices(
    fake: Faker,
    companies: List[Company],
    vendors: List[Vendor],
    start_date: datetime,
    end_date: datetime,
    count: int
) -> List[Invoice]:
    invoices = []
    
    if not companies or not vendors:
        return invoices
        
    delta = end_date - start_date
    
    for _ in range(count):
        random_seconds = random.randint(0, int(delta.total_seconds()))
        issue_date = start_date + timedelta(seconds=random_seconds)
        due_date = issue_date + timedelta(days=random.choice([15, 30, 45, 60]))
        
        company = random.choice(companies)
        vendor = random.choice(vendors)
        amount = round(random.uniform(500, 50000), 2)
        tax = round(amount * 0.1, 2)
        
        invoice = Invoice(
            invoice_id=f"INV_{fake.unique.uuid4()[:8]}",
            vendor_id=vendor.id,
            company_id=company.id,
            amount=amount,
            tax_amount=tax,
            date_issued=issue_date,
            due_date=due_date,
            description=f"Services provided by {vendor.name}"
        )
        invoices.append(invoice)
        
    return invoices
