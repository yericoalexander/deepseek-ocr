#!/usr/bin/env python3
"""
Clean and structure OCR output from DeepSeek-OCR
Converts messy text output to clean JSON format
"""

import re
import json
from typing import Dict, List, Optional

class KTPCleaner:
    """Clean and structure KTP extraction output"""
    
    # Field mappings (various formats → standard field name)
    FIELD_MAPPINGS = {
        # NIK variations
        r'NIK\s*[:\-]?\s*': 'NIK',
        r'Nomor\s*Induk\s*Kependudukan\s*[:\-]?\s*': 'NIK',
        
        # Name variations
        r'Name\s*[:\-]?\s*': 'Nama',
        r'Nama\s*[:\-]?\s*': 'Nama',
        r'NAMA\s*[:\-]?\s*': 'Nama',
        
        # Birth place/date
        r'Tempat\s*[/]?\s*Tgl\s*Lahir\s*[:\-]?\s*': 'Tempat_Tanggal_Lahir',
        r'Tempat/Tanggal\s*Lahir\s*[:\-]?\s*': 'Tempat_Tanggal_Lahir',
        r'Tempat\s*Lahir\s*[:\-]?\s*': 'Tempat_Lahir',
        r'Tanggal\s*Lahir\s*[:\-]?\s*': 'Tanggal_Lahir',
        
        # Gender
        r'Jenis\s*Kelamin\s*[:\-]?\s*': 'Jenis_Kelamin',
        r'Gender\s*[:\-]?\s*': 'Jenis_Kelamin',
        
        # Address
        r'Alamat\s*[:\-]?\s*': 'Alamat',
        
        # RT/RW
        r'RT\s*[/]?\s*RW\s*[:\-]?\s*': 'RT_RW',
        
        # Village
        r'Kel\s*[/]?\s*Desa\s*[:\-]?\s*': 'Kelurahan',
        r'Kelurahan\s*[:\-]?\s*': 'Kelurahan',
        
        # District
        r'Kecamatan\s*[:\-]?\s*': 'Kecamatan',
        
        # Religion
        r'Agama\s*[:\-]?\s*': 'Agama',
        
        # Marital status
        r'Status\s*Perkawinan\s*[:\-]?\s*': 'Status_Perkawinan',
        
        # Occupation
        r'Pekerjaan\s*[:\-]?\s*': 'Pekerjaan',
        
        # Nationality
        r'Kewarganegaraan\s*[:\-]?\s*': 'Kewarganegaraan',
        
        # Valid until
        r'Berlaku\s*Hingga\s*[:\-]?\s*': 'Berlaku_Hingga',
        
        # City
        r'KOTA\s*[:\-]?\s*': 'Kota',
        r'Kota\s*[:\-]?\s*': 'Kota',
    }
    
    def clean(self, raw_text: str) -> Dict[str, str]:
        """Clean and structure raw OCR text"""
        
        # Split into lines
        lines = raw_text.strip().split('\n')
        
        # Extract fields
        data = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Try to match with field mappings
            for pattern, field_name in self.FIELD_MAPPINGS.items():
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    # Extract value (everything after the pattern)
                    value = re.sub(pattern, '', line, flags=re.IGNORECASE).strip()
                    value = value.lstrip(':- ').strip()
                    
                    if value:
                        data[field_name] = value
                    break
        
        # Post-process specific fields
        data = self._post_process(data)
        
        return data
    
    def _post_process(self, data: Dict[str, str]) -> Dict[str, str]:
        """Post-process extracted data"""
        
        # Split combined birth place/date if needed
        if 'Tempat_Tanggal_Lahir' in data and 'Tempat_Lahir' not in data:
            birth_info = data['Tempat_Tanggal_Lahir']
            # Try to split by comma or date pattern
            match = re.match(r'([A-Z\s]+),?\s*(\d{2}-\d{2}-\d{4})', birth_info)
            if match:
                data['Tempat_Lahir'] = match.group(1).strip()
                data['Tanggal_Lahir'] = match.group(2).strip()
                del data['Tempat_Tanggal_Lahir']
        
        # Clean NIK (remove spaces, keep only digits)
        if 'NIK' in data:
            data['NIK'] = re.sub(r'\D', '', data['NIK'])
        
        # Normalize gender
        if 'Jenis_Kelamin' in data:
            gender = data['Jenis_Kelamin'].upper()
            if 'LAKI' in gender or 'MALE' in gender or 'L' == gender:
                data['Jenis_Kelamin'] = 'LAKI-LAKI'
            elif 'PEREMPUAN' in gender or 'FEMALE' in gender or 'P' == gender:
                data['Jenis_Kelamin'] = 'PEREMPUAN'
        
        # Clean RT/RW format
        if 'RT_RW' in data:
            rt_rw = data['RT_RW']
            # Normalize format to 000/000
            match = re.match(r'(\d+)\s*/\s*(\d+)', rt_rw)
            if match:
                rt = match.group(1).zfill(3)
                rw = match.group(2).zfill(3)
                data['RT_RW'] = f"{rt}/{rw}"
        
        # Uppercase certain fields
        uppercase_fields = ['Agama', 'Status_Perkawinan', 'Kewarganegaraan', 'Berlaku_Hingga']
        for field in uppercase_fields:
            if field in data:
                data[field] = data[field].upper()
        
        return data
    
    def validate(self, data: Dict[str, str]) -> Dict[str, any]:
        """Validate extracted KTP data"""
        
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Required fields
        required_fields = [
            'NIK', 'Nama', 'Tempat_Lahir', 'Tanggal_Lahir',
            'Jenis_Kelamin', 'Alamat', 'Agama', 'Kewarganegaraan'
        ]
        
        for field in required_fields:
            if field not in data or not data[field]:
                validation['errors'].append(f"Missing required field: {field}")
                validation['is_valid'] = False
        
        # Validate NIK (must be 16 digits)
        if 'NIK' in data:
            if len(data['NIK']) != 16:
                validation['errors'].append(f"NIK must be 16 digits, got {len(data['NIK'])}")
                validation['is_valid'] = False
            elif not data['NIK'].isdigit():
                validation['errors'].append("NIK must contain only digits")
                validation['is_valid'] = False
        
        # Validate date format
        if 'Tanggal_Lahir' in data:
            if not re.match(r'\d{2}-\d{2}-\d{4}', data['Tanggal_Lahir']):
                validation['warnings'].append(f"Date format should be DD-MM-YYYY, got: {data['Tanggal_Lahir']}")
        
        # Validate gender
        if 'Jenis_Kelamin' in data:
            if data['Jenis_Kelamin'] not in ['LAKI-LAKI', 'PEREMPUAN']:
                validation['warnings'].append(f"Unexpected gender value: {data['Jenis_Kelamin']}")
        
        return validation


