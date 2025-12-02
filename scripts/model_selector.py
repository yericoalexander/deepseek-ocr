#!/usr/bin/env python3
"""
Intelligent Model Selector for DeepSeek-OCR
Auto-select optimal model based on document type, server resources, and requirements

Usage:
    python3 model_selector.py --doc-type ktp
    python3 model_selector.py --doc-type ijazah --vram 8
    python3 model_selector.py --analyze image.jpg
"""

import argparse
import json
import subprocess
import sys
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class DocumentType(Enum):
    """Supported document types"""
    KTP = "ktp"
    SIM = "sim"
    IJAZAH = "ijazah"
    SERTIFIKAT = "sertifikat"
    PASSPORT = "passport"
    KARTU_KELUARGA = "kk"
    NPWP = "npwp"
    AKTA = "akta"
    INVOICE = "invoice"
    RECEIPT = "receipt"
    FORM = "form"
    UNKNOWN = "unknown"

@dataclass
class ModelConfig:
    """Model configuration with performance characteristics"""
    model_id: str
    vram_gb: float
    speed_seconds: float
    accuracy_pct: float
    best_for: list
    notes: str = ""
    
class ModelSelector:
    """Intelligent model selection based on document type and constraints"""
    
    # Model database with tested/estimated performance
    MODELS = {
        "paddleocr-vl": ModelConfig(
            model_id="paddleocr-vl",
            vram_gb=9.0,
            speed_seconds=10.0,
            accuracy_pct=100.0,
            best_for=["ktp", "sim", "kk", "akta"],
            notes="Tested & proven. Best for Indonesian ID documents. No duplicates."
        ),
        "paddleocr-vl-q4k": ModelConfig(
            model_id="paddleocr-vl-q4k",
            vram_gb=2.5,
            speed_seconds=6.0,
            accuracy_pct=95.0,
            best_for=["ktp", "sim", "npwp", "receipt"],
            notes="Fastest & lightest. Good for batch processing. Slight accuracy drop."
        ),
        "paddleocr-vl-q6k": ModelConfig(
            model_id="paddleocr-vl-q6k",
            vram_gb=4.5,
            speed_seconds=7.5,
            accuracy_pct=98.0,
            best_for=["ijazah", "sertifikat", "passport"],
            notes="Sweet spot for text-heavy documents. Balanced performance."
        ),
        "paddleocr-vl-q8k": ModelConfig(
            model_id="paddleocr-vl-q8k",
            vram_gb=6.5,
            speed_seconds=9.0,
            accuracy_pct=99.0,
            best_for=["ijazah", "sertifikat"],
            notes="Near-FP16 quality. Good compromise."
        ),
        "deepseek-ocr": ModelConfig(
            model_id="deepseek-ocr",
            vram_gb=13.0,
            speed_seconds=18.0,
            accuracy_pct=100.0,
            best_for=[],  # Not recommended due to duplicate issue
            notes="⚠️ AVOID: Duplicate output issue. Use paddleocr-vl instead."
        ),
        "deepseek-ocr-q4k": ModelConfig(
            model_id="deepseek-ocr-q4k",
            vram_gb=5.0,
            speed_seconds=12.0,
            accuracy_pct=0.0,  # Known issue
            best_for=[],
            notes="❌ AVOID: Empty response bug. Do not use."
        ),
        "deepseek-ocr-q6k": ModelConfig(
            model_id="deepseek-ocr-q6k",
            vram_gb=7.0,
            speed_seconds=14.0,
            accuracy_pct=98.0,
            best_for=["passport"],  # Only if paddleocr fails
            notes="⚠️ Use only as fallback. paddleocr-vl preferred."
        ),
        "dots-ocr-q4k": ModelConfig(
            model_id="dots-ocr-q4k",
            vram_gb=18.0,
            speed_seconds=35.0,
            accuracy_pct=95.0,
            best_for=["invoice", "form"],
            notes="For complex layouts with tables. Includes bounding boxes."
        ),
    }
    
    # Document type to recommended models mapping
    DOC_TYPE_MAPPING = {
        DocumentType.KTP: ("paddleocr-vl", "paddleocr-vl-q4k"),
        DocumentType.SIM: ("paddleocr-vl", "paddleocr-vl-q4k"),
        DocumentType.IJAZAH: ("paddleocr-vl-q6k", "paddleocr-vl"),
        DocumentType.SERTIFIKAT: ("paddleocr-vl-q6k", "paddleocr-vl-q8k"),
        DocumentType.PASSPORT: ("paddleocr-vl-q6k", "deepseek-ocr-q6k"),
        DocumentType.KARTU_KELUARGA: ("paddleocr-vl", "paddleocr-vl-q6k"),
        DocumentType.NPWP: ("paddleocr-vl-q4k", "paddleocr-vl"),
        DocumentType.AKTA: ("paddleocr-vl", "paddleocr-vl-q6k"),
        DocumentType.INVOICE: ("dots-ocr-q4k", "paddleocr-vl-q6k"),
        DocumentType.RECEIPT: ("paddleocr-vl-q4k", "paddleocr-vl"),
        DocumentType.FORM: ("dots-ocr-q4k", "paddleocr-vl-q6k"),
        DocumentType.UNKNOWN: ("paddleocr-vl", "paddleocr-vl-q4k"),
    }
    
    def __init__(self, available_vram_gb: Optional[float] = None):
        """
        Initialize model selector
        
        Args:
            available_vram_gb: Available VRAM in GB. If None, will try to detect.
        """
        self.available_vram = available_vram_gb or self._detect_vram()
        
    def _detect_vram(self) -> float:
        """Detect available VRAM using nvidia-smi"""
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=memory.total', '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                vram_mb = float(result.stdout.strip().split('\n')[0])
                return vram_mb / 1024.0  # Convert to GB
        except:
            pass
        
        # Default to conservative 16GB if cannot detect
        return 16.0
    
    def select_model(
        self, 
        doc_type: DocumentType,
        priority: str = "balanced",  # "accuracy", "speed", "memory"
        batch_mode: bool = False
    ) -> Tuple[str, ModelConfig, str]:
        """
        Select optimal model for document type
        
        Args:
            doc_type: Type of document to OCR
            priority: Optimization priority (accuracy/speed/memory)
            batch_mode: Whether processing multiple documents
            
        Returns:
            Tuple of (model_id, config, reason)
        """
        # Get candidate models for this document type
        primary, fallback = self.DOC_TYPE_MAPPING.get(
            doc_type, 
            ("paddleocr-vl", "paddleocr-vl-q4k")
        )
        
        candidates = [primary, fallback]
        
        # Filter by available VRAM
        valid_models = [
            (name, self.MODELS[name]) 
            for name in candidates 
            if self.MODELS[name].vram_gb <= self.available_vram
        ]
        
        if not valid_models:
            # Fallback to smallest model
            model_name = "paddleocr-vl-q4k"
            config = self.MODELS[model_name]
            reason = f"⚠️ Insufficient VRAM ({self.available_vram:.1f}GB). Using lightest model."
            return model_name, config, reason
        
        # Apply priority selection
        if priority == "speed" or batch_mode:
            # Sort by speed (fastest first)
            valid_models.sort(key=lambda x: x[1].speed_seconds)
            model_name, config = valid_models[0]
            reason = f"✅ Selected for SPEED: {config.speed_seconds}s per doc"
            
        elif priority == "memory":
            # Sort by VRAM usage (lowest first)
            valid_models.sort(key=lambda x: x[1].vram_gb)
            model_name, config = valid_models[0]
            reason = f"✅ Selected for MEMORY: {config.vram_gb:.1f}GB VRAM"
            
        elif priority == "accuracy":
            # Sort by accuracy (highest first)
            valid_models.sort(key=lambda x: x[1].accuracy_pct, reverse=True)
            model_name, config = valid_models[0]
            reason = f"✅ Selected for ACCURACY: {config.accuracy_pct:.0f}%"
            
        else:  # balanced
            # Use primary recommendation if fits in memory
            model_name, config = valid_models[0]
            reason = f"✅ Best for {doc_type.value.upper()}: {config.notes}"
        
        return model_name, config, reason
    
    def get_recommendation_report(
        self, 
        doc_type: DocumentType,
        priority: str = "balanced"
    ) -> Dict:
        """
        Generate detailed recommendation report
        
        Returns:
            Dictionary with model selection details and alternatives
        """
        model_id, config, reason = self.select_model(doc_type, priority)
        
        # Get alternatives
        alternatives = []
        for name, model_config in self.MODELS.items():
            if name != model_id and model_config.vram_gb <= self.available_vram:
                if doc_type.value in model_config.best_for or not model_config.best_for:
                    alternatives.append({
                        "model_id": name,
                        "vram_gb": model_config.vram_gb,
                        "speed_seconds": model_config.speed_seconds,
                        "accuracy_pct": model_config.accuracy_pct,
                        "notes": model_config.notes
                    })
        
        # Sort alternatives by accuracy
        alternatives.sort(key=lambda x: x['accuracy_pct'], reverse=True)
        
        return {
            "document_type": doc_type.value,
            "recommended_model": {
                "model_id": model_id,
                "vram_gb": config.vram_gb,
                "speed_seconds": config.speed_seconds,
                "accuracy_pct": config.accuracy_pct,
                "notes": config.notes,
                "reason": reason
            },
            "server_info": {
                "available_vram_gb": self.available_vram,
                "sufficient": config.vram_gb <= self.available_vram
            },
            "alternatives": alternatives[:3],  # Top 3 alternatives
            "optimization_tips": self._get_optimization_tips(doc_type, config)
        }
    
    def _get_optimization_tips(
        self, 
        doc_type: DocumentType, 
        config: ModelConfig
    ) -> list:
        """Generate optimization tips based on selection"""
        tips = []
        
        if config.vram_gb > self.available_vram * 0.8:
            tips.append("⚠️ Model using >80% VRAM. Consider smaller variant for batch processing.")
        
        if config.speed_seconds > 15:
            tips.append("⏱️ Slow model. Use q4k variant for faster processing.")
        
        if config.accuracy_pct < 100 and doc_type in [DocumentType.KTP, DocumentType.PASSPORT]:
            tips.append("💡 For critical documents, consider higher quality model if VRAM allows.")
        
        if doc_type == DocumentType.IJAZAH and config.model_id == "paddleocr-vl":
            tips.append("💡 Consider paddleocr-vl-q6k for better speed/memory on text-heavy docs.")
        
        if not tips:
            tips.append("✅ Optimal model selected. No optimization needed.")
        
        return tips

