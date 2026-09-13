from typing import List, Optional, Dict
from pydantic import BaseModel
from faker import Faker
import random
from datetime import datetime, timedelta

from .entities import Company, Employee, Vendor, Account

class Transaction(BaseModel):
    transaction_id: str
    timestamp: datetime
    source_account: str
    destination_account: str
    amount: float
    currency: str
    transaction_type: str  # 'SALARY', 'INVOICE_PAYMENT', 'TRANSFER', 'REIMBURSEMENT'
    description: str
    invoice_id: Optional[str] = None
    is_anomaly: bool = False
    anomaly_type: Optional[str] = None

def generate_normal_transactions(
    fake: Faker, 
    accounts: List[Account], 
    start_date: datetime, 
    end_date: datetime,
    num_transactions: int
) -> List[Transaction]:
    transactions = []
    
    # Pre-categorize accounts for quick access
    company_accounts = [a for a in accounts if a.account_type == 'company']
    employee_accounts = [a for a in accounts if a.account_type == 'employee']
    vendor_accounts = [a for a in accounts if a.account_type == 'vendor']

    if not company_accounts:
        return transactions

    delta = end_date - start_date

    for _ in range(num_transactions):
        # Pick a random timestamp within the range
        random_seconds = random.randint(0, int(delta.total_seconds()))
        ts = start_date + timedelta(seconds=random_seconds)
        
        tx_type = random.choices(['SALARY', 'INVOICE_PAYMENT', 'REIMBURSEMENT'], weights=[0.2, 0.6, 0.2])[0]
        
        source = random.choice(company_accounts)
        dest = None
        amount = 0.0
        desc = ""
        
        if tx_type == 'SALARY' and employee_accounts:
            dest = random.choice(employee_accounts)
            amount = round(random.uniform(2000, 15000), 2)
            desc = "Monthly Salary Payment"
        elif tx_type == 'INVOICE_PAYMENT' and vendor_accounts:
            dest = random.choice(vendor_accounts)
            amount = round(random.uniform(500, 50000), 2)
            desc = "Vendor Invoice Payment"
        elif tx_type == 'REIMBURSEMENT' and employee_accounts:
            dest = random.choice(employee_accounts)
            amount = round(random.uniform(50, 2000), 2)
            desc = "Travel and Expense Reimbursement"
        
        if dest is not None:
            tx = Transaction(
                transaction_id=f"TXN_{fake.unique.uuid4()[:8]}",
                timestamp=ts,
                source_account=source.id,
                destination_account=dest.id,
                amount=amount,
                currency="USD",
                transaction_type=tx_type,
                description=desc
            )
            transactions.append(tx)
            
    # Sort transactions by timestamp
    transactions.sort(key=lambda x: x.timestamp)
    return transactions
