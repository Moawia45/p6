"""
ConstructMind AI - BOQ File Parser Utility
Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744

Provides functions to parse Bill of Quantities (BOQ) files 
in Excel (.xlsx) and PDF formats, extracting item codes,
descriptions, quantities, units, rates, and amounts.
"""

from __future__ import annotations

import logging
import io
import re
from typing import Any, Dict, List
import pandas as pd
import pdfplumber

logger = logging.getLogger("constructmind.utils.file_parser")


def parse_excel_boq(file_bytes: bytes, file_name: str) -> List[Dict[str, Any]]:
    """
    Parse an Excel BOQ sheet and extract structured items.
    Tries to automatically identify columns.
    """
    logger.info(f"Parsing Excel BOQ file: {file_name}")
    try:
        # Load workbook
        excel_file = io.BytesIO(file_bytes)
        df = pd.read_excel(excel_file, dtype=str)
        
        # Fill NaN values with empty string
        df = df.fillna("")
        
        # Convert columns to lowercase for match logic
        headers = [str(col).strip().lower() for col in df.columns]
        
        # Map indices of interest
        item_idx = -1
        desc_idx = -1
        qty_idx = -1
        unit_idx = -1
        rate_idx = -1
        amount_idx = -1
        
        # Common column names mapping
        item_patterns = ["item", "s.no", "sno", "sr", "code", "no"]
        desc_patterns = ["desc", "particular", "work", "detail", "item of work", "specification"]
        qty_patterns = ["qty", "quantity", "volume", "weight"]
        unit_patterns = ["unit", "uom"]
        rate_patterns = ["rate", "unit rate", "price"]
        amount_patterns = ["amount", "total", "cost", "total cost"]
        
        for idx, header in enumerate(headers):
            if any(p in header for p in item_patterns) and item_idx == -1:
                item_idx = idx
            elif any(p in header for p in desc_patterns) and desc_idx == -1:
                desc_idx = idx
            elif any(p in header for p in qty_patterns) and qty_idx == -1:
                qty_idx = idx
            elif any(p in header for p in unit_patterns) and unit_idx == -1:
                unit_idx = idx
            elif any(p in header for p in rate_patterns) and rate_idx == -1:
                rate_idx = idx
            elif any(p in header for p in amount_patterns) and amount_idx == -1:
                amount_idx = idx

        # Fallback mappings if not found
        if desc_idx == -1:
            # If no description column found, try to use the column with longest text
            desc_idx = 1 if len(df.columns) > 1 else 0
        if item_idx == -1:
            item_idx = 0
            
        items = []
        for row_idx, row in df.iterrows():
            row_values = list(row)
            
            # Extract raw values
            item_no = str(row_values[item_idx]).strip() if item_idx < len(row_values) else ""
            description = str(row_values[desc_idx]).strip() if desc_idx < len(row_values) else ""
            
            # Skip empty description rows
            if not description or description.lower() in ["description", "particulars", "total", "grand total"]:
                continue
                
            qty_val = 0.0
            if qty_idx != -1 and qty_idx < len(row_values):
                qty_str = re.sub(r"[^\d\.]", "", str(row_values[qty_idx]))
                qty_val = float(qty_str) if qty_str else 0.0
                
            unit_val = str(row_values[unit_idx]).strip() if (unit_idx != -1 and unit_idx < len(row_values)) else "LS"
            
            rate_val = 0.0
            if rate_idx != -1 and rate_idx < len(row_values):
                rate_str = re.sub(r"[^\d\.]", "", str(row_values[rate_idx]))
                rate_val = float(rate_str) if rate_str else 0.0
                
            amount_val = 0.0
            if amount_idx != -1 and amount_idx < len(row_values):
                amount_str = re.sub(r"[^\d\.]", "", str(row_values[amount_idx]))
                amount_val = float(amount_str) if amount_str else 0.0
            else:
                amount_val = qty_val * rate_val

            # Format item number if empty
            if not item_no:
                item_no = f"{row_idx + 1}"
                
            items.append({
                "item_no": item_no,
                "description": description,
                "quantity": qty_val,
                "unit": unit_val if unit_val else "LS",
                "unit_rate": rate_val,
                "total_amount": amount_val if amount_val > 0 else qty_val * rate_val,
                "source_file": file_name,
                "source_row": row_idx + 1
            })
            
        return items
    except Exception as e:
        logger.error(f"Error parsing Excel BOQ: {e}", exc_info=True)
        raise ValueError(f"Failed to parse Excel file: {e}")


