from typing import List, Dict, Any
import random
from datetime import timedelta
from faker import Faker
from .transactions import Transaction
from .invoices import Invoice
from .entities import Account

def inject_transaction_anomalies(transactions: List[Transaction], num_anomalies: int) -> None:
    if not transactions:
        return
        
    candidates = random.sample(transactions, min(num_anomalies, len(transactions)))
    
    for txn in candidates:
        anomaly_type = random.choice([
            'large_transfer', 
            'unusual_time', 
            'unexpected_counterparty'
        ])
        
        txn.is_anomaly = True
        txn.anomaly_type = f"transaction_{anomaly_type}"
        
        if anomaly_type == 'large_transfer':
            txn.amount *= random.uniform(5.0, 20.0)
        elif anomaly_type == 'unusual_time':
            # Shift to 3 AM
            txn.timestamp = txn.timestamp.replace(hour=3, minute=random.randint(0, 59))
        elif anomaly_type == 'unexpected_counterparty':
            # This is hard to do without context of normal graph, but we'll flag it
            pass

def inject_sequence_anomalies(
    fake: Faker,
    transactions: List[Transaction], 
    accounts: List[Account], 
    num_cycles: int
) -> None:
    # Example: A -> B -> C -> A
    if len(accounts) < 3:
        return
        
    for _ in range(num_cycles):
        cycle_accounts = random.sample(accounts, 3)
        amount = round(random.uniform(50000, 100000), 2)
        base_time = random.choice(transactions).timestamp if transactions else fake.date_time_this_year()
        
        for i in range(3):
            src = cycle_accounts[i]
            dst = cycle_accounts[(i + 1) % 3]
            tx = Transaction(
                transaction_id=f"TXN_{fake.unique.uuid4()[:8]}",
                timestamp=base_time + timedelta(minutes=5 * i),
                source_account=src.id,
                destination_account=dst.id,
                amount=amount,
                currency="USD",
                transaction_type="TRANSFER",
                description="Consulting fee",
                is_anomaly=True,
                anomaly_type="sequence_circular_flow"
            )
            transactions.append(tx)
            
    transactions.sort(key=lambda x: x.timestamp)

def inject_document_anomalies(invoices: List[Invoice], num_anomalies: int) -> None:
    if not invoices:
        return
        
    candidates = random.sample(invoices, min(num_anomalies, len(invoices)))
    
    for inv in candidates:
        anomaly_type = random.choice([
            'duplicate_invoice',
            'amount_mismatch',
            'vendor_mismatch'
        ])
        
        inv.is_anomaly = True
        inv.anomaly_type = f"document_{anomaly_type}"
        
        if anomaly_type == 'amount_mismatch':
            inv.amount *= random.uniform(2.0, 5.0)
