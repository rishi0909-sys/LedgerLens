import os
import random
import json
from PIL import Image, ImageDraw, ImageFont
import numpy as np

try:
    font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
    font_med = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
    font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
except Exception:
    font_large = ImageFont.load_default()
    font_med = ImageFont.load_default()
    font_small = ImageFont.load_default()

def render_invoice_image(doc_id, invoice_id, vendor_name, company_name, date_issued, due_date, amount, tax, total, description, output_path, template=1):
    width, height = 800, 1000
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    if template == 1:
        draw.text((50, 50), "INVOICE", fill="black", font=font_large)
        draw.text((50, 120), f"From: {vendor_name}", fill="black", font=font_med)
        draw.text((50, 160), f"To: {company_name}", fill="black", font=font_med)
        draw.text((450, 50), f"Invoice #: {invoice_id}", fill="black", font=font_med)
        draw.text((450, 90), f"Date: {date_issued}", fill="black", font=font_med)
        draw.text((450, 130), f"Due: {due_date}", fill="black", font=font_med)
        
        draw.line([(50, 250), (750, 250)], fill="black", width=2)
        draw.text((50, 270), "Description", fill="black", font=font_med)
        draw.text((550, 270), "Amount (USD)", fill="black", font=font_med)
        draw.line([(50, 310), (750, 310)], fill="black", width=2)
        
        draw.text((50, 340), description, fill="black", font=font_small)
        draw.text((550, 340), f"{amount:.2f}", fill="black", font=font_med)
        
        draw.line([(400, 600), (750, 600)], fill="black", width=1)
        draw.text((400, 620), f"Subtotal: {amount:.2f}", fill="black", font=font_med)
        draw.text((400, 660), f"Tax: {tax:.2f}", fill="black", font=font_med)
        draw.line([(400, 700), (750, 700)], fill="black", width=2)
        draw.text((400, 720), f"Total: {total:.2f}", fill="black", font=font_large)
        
    elif template == 2:
        # Centered layout
        draw.text((300, 50), vendor_name.upper(), fill="black", font=font_large)
        draw.text((320, 100), "OFFICIAL INVOICE", fill="gray", font=font_med)
        
        draw.text((50, 200), f"Bill To: {company_name}", fill="black", font=font_med)
        draw.text((550, 200), f"INV Number: {invoice_id}", fill="black", font=font_small)
        draw.text((550, 230), f"Date: {date_issued}", fill="black", font=font_small)
        
        draw.rectangle([(50, 300), (750, 350)], outline="black", width=2)
        draw.text((60, 310), "Item", fill="black", font=font_med)
        draw.text((600, 310), "Price", fill="black", font=font_med)
        
        draw.text((60, 370), description, fill="black", font=font_small)
        draw.text((600, 370), f"${amount:.2f}", fill="black", font=font_med)
        
        draw.text((500, 700), f"Sub: ${amount:.2f}", fill="black", font=font_small)
        draw.text((500, 730), f"Tax: ${tax:.2f}", fill="black", font=font_small)
        draw.text((500, 760), f"Amount Due: ${total:.2f}", fill="black", font=font_large)
        
    # Add a bit of noise to simulate scan
    img_array = np.array(image)
    noise = np.random.normal(0, 5, img_array.shape).astype(np.uint8)
    noisy_img = np.clip(img_array + noise, 0, 255).astype(np.uint8)
    final_image = Image.fromarray(noisy_img)
    
    final_image.save(output_path)

def generate_documents(invoices, companies, vendors, output_dir, anomaly_ratio=0.1):
    os.makedirs(output_dir, exist_ok=True)
    
    company_map = {c.id: c.name for c in companies}
    vendor_map = {v.id: v.name for v in vendors}
    
    metadata = []
    
    for inv in invoices:
        company_name = company_map[inv.company_id]
        vendor_name = vendor_map[inv.vendor_id]
        
        # Decide if this document will have an anomaly
        is_doc_anomaly = random.random() < anomaly_ratio
        anomaly_type = None
        
        render_amount = inv.amount
        render_tax = inv.tax_amount
        render_total = inv.amount + inv.tax_amount
        render_vendor = vendor_name
        render_date = inv.date_issued.strftime('%Y-%m-%d')
        
        if is_doc_anomaly:
            anomaly_types = ['amount_mismatch', 'vendor_alteration', 'date_alteration', 'arithmetic_error']
            anomaly_type = random.choice(anomaly_types)
            
            if anomaly_type == 'amount_mismatch':
                render_amount = inv.amount * 10 # classic extra zero fraud
                render_total = render_amount + render_tax
            elif anomaly_type == 'vendor_alteration':
                render_vendor = vendor_name + " LLC (Payment Account)"
            elif anomaly_type == 'date_alteration':
                from datetime import timedelta
                render_date = (inv.date_issued + random.choice([timedelta(days=90), timedelta(days=-90)])).strftime('%Y-%m-%d')
            elif anomaly_type == 'arithmetic_error':
                render_total = render_amount + render_tax + random.uniform(500, 5000)
                
        doc_id = f"DOC_{inv.invoice_id}"
        template = random.choice([1, 2])
        output_path = os.path.join(output_dir, f"{doc_id}.png")
        
        render_invoice_image(
            doc_id=doc_id,
            invoice_id=inv.invoice_id,
            vendor_name=render_vendor,
            company_name=company_name,
            date_issued=render_date,
            due_date=inv.due_date.strftime('%Y-%m-%d'),
            amount=render_amount,
            tax=render_tax,
            total=render_total,
            description=inv.description,
            output_path=output_path,
            template=template
        )
        
        meta = {
            "document_id": doc_id,
            "invoice_id": inv.invoice_id,
            "template_id": template,
            "is_document_anomaly": is_doc_anomaly,
            "document_anomaly_type": anomaly_type,
            "rendered_fields": {
                "amount": render_amount,
                "tax": render_tax,
                "total": render_total,
                "vendor_name": render_vendor,
                "date_issued": render_date
            }
        }
        metadata.append(meta)
        
        # Optionally generate a duplicate
        if is_doc_anomaly and random.random() < 0.2:
            dup_doc_id = f"DOC_DUP_{inv.invoice_id}"
            dup_output_path = os.path.join(output_dir, f"{dup_doc_id}.png")
            # Same rendered fields, maybe a different template or identical
            render_invoice_image(
                doc_id=dup_doc_id,
                invoice_id=inv.invoice_id, # exact same invoice ID
                vendor_name=render_vendor,
                company_name=company_name,
                date_issued=render_date,
                due_date=inv.due_date.strftime('%Y-%m-%d'),
                amount=render_amount,
                tax=render_tax,
                total=render_total,
                description=inv.description,
                output_path=dup_output_path,
                template=template
            )
            dup_meta = meta.copy()
            dup_meta["document_id"] = dup_doc_id
            dup_meta["document_anomaly_type"] = "duplicate"
            metadata.append(dup_meta)
            
    with open(os.path.join(output_dir, 'documents_metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=2)
        
    print(f"Generated {len(metadata)} document images to {output_dir}")