def clean_ktp_output(raw_text: str) -> Dict[str, any]:
    """
    Clean and structure KTP OCR output
    
    Args:
        raw_text: Raw OCR output text
    
    Returns:
        Dict with cleaned data, validation, and metadata
    """
    
    cleaner = KTPCleaner()
    
    # Clean and structure
    cleaned_data = cleaner.clean(raw_text)
    
    # Validate
    validation = cleaner.validate(cleaned_data)
    
    return {
        'data': cleaned_data,
        'validation': validation,
        'fields_extracted': len(cleaned_data),
        'raw_text': raw_text
    }


def main():
    """CLI for testing"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 ktp_cleaner.py <raw_text_file>")
        print("\nExample:")
        print("  python3 ktp_cleaner.py ktp_output.txt")
        sys.exit(1)
    
    # Read raw text
    with open(sys.argv[1], 'r') as f:
        raw_text = f.read()
    
    # Clean and structure
    result = clean_ktp_output(raw_text)
    
    # Print result
    print("=" * 80)
    print("📊 CLEANED KTP DATA")
    print("=" * 80)
    print()
    print(json.dumps(result['data'], indent=2, ensure_ascii=False))
    print()
    print("=" * 80)
    print("✅ VALIDATION")
    print("=" * 80)
    print()
    print(f"Status: {'✅ VALID' if result['validation']['is_valid'] else '❌ INVALID'}")
    print(f"Fields Extracted: {result['fields_extracted']}")
    
    if result['validation']['errors']:
        print("\n❌ Errors:")
        for error in result['validation']['errors']:
            print(f"  - {error}")
    
    if result['validation']['warnings']:
        print("\n⚠️  Warnings:")
        for warning in result['validation']['warnings']:
            print(f"  - {warning}")
    
    print()
    
    # Save cleaned output
    output_file = sys.argv[1].replace('.txt', '_cleaned.json')
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved to: {output_file}")


if __name__ == '__main__':
    main()
