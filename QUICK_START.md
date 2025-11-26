# 🚀 Quick Reference - DeepSeek-OCR CLI

## Setup Awal (Satu Kali Saja)

```bash
# Tambahkan Rust ke PATH secara permanen
echo 'source "$HOME/.cargo/env"' >> ~/.zshrc
source ~/.zshrc
```

## Cara Menggunakan

### Method 1: Langsung (Recommended setelah setup PATH)
```bash
deepseek-ocr-cli \
  --prompt "<image>\n<|grounding|>Convert to JSON." \
  --image /path/to/image.jpg \
  --max-new-tokens 8192 \
  --device metal \
  --dtype f16
```

### Method 2: Menggunakan Helper Script (Tanpa setup PATH)
```bash
cd /Users/yericoalexander/Documents/PROJECT-SMARTELCO/deepseek-ocr.rs
./run-ocr.sh \
  --prompt "<image>\n<|grounding|>Convert to JSON." \
  --image /path/to/image.jpg \
  --max-new-tokens 8192 \
  --device metal \
  --dtype f16
```

## Contoh Perintah Client

```bash
deepseek-ocr-cli \
  --prompt "<image>\n<|grounding|>Convert this timesheet to json format." \
  --image /Users/subhanfauzi/Downloads/timesheet.jpg \
  --max-new-tokens 8192 \
  --device metal \
  --dtype f16
```

## Parameter Penting

| Parameter | Nilai | Keterangan |
|-----------|-------|------------|
| `--device` | `metal` | GPU Apple Silicon (CEPAT) |
| `--device` | `cpu` | CPU saja (LAMBAT) |
| `--dtype` | `f16` | 16-bit (Cepat, hemat memory) |
| `--dtype` | `f32` | 32-bit (Lebih akurat tapi lambat) |
| `--max-new-tokens` | `2048` | Output pendek |
| `--max-new-tokens` | `8192` | Output panjang (tabel besar) |
| `--quiet` | - | Hanya tampilkan hasil, tanpa log |

## Tips & Tricks

### Quiet Mode (Hanya Output)
```bash
deepseek-ocr-cli --quiet \
  --prompt "<image>\nExtract text." \
  --image doc.jpg \
  --device metal --dtype f16
```

### Multiple Images
```bash
deepseek-ocr-cli \
  --prompt "<image>\nPage 1\n\n<image>\nPage 2" \
  --image page1.jpg \
  --image page2.jpg \
  --device metal --dtype f16
```

### Save Output to File
```bash
deepseek-ocr-cli --quiet \
  --prompt "<image>\nConvert to JSON." \
  --image data.jpg \
  --device metal --dtype f16 > output.json
```

## Troubleshooting

**Command not found?**
```bash
source "$HOME/.cargo/env"
```

**Download model pertama kali:** Tunggu 5-15 menit (tergantung internet)

**Out of memory:** Gunakan `--max-new-tokens 2048` atau lebih kecil

**Lambat:** Pastikan gunakan `--device metal --dtype f16`

## Info Model

- **Location:** `~/Library/Caches/deepseek-ocr/models/deepseek-ocr/`
- **Size:** ~6.3GB
- **RAM Usage:** ~13GB saat running
- **First Run:** Auto-download dari Hugging Face/ModelScope

## Check Installation

```bash
# Check CLI version
deepseek-ocr-cli --version

# Check help
deepseek-ocr-cli --help

# Check Rust
rustc --version
cargo --version
```

---

**Last Updated:** November 26, 2025
