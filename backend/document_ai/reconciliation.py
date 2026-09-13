from typing import Dict, Any, Optional

def _fuzzy_match(str1: Optional[str], str2: Optional[str]) -> bool:
    if not str1 or not str2:
        return False
    # Simple case-insensitive match, stripping common suffixes if necessary
    s1 = str1.lower().strip()
    s2 = str2.lower().strip()
    
    # We injected " LLC (Payment Account)" to some vendors, so let's see if one contains another
    if s1 in s2 or s2 in s1:
        return True
    return False

def _exact_match(val1: Any, val2: Any, tolerance: float = 0.01) -> bool:
    if val1 is None or val2 is None:
        return False
    if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
        return abs(val1 - val2) <= tolerance
    return val1 == val2

def reconcile_document_to_ledger(extracted: Dict[str, Any], ledger_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare extracted document fields against structured ledger record.
    ledger_record is a dict containing expected fields:
    - amount
    - vendor_name
    - date_issued
    """
    amount_match = _exact_match(extracted.get('amount'), ledger_record.get('amount'))
    # If the document subtotal matches the ledger amount, they match.
    # Note: ledger amount is often the subtotal. Let's compare subtotal.
    
    vendor_match = _fuzzy_match(extracted.get('vendor_name'), ledger_record.get('vendor_name'))
    
    date_match = _exact_match(extracted.get('date_issued'), ledger_record.get('date_issued'))
    
    # Arithmetic consistency
    ext_subtotal = extracted.get('amount')
    ext_tax = extracted.get('tax')
    ext_total = extracted.get('total')
    
    arithmetic_consistency = True
    if ext_subtotal is not None and ext_tax is not None and ext_total is not None:
        arithmetic_consistency = abs((ext_subtotal + ext_tax) - ext_total) < 0.1
        
    risk = "LOW"
    if not amount_match or not vendor_match or not date_match or not arithmetic_consistency:
        risk = "HIGH"
        
    discrepancies = []
    if not amount_match:
        discrepancies.append({
            "field": "amount",
            "document_value": extracted.get('amount'),
            "ledger_value": ledger_record.get('amount')
        })
    if not vendor_match:
        discrepancies.append({
            "field": "vendor_name",
            "document_value": extracted.get('vendor_name'),
            "ledger_value": ledger_record.get('vendor_name')
        })
    if not date_match:
        discrepancies.append({
            "field": "date_issued",
            "document_value": extracted.get('date_issued'),
            "ledger_value": ledger_record.get('date_issued')
        })
    if not arithmetic_consistency:
        discrepancies.append({
            "field": "arithmetic",
            "document_value": f"{ext_subtotal} + {ext_tax} != {ext_total}",
            "ledger_value": "consistent"
        })
        
    return {
        "invoice_id": extracted.get('invoice_id') or ledger_record.get('invoice_id'),
        "amount_match": amount_match,
        "vendor_match": vendor_match,
        "date_match": date_match,
        "arithmetic_consistency": arithmetic_consistency,
        "risk": risk,
        "discrepancies": discrepancies
    }
