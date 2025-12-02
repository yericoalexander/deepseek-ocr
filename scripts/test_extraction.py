#!/usr/bin/env python3
"""
Test KTP/Ijazah extraction via DeepSeek-OCR API
Usage: python3 test_extraction.py <image_path> [document_type]
"""

import sys
import json
import base64
import requests
import time
from pathlib import Path
from ktp_cleaner import clean_ktp_output

# API Configuration
API_BASE = "http://localhost:23333/v1"
API_KEY = "dummy"  # Not validated by server

def select_optimal_model(doc_type: str = "ktp", priority: str = "balanced") -> dict:
    """Use model selector to get optimal model"""
    import subprocess
    
    try:
        result = subprocess.run(
            ["python3", "scripts/model_selector.py",
             "--doc-type", doc_type,
             "--priority", priority,
             "--json"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"⚠️  Model selector failed, using default: paddleocr-vl")
            return {
                "recommended_model": {
                    "model_id": "paddleocr-vl",
                    "vram_gb": 9.0,
                    "speed_seconds": 10.0,
                    "accuracy_pct": 100.0
                }
            }
    except Exception as e:
        print(f"⚠️  Error selecting model: {e}")
        return {
            "recommended_model": {
                "model_id": "paddleocr-vl"
            }
        }

def encode_image(image_path: str) -> str:
    """Encode image to base64"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def extract_document(image_path: str, doc_type: str = "ktp", model_id: str = None) -> dict:
    """Extract data from document image"""
    
    # Step 1: Select model if not specified
    if not model_id:
        print(f"🔍 Selecting optimal model for {doc_type.upper()}...")
        model_rec = select_optimal_model(doc_type)
        model_id = model_rec["recommended_model"]["model_id"]
        print(f"✅ Selected: {model_id}")
        print(f"   VRAM: {model_rec['recommended_model'].get('vram_gb', 'N/A')}GB")
        print(f"   Speed: {model_rec['recommended_model'].get('speed_seconds', 'N/A')}s")
        print(f"   Accuracy: {model_rec['recommended_model'].get('accuracy_pct', 'N/A')}%")
        print()
    
    # Step 2: Encode image
    print(f"📷 Encoding image: {image_path}")
    image_base64 = encode_image(image_path)
    image_size_kb = len(image_base64) * 3 / 4 / 1024  # Approximate original size
    print(f"   Size: {image_size_kb:.1f} KB")
    print()
    
    # Step 3: Prepare prompt based on doc type
    prompts = {
        "ktp": """Extract all information from this KTP (Indonesian ID card) and return as JSON with these fields:
- NIK (16 digits)
- Nama (Full name)
- Tempat_Lahir (Place of birth)
- Tanggal_Lahir (Date of birth, format: DD-MM-YYYY)
- Jenis_Kelamin (Gender)
- Alamat (Address)
- RT_RW (RT/RW)
- Kelurahan (Village)
- Kecamatan (District)
- Agama (Religion)
- Status_Perkawinan (Marital status)
- Pekerjaan (Occupation)
- Kewarganegaraan (Nationality)
- Berlaku_Hingga (Valid until)

Return only valid JSON, no additional text.""",
        
        "ijazah": """Extract all information from this diploma/certificate and return as JSON with these fields:
- Nama (Graduate name)
- Institusi (Institution name)
- Program_Studi (Study program)
- Gelar (Degree)
- Tanggal_Lulus (Graduation date)
- IPK (GPA if available)
- Nomor_Ijazah (Certificate number)

Return only valid JSON, no additional text.""",
        
        "sim": """Extract all information from this SIM (Driver's License) and return as JSON with these fields:
- Nomor_SIM (License number)
- Nama (Full name)
- Tempat_Lahir (Place of birth)
- Tanggal_Lahir (Date of birth)
- Jenis_Kelamin (Gender)
- Alamat (Address)
- Pekerjaan (Occupation)
- Berlaku_Hingga (Valid until)
- Golongan (License class)

Return only valid JSON, no additional text."""
    }
    
    prompt = prompts.get(doc_type, prompts["ktp"])
    
    # Step 4: Call API
    print(f"🚀 Calling DeepSeek-OCR API...")
    print(f"   Endpoint: {API_BASE}/chat/completions")
    print(f"   Model: {model_id}")
    print()
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{API_BASE}/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}"
            },
            json={
                "model": model_id,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ],
                "temperature": 0,
                "max_tokens": 2048
            },
            timeout=120
        )
        
        duration = time.time() - start_time
        
        # Step 5: Parse response
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"API error: {response.status_code}",
                "message": response.text
            }
        
        result = response.json()
        
        if "error" in result:
            return {
                "success": False,
                "error": result["error"].get("message", "Unknown error")
            }
        
        content = result["choices"][0]["message"]["content"]
        
        # Clean and structure the output for KTP
        if doc_type == "ktp":
            cleaned_result = clean_ktp_output(content)
            
            return {
                "success": True,
                "model_used": model_id,
                "duration_seconds": duration,
                "image_size_kb": image_size_kb,
                "raw_response": content,
                "extracted_data": cleaned_result['data'],
                "validation": cleaned_result['validation'],
                "fields_count": cleaned_result['fields_extracted']
            }
        
        # Try to parse as JSON for other document types
        try:
            # Extract JSON from markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            extracted_data = json.loads(content)
            
            return {
                "success": True,
                "model_used": model_id,
                "duration_seconds": duration,
                "image_size_kb": image_size_kb,
                "raw_response": content,
                "extracted_data": extracted_data,
                "fields_count": len(extracted_data)
            }
        
        except json.JSONDecodeError:
            # Return raw text if not valid JSON
            return {
                "success": True,
                "model_used": model_id,
                "duration_seconds": duration,
                "image_size_kb": image_size_kb,
                "raw_response": content,
                "extracted_data": None,
                "note": "Response is not valid JSON, returning raw text"
            }
    
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Connection refused",
            "message": "Cannot connect to DeepSeek-OCR server. Check if:\n" +
                      "1. Server is running on localhost:23333\n" +
                      "2. SSH tunnel is active: ssh -L 23333:localhost:23333 rocky37"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def print_result(result: dict):
    """Pretty print extraction result"""
    print("=" * 80)
    print("📊 EXTRACTION RESULT")
    print("=" * 80)
    print()
    
    if not result["success"]:
        print("❌ EXTRACTION FAILED")
        print(f"   Error: {result.get('error', 'Unknown error')}")
        if "message" in result:
            print(f"\n{result['message']}")
        return
    
    print("✅ EXTRACTION SUCCESSFUL")
    print()
    print(f"Model Used: {result['model_used']}")
    print(f"Duration: {result['duration_seconds']:.2f} seconds")
    print(f"Image Size: {result['image_size_kb']:.1f} KB")
    
    if result.get("extracted_data"):
        print(f"Fields Extracted: {result['fields_count']}")
        
        # Show validation if available
        if 'validation' in result:
            validation = result['validation']
            print()
            print("=" * 80)
            print("✅ VALIDATION")
            print("=" * 80)
            print()
            print(f"Status: {'✅ VALID' if validation['is_valid'] else '❌ INVALID'}")
            
            if validation.get('errors'):
                print("\n❌ Errors:")
                for error in validation['errors']:
                    print(f"  - {error}")
            
            if validation.get('warnings'):
                print("\n⚠️  Warnings:")
                for warning in validation['warnings']:
                    print(f"  - {warning}")
        
        print()
        print("=" * 80)
        print("📄 EXTRACTED DATA (Cleaned & Structured)")
        print("=" * 80)
        print()
        print(json.dumps(result["extracted_data"], indent=2, ensure_ascii=False))
    else:
        print()
        print("=" * 80)
        print("📄 RAW RESPONSE (Not JSON)")
        print("=" * 80)
        print()
        print(result["raw_response"])
        if result.get("note"):
            print()
            print(f"⚠️  {result['note']}")
    
    print()
    print("=" * 80)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 test_extraction.py <image_path> [document_type]")
        print()
        print("Document types:")
        print("  - ktp (default): Indonesian ID card")
        print("  - ijazah: Diploma/Certificate")
        print("  - sim: Driver's License")
        print()
        print("Examples:")
        print("  python3 test_extraction.py ktp.jpg")
        print("  python3 test_extraction.py diploma.png ijazah")
        print("  python3 test_extraction.py sim.jpg sim")
        sys.exit(1)
    
    image_path = sys.argv[1]
    doc_type = sys.argv[2] if len(sys.argv) > 2 else "ktp"
    
    # Validate image exists
    if not Path(image_path).exists():
        print(f"❌ Error: Image not found: {image_path}")
        sys.exit(1)
    
    # Validate doc type
    valid_types = ["ktp", "ijazah", "sim", "sertifikat", "passport"]
    if doc_type not in valid_types:
        print(f"⚠️  Unknown document type: {doc_type}")
        print(f"   Valid types: {', '.join(valid_types)}")
        print(f"   Using default: ktp")
        doc_type = "ktp"
    
    print()
    print("🔍 DeepSeek-OCR Extraction Test")
    print("=" * 80)
    print(f"Image: {image_path}")
    print(f"Document Type: {doc_type.upper()}")
    print("=" * 80)
    print()
    
    # Extract
    result = extract_document(image_path, doc_type)
    
    # Print result
    print_result(result)
    
    # Save to file
    output_file = Path(image_path).stem + "_extracted.json"
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Result saved to: {output_file}")
    print()

if __name__ == "__main__":
    main()