def parse_document_type(doc_type_str: str) -> DocumentType:
    """Parse document type from string"""
    doc_type_str = doc_type_str.lower().strip()
    
    # Map aliases
    aliases = {
        'ktp': DocumentType.KTP,
        'e-ktp': DocumentType.KTP,
        'ektp': DocumentType.KTP,
        'sim': DocumentType.SIM,
        'ijazah': DocumentType.IJAZAH,
        'diploma': DocumentType.IJAZAH,
        'certificate': DocumentType.SERTIFIKAT,
        'sertifikat': DocumentType.SERTIFIKAT,
        'passport': DocumentType.PASSPORT,
        'paspor': DocumentType.PASSPORT,
        'kk': DocumentType.KARTU_KELUARGA,
        'kartu-keluarga': DocumentType.KARTU_KELUARGA,
        'npwp': DocumentType.NPWP,
        'akta': DocumentType.AKTA,
        'invoice': DocumentType.INVOICE,
        'receipt': DocumentType.RECEIPT,
        'form': DocumentType.FORM,
    }
    
    return aliases.get(doc_type_str, DocumentType.UNKNOWN)

def main():
    parser = argparse.ArgumentParser(
        description="Intelligent Model Selector for DeepSeek-OCR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Select model for KTP
  python3 model_selector.py --doc-type ktp
  
  # Select model for Ijazah with 8GB VRAM limit
  python3 model_selector.py --doc-type ijazah --vram 8
  
  # Select fastest model for batch processing
  python3 model_selector.py --doc-type ktp --priority speed --batch
  
  # Get JSON output for API integration
  python3 model_selector.py --doc-type ijazah --json
        """
    )
    
    parser.add_argument(
        '--doc-type',
        required=True,
        help='Document type: ktp, sim, ijazah, sertifikat, passport, kk, npwp, etc.'
    )
    
    parser.add_argument(
        '--vram',
        type=float,
        help='Available VRAM in GB (auto-detect if not specified)'
    )
    
    parser.add_argument(
        '--priority',
        choices=['accuracy', 'speed', 'memory', 'balanced'],
        default='balanced',
        help='Optimization priority (default: balanced)'
    )
    
    parser.add_argument(
        '--batch',
        action='store_true',
        help='Optimize for batch processing (prioritizes speed)'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON'
    )
    
    parser.add_argument(
        '--list-models',
        action='store_true',
        help='List all available models with specs'
    )
    
    args = parser.parse_args()
    
    # List models if requested
    if args.list_models:
        print("\n📊 Available Models:\n")
        for name, config in ModelSelector.MODELS.items():
            status = "✅" if config.accuracy_pct > 90 else "⚠️"
            print(f"{status} {name}")
            print(f"   VRAM: {config.vram_gb:.1f}GB | Speed: {config.speed_seconds:.1f}s | Accuracy: {config.accuracy_pct:.0f}%")
            print(f"   Best for: {', '.join(config.best_for) or 'N/A'}")
            print(f"   Notes: {config.notes}")
            print()
        return
    
    # Parse document type
    doc_type = parse_document_type(args.doc_type)
    
    if doc_type == DocumentType.UNKNOWN:
        print(f"⚠️ Unknown document type: {args.doc_type}", file=sys.stderr)
        print("Supported types: ktp, sim, ijazah, sertifikat, passport, kk, npwp, akta, invoice, receipt, form", file=sys.stderr)
        sys.exit(1)
    
    # Initialize selector
    selector = ModelSelector(available_vram_gb=args.vram)
    
    # Get recommendation
    report = selector.get_recommendation_report(
        doc_type=doc_type,
        priority=args.priority if not args.batch else "speed"
    )
    
    # Output
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("\n" + "="*60)
        print(f"🎯 Model Recommendation for {doc_type.value.upper()}")
        print("="*60)
        print()
        
        rec = report['recommended_model']
        print(f"✅ Recommended Model: {rec['model_id']}")
        print(f"   VRAM Required: {rec['vram_gb']:.1f}GB")
        print(f"   Expected Speed: {rec['speed_seconds']:.1f}s per document")
        print(f"   Accuracy: {rec['accuracy_pct']:.0f}%")
        print(f"   Reason: {rec['reason']}")
        print(f"   Notes: {rec['notes']}")
        print()
        
        server = report['server_info']
        status = "✅" if server['sufficient'] else "⚠️"
        print(f"{status} Server VRAM: {server['available_vram_gb']:.1f}GB available")
        print()
        
        if report['alternatives']:
            print("🔄 Alternative Models:")
            for i, alt in enumerate(report['alternatives'], 1):
                print(f"   {i}. {alt['model_id']}")
                print(f"      VRAM: {alt['vram_gb']:.1f}GB | Speed: {alt['speed_seconds']:.1f}s | Accuracy: {alt['accuracy_pct']:.0f}%")
            print()
        
        if report['optimization_tips']:
            print("💡 Optimization Tips:")
            for tip in report['optimization_tips']:
                print(f"   {tip}")
            print()
        
        print("="*60)
        print()
        print("📱 Usage in OpenWebUI:")
        print(f"   1. Select model: {rec['model_id']}")
        print(f"   2. Upload {doc_type.value.upper()}")
        print("   3. Extract text")
        print()

if __name__ == '__main__':
    main()
