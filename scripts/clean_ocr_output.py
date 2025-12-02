#!/usr/bin/env python3
"""
Post-Processing Script untuk Clean OCR Output
Untuk Grace - Remove XML tags dan format output KTP

Usage:
    python3 clean_ocr_output.py < raw_output.txt
    atau
    echo "raw text" | python3 clean_ocr_output.py
"""

import sys
import re
from typing import Dict, List

def clean_xml_tags(text: str) -> str:
    """Remove XML-like tags from paddleocr-vl output"""
    # Remove common tags
    text = re.sub(r'<fcel>', '', text)
    text = re.sub(r'<lcel>', '', text)
    text = re.sub(r'<nl>', '\n', text)
    text = re.sub(r'<.*?>', '', text)  # Remove any other tags
    return text

def remove_duplicates(lines: List[str]) -> List[str]:
    """Remove consecutive duplicate lines"""
    cleaned = []
    prev = None
    for line in lines:
        line = line.strip()
        if line and line != prev:
            cleaned.append(line)
            prev = line
    return cleaned

def parse_ktp_fields(text: str) -> Dict[str, str]:
    """Parse KTP text into structured fields"""
    fields = {}
    
    # Patterns for KTP fields
    patterns = {
        'provinsi': r'(?:PROVINSI|Provinsi)\s+([A-Z\s]+)',
        'kota': r'(?:KOTA|KABUPATEN|Kota|Kabupaten)\s+([A-Z\s]+)',
        'nik': r'(?:NIK|Nik)\s*:?\s*(\d{16})',
        'nama': r'(?:Nama|NAMA)\s*:?\s*([A-Z\s]+)',
        'tempat_lahir': r'(?:Tempat.*Lahir|TEMPAT.*LAHIR)\s*:?\s*([A-Za-z\s]+),',
        'tanggal_lahir': r',\s*(\d{2}-\d{2}-\d{4})',
        'jenis_kelamin': r'(?:Jenis Kelamin|JENIS KELAMIN)\s*:?\s*(LAKI-LAKI|PEREMPUAN)',
        'gol_darah': r'(?:Gol.*Darah|GOL.*DARAH)\s*:?\s*([ABO-]+)',
        'alamat': r'(?:Alamat|ALAMAT)\s*:?\s*([A-Z0-9\s,\.]+)',
        'rt_rw': r'(?:RT/RW|Rt/Rw)\s*:?\s*(\d{3}/\d{3})',
        'kelurahan': r'(?:Kel/Desa|KEL/DESA)\s*:?\s*([A-Z\s]+)',
        'kecamatan': r'(?:Kecamatan|KECAMATAN)\s*:?\s*([A-Z\s]+)',
        'agama': r'(?:Agama|AGAMA)\s*:?\s*(ISLAM|KRISTEN|KATOLIK|HINDU|BUDDHA|KONGHUCU)',
        'status_kawin': r'(?:Status Perkawinan|STATUS PERKAWINAN)\s*:?\s*(KAWIN|BELUM KAWIN|CERAI)',
        'pekerjaan': r'(?:Pekerjaan|PEKERJAAN)\s*:?\s*([A-Z\s/]+)',
        'kewarganegaraan': r'(?:Kewarganegaraan|KEWARGANEGARAAN)\s*:?\s*(WNI|WNA)',
        'berlaku': r'(?:Berlaku Hingga|BERLAKU HINGGA)\s*:?\s*([A-Z\s]+|\d{2}-\d{2}-\d{4})',
    }
    
    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            fields[field] = match.group(1).strip()
    
    return fields

def format_ktp_output(fields: Dict[str, str]) -> str:
    """Format KTP fields into readable output"""
    output = []
    output.append("=" * 60)
    output.append("           KARTU TANDA PENDUDUK (KTP)")
    output.append("=" * 60)
    output.append("")
    
    if 'provinsi' in fields:
        output.append(f"Provinsi: {fields['provinsi']}")
    if 'kota' in fields:
        output.append(f"Kota/Kabupaten: {fields['kota']}")
    
    output.append("")
    output.append("-" * 60)
    
    if 'nik' in fields:
        output.append(f"NIK                 : {fields['nik']}")
    if 'nama' in fields:
        output.append(f"Nama                : {fields['nama']}")
    if 'tempat_lahir' in fields and 'tanggal_lahir' in fields:
        output.append(f"Tempat/Tgl Lahir    : {fields['tempat_lahir']}, {fields['tanggal_lahir']}")
    elif 'tempat_lahir' in fields:
        output.append(f"Tempat Lahir        : {fields['tempat_lahir']}")
    elif 'tanggal_lahir' in fields:
        output.append(f"Tanggal Lahir       : {fields['tanggal_lahir']}")
    
    if 'jenis_kelamin' in fields:
        jk = fields['jenis_kelamin']
        gd = fields.get('gol_darah', '-')
        output.append(f"Jenis Kelamin       : {jk:<20} Gol. Darah: {gd}")
    
    if 'alamat' in fields:
        output.append(f"Alamat              : {fields['alamat']}")
    if 'rt_rw' in fields:
        output.append(f"    RT/RW           : {fields['rt_rw']}")
    if 'kelurahan' in fields:
        output.append(f"    Kel/Desa        : {fields['kelurahan']}")
    if 'kecamatan' in fields:
        output.append(f"    Kecamatan       : {fields['kecamatan']}")
    
    if 'agama' in fields:
        output.append(f"Agama               : {fields['agama']}")
    if 'status_kawin' in fields:
        output.append(f"Status Perkawinan   : {fields['status_kawin']}")
    if 'pekerjaan' in fields:
        output.append(f"Pekerjaan           : {fields['pekerjaan']}")
    if 'kewarganegaraan' in fields:
        output.append(f"Kewarganegaraan     : {fields['kewarganegaraan']}")
    if 'berlaku' in fields:
        output.append(f"Berlaku Hingga      : {fields['berlaku']}")
    
    output.append("")
    output.append("=" * 60)
    
    return "\n".join(output)

def format_as_json(fields: Dict[str, str]) -> str:
    """Format KTP fields as JSON"""
    import json
    return json.dumps(fields, indent=2, ensure_ascii=False)

def main():
    # Read input from stdin or file
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            raw_text = f.read()
    else:
        raw_text = sys.stdin.read()
    
    # Step 1: Clean XML tags
    cleaned_text = clean_xml_tags(raw_text)
    
    # Step 2: Remove duplicate lines
    lines = cleaned_text.split('\n')
    unique_lines = remove_duplicates(lines)
    cleaned_text = '\n'.join(unique_lines)
    
    # Step 3: Parse into structured fields
    fields = parse_ktp_fields(cleaned_text)
    
    # Step 4: Format output
    print("\n📋 CLEANED TEXT OUTPUT:")
    print("-" * 60)
    print(cleaned_text)
    print()
    
    if fields:
        print("\n📊 STRUCTURED KTP DATA:")
        print(format_ktp_output(fields))
        
        print("\n💾 JSON FORMAT:")
        print(format_as_json(fields))
    else:
        print("\n⚠️  No KTP fields detected. Raw cleaned output shown above.")

if __name__ == '__main__':
    main()