def parse_pdf_boq(file_bytes: bytes, file_name: str) -> List[Dict[str, Any]]:
    """
    Parse a PDF BOQ using pdfplumber to extract tabular items.
    """
    logger.info(f"Parsing PDF BOQ file: {file_name}")
    items = []
    
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            item_counter = 1
            for page_idx, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                for table in tables:
                    if not table or len(table) < 2:
                        continue
                        
                    # Filter out empty tables and check headers
                    headers = [str(cell).strip().lower() for cell in table[0] if cell]
                    
                    # Determine column indices
                    item_idx = 0
                    desc_idx = 1
                    qty_idx = -1
                    unit_idx = -1
                    rate_idx = -1
                    amount_idx = -1
                    
                    # Attempt header scanning
                    for col_idx, col in enumerate(table[0]):
                        if not col:
                            continue
                        c_lower = str(col).strip().lower()
                        if "description" in c_lower or "particular" in c_lower:
                            desc_idx = col_idx
                        elif "item" in c_lower or "s.no" in c_lower or "sr" in c_lower:
                            item_idx = col_idx
                        elif "qty" in c_lower or "quantity" in c_lower:
                            qty_idx = col_idx
                        elif "unit" in c_lower or "uom" in c_lower:
                            unit_idx = col_idx
                        elif "rate" in c_lower or "unit price" in c_lower:
                            rate_idx = col_idx
                        elif "amount" in c_lower or "total" in c_lower:
                            amount_idx = col_idx
                            
                    # Iterate rows (skip header)
                    for row in table[1:]:
                        if not row or len(row) <= max(item_idx, desc_idx):
                            continue
                            
                        description = str(row[desc_idx]).strip() if row[desc_idx] else ""
                        if not description or description.lower() in ["description", "particulars", "total", "grand total"]:
                            continue
                            
                        item_no = str(row[item_idx]).strip() if row[item_idx] else f"{item_counter}"
                        
                        qty_val = 0.0
                        if qty_idx != -1 and qty_idx < len(row) and row[qty_idx]:
                            qty_str = re.sub(r"[^\d\.]", "", str(row[qty_idx]))
                            qty_val = float(qty_str) if qty_str else 0.0
                            
                        unit_val = str(row[unit_idx]).strip() if (unit_idx != -1 and unit_idx < len(row) and row[unit_idx]) else "LS"
                        
                        rate_val = 0.0
                        if rate_idx != -1 and rate_idx < len(row) and row[rate_idx]:
                            rate_str = re.sub(r"[^\d\.]", "", str(row[rate_idx]))
                            rate_val = float(rate_str) if rate_str else 0.0
                            
                        amount_val = 0.0
                        if amount_idx != -1 and amount_idx < len(row) and row[amount_idx]:
                            amount_str = re.sub(r"[^\d\.]", "", str(row[amount_idx]))
                            amount_val = float(amount_str) if amount_str else 0.0
                        else:
                            amount_val = qty_val * rate_val
                            
                        items.append({
                            "item_no": item_no,
                            "description": description.replace("\n", " "),
                            "quantity": qty_val,
                            "unit": unit_val if unit_val else "LS",
                            "unit_rate": rate_val,
                            "total_amount": amount_val if amount_val > 0 else qty_val * rate_val,
                            "source_file": file_name,
                            "source_row": item_counter
                        })
                        item_counter += 1
                        
        # If no tables found, try simple regex line-by-line parsing
        if not items:
            logger.info("No tables detected in PDF, attempting text regex fallback...")
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                
                # Regex match for common BOQ lines: e.g. "1.1 Excavation in soil m3 250 450 112500"
                pattern = re.compile(r"(\d+[\.\d]*)\s+(.+?)\s+([a-zA-Z\d\/]+)\s+([\d\.\,]+)\s+([\d\.\,]+)\s+([\d\.\,]+)")
                matches = pattern.findall(text)
                
                for idx, match in enumerate(matches):
                    try:
                        item_no, desc, unit, qty_str, rate_str, amt_str = match
                        qty = float(qty_str.replace(",", ""))
                        rate = float(rate_str.replace(",", ""))
                        amt = float(amt_str.replace(",", ""))
                        items.append({
                            "item_no": item_no,
                            "description": desc.strip(),
                            "quantity": qty,
                            "unit": unit.strip(),
                            "unit_rate": rate,
                            "total_amount": amt,
                            "source_file": file_name,
                            "source_row": idx + 1
                        })
                    except Exception:
                        continue
                        
        return items
    except Exception as e:
        logger.error(f"Error parsing PDF BOQ: {e}", exc_info=True)
        raise ValueError(f"Failed to parse PDF file: {e}")
