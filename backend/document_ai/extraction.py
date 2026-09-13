import re
from typing import Dict, Any, Optional

class DocumentExtractor:
    def __init__(self):
        # Basic patterns
        self.amount_pattern = re.compile(r'Total:\s*[\$]?\s*([\d,]+\.?\d*)', re.IGNORECASE)
        self.subtotal_pattern = re.compile(r'Sub(?:total)?:?\s*[\$]?\s*([\d,]+\.?\d*)', re.IGNORECASE)
        self.tax_pattern = re.compile(r'Tax:?\s*[\$]?\s*([\d,]+\.?\d*)', re.IGNORECASE)
        
        self.invoice_num_pattern1 = re.compile(r'Invoice\s*#?:?\s*(INV[-_]?\w+)', re.IGNORECASE)
        self.invoice_num_pattern2 = re.compile(r'INV\s*Number:?\s*(INV[-_]?\w+)', re.IGNORECASE)
        
        self.date_pattern1 = re.compile(r'Date:\s*(\d{4}-\d{2}-\d{2})', re.IGNORECASE)
        self.date_pattern2 = re.compile(r'Due:\s*(\d{4}-\d{2}-\d{2})', re.IGNORECASE)
        
        self.vendor_pattern1 = re.compile(r'From:\s*([^\n]+)', re.IGNORECASE)
        
    def normalize_amount(self, amount_str: str) -> Optional[float]:
        if not amount_str:
            return None
        try:
            clean_str = amount_str.replace(',', '').strip()
            return float(clean_str)
        except ValueError:
            return None
            
    def normalize_date(self, date_str: str) -> Optional[str]:
        if not date_str:
            return None
        return date_str.strip()
        
    def normalize_vendor(self, vendor_str: str) -> Optional[str]:
        if not vendor_str:
            return None
        return vendor_str.strip()

    def extract_fields(self, raw_text: str) -> Dict[str, Any]:
        result = {
            'invoice_id': None,
            'vendor_name': None,
            'date_issued': None,
            'due_date': None,
            'amount': None,
            'tax': None,
            'total': None
        }
        
        # Invoice number
        m = self.invoice_num_pattern1.search(raw_text)
        if not m:
            m = self.invoice_num_pattern2.search(raw_text)
        if m:
            result['invoice_id'] = m.group(1).strip()
            
        # Vendor
        m = self.vendor_pattern1.search(raw_text)
        if m:
            result['vendor_name'] = self.normalize_vendor(m.group(1))
        else:
            # Try to grab the first line of the text if it's the center layout (Template 2)
            lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
            if lines:
                # If first line doesn't look like INVOICE, it might be the vendor
                if 'INVOICE' not in lines[0].upper():
                    result['vendor_name'] = self.normalize_vendor(lines[0])
                    
        # Dates
        m = self.date_pattern1.search(raw_text)
        if m:
            result['date_issued'] = self.normalize_date(m.group(1))
            
        m = self.date_pattern2.search(raw_text)
        if m:
            result['due_date'] = self.normalize_date(m.group(1))
            
        # Amounts
        m = self.subtotal_pattern.search(raw_text)
        if m:
            result['amount'] = self.normalize_amount(m.group(1))
            
        m = self.tax_pattern.search(raw_text)
        if m:
            result['tax'] = self.normalize_amount(m.group(1))
            
        m = self.amount_pattern.search(raw_text)
        if m:
            result['total'] = self.normalize_amount(m.group(1))
            
        return result
