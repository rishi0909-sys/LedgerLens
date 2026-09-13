import os
import pandas as pd
import json

from backend.document_ai.document_features import process_documents

def main():
    image_dir = 'data/processed/invoices_images'
    metadata_path = 'data/processed/invoices_images/documents_metadata.json'
    ledger_df = pd.read_parquet('data/processed/invoices.parquet')
    output_dir = 'data/processed/ml/'
    
    print("Running standalone extraction...")
    process_documents(image_dir, metadata_path, ledger_df, output_dir)
    print("Done!")

if __name__ == "__main__":
    main()
