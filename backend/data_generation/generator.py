import argparse
from faker import Faker
import pandas as pd
from datetime import datetime, timedelta
import os
import json
import random

from backend.data_generation.entities import generate_companies, generate_employees, generate_vendors, generate_accounts
from backend.data_generation.transactions import generate_normal_transactions
from backend.data_generation.invoices import generate_normal_invoices
from backend.data_generation.anomalies import inject_transaction_anomalies, inject_sequence_anomalies, inject_document_anomalies

def generate_synthetic_data(
    seed: int, 
    num_companies: int, 
    num_employees: int, 
    num_vendors: int,
    num_transactions: int,
    num_invoices: int,
    num_anomalies: int,
    output_dir: str
):
    print(f"Generating synthetic financial world with seed {seed}")
    
    # Set seeds for reproducibility
    fake = Faker()
    Faker.seed(seed)
    random.seed(seed)
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate Entities
    print("Generating entities...")
    companies = generate_companies(fake, num_companies)
    employees = generate_employees(fake, companies, num_employees)
    vendors = generate_vendors(fake, num_vendors)
    
    all_entities = companies + employees + vendors
    
    accounts = generate_accounts(fake, companies, 'company') + \
               generate_accounts(fake, employees, 'employee') + \
               generate_accounts(fake, vendors, 'vendor')
               
    # Save entities
    entities_data = [e.model_dump() for e in all_entities]
    accounts_data = [a.model_dump() for a in accounts]
    
    with open(os.path.join(output_dir, 'entities.json'), 'w') as f:
        json.dump(entities_data, f)
    with open(os.path.join(output_dir, 'accounts.json'), 'w') as f:
        json.dump(accounts_data, f)

    # Generate Activity
    print("Generating activity...")
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 12, 31)
    
    transactions = generate_normal_transactions(fake, accounts, start_date, end_date, num_transactions)
    invoices = generate_normal_invoices(fake, companies, vendors, start_date, end_date, num_invoices)
    
    # Inject Anomalies
    print("Injecting anomalies...")
    inject_transaction_anomalies(transactions, num_anomalies // 3)
    inject_sequence_anomalies(fake, transactions, accounts, max(1, num_anomalies // 3))
    inject_document_anomalies(invoices, num_anomalies // 3)
    
    from backend.data_generation.documents import generate_documents
    
    # Save Transactions and Invoices as Parquet
    print("Saving datasets...")
    df_tx = pd.DataFrame([t.model_dump() for t in transactions])
    df_inv = pd.DataFrame([i.model_dump() for i in invoices])
    
    df_tx.to_parquet(os.path.join(output_dir, 'transactions.parquet'))
    df_inv.to_parquet(os.path.join(output_dir, 'invoices.parquet'))
    
    # Generate Synthetic Documents
    print("Generating synthetic documents...")
    doc_output_dir = os.path.join(output_dir, 'invoices_images')
    generate_documents(invoices, companies, vendors, doc_output_dir, anomaly_ratio=0.1)
    
    # Save Ground Truth separately
    ground_truth = {
        'anomalous_transactions': df_tx[df_tx['is_anomaly'] == True]['transaction_id'].tolist(),
        'anomalous_invoices': df_inv[df_inv['is_anomaly'] == True]['invoice_id'].tolist()
    }
    with open(os.path.join(output_dir, 'ground_truth.json'), 'w') as f:
        json.dump(ground_truth, f)
        
    print(f"Data generation complete! Saved to {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--companies', type=int, default=10)
    parser.add_argument('--employees', type=int, default=100)
    parser.add_argument('--vendors', type=int, default=50)
    parser.add_argument('--transactions', type=int, default=10000)
    parser.add_argument('--invoices', type=int, default=1000)
    parser.add_argument('--anomalies', type=int, default=100)
    parser.add_argument('--output-dir', type=str, default='data/processed')
    args = parser.parse_args()
    
    generate_synthetic_data(
        args.seed, args.companies, args.employees, args.vendors, 
        args.transactions, args.invoices, args.anomalies, args.output_dir
    )
