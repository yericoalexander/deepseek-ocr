# 🚀 Setup DeepSeek-OCR di Rocky Linux Server

## 📋 Panduan untuk Client (Gracia Rizka Pasfica)

Dokumen ini menjelaskan cara mengatasi error **"500: failed to load language model"** dan **"out of memory"** yang terjadi di server OpenWebUI Anda.

---

## ❌ Problem Analysis

Dari screenshot error yang Anda berikan:

```
500: failed to load language model
```

**Root Cause:**
- Model `deepseek-ocr` (full precision) membutuhkan **13GB+ VRAM**
- Server Rocky Linux Anda kehabisan memory (terlihat dari nvtop - GPU memory naik tapi tidak cukup)
- OpenWebUI gagal load model karena insufficient memory

---

## ✅ Solusi: Gunakan Model Quantized

### Option 1: PaddleOCR-VL Quantized (RECOMMENDED)

Model ini **lebih ringan** dan **sangat bagus untuk KTP Indonesia**.

**Memory requirement:**
- `paddleocr-vl:q4k` → **2-3GB VRAM** ✅ (Paling ringan)
- `paddleocr-vl:q8` → **4-5GB VRAM**
- `paddleocr-vl` (full) → **8GB+ VRAM**

### Option 2: DeepSeek-OCR Quantized

Jika ingin tetap pakai DeepSeek:
- `deepseek-ocr:q4k` → **4-6GB VRAM**
- `deepseek-ocr:q8` → **7-9GB VRAM**

---

## 🔧 Step-by-Step Setup di Server Rocky

### 1. SSH ke Server Rocky Linux

```bash
ssh rocky@your-server-ip
```

### 2. Check Available Memory

```bash
# Check RAM
free -h

# Check GPU VRAM (jika pakai GPU)
nvtop
# atau
nvidia-smi
```

**Pastikan minimal ada 4GB free memory!**

### 3. Masuk ke Docker Container OpenWebUI

```bash
# List running containers
docker ps

# Masuk ke container (sesuaikan nama container)
docker exec -it open-webui bash
```

### 4. Check Model yang Sudah Terinstall

```bash
ollama list
```

Output contoh:
```
NAME                    ID              SIZE      MODIFIED
deepseek-ocr:latest     abc123def       13 GB     2 days ago
```

### 5. Pull Model Quantized yang Ringan

**Pilih salah satu:**

#### Option A: PaddleOCR-VL Q4K (RECOMMENDED - Paling Ringan)

```bash
ollama pull paddleocr-vl:q4k
```

#### Option B: DeepSeek-OCR Q4K

```bash
ollama pull deepseek-ocr:q4k
```

**Monitor progress:**
```bash
# Di terminal lain, jalankan nvtop untuk monitor VRAM usage
nvtop
```

### 6. Remove Model Lama (Opsional - Hemat Space)

Jika space terbatas, hapus model full precision:

```bash
ollama rm deepseek-ocr:latest
```

### 7. Restart OpenWebUI (Jika Perlu)

```bash
# Exit dari container
exit

# Restart container
docker restart open-webui
```

---

## 🧪 Testing dari macOS Client

### 1. Set Environment Variable (API Token)

Dapatkan token dari OpenWebUI:
1. Buka https://openwebui.3ddm.my.id/
2. Login
3. **Settings** → **Account** → **API Keys**
4. **Create New Secret Key**
5. Copy token (contoh: `sk-abc123xyz...`)

```bash
export OPENWEBUI_TOKEN="sk-abc123xyz..."
```

### 2. Edit Model di Code (File sudah diupdate!)

File: `examples/007_analyze_ai_deepseek_ocr_server.rs`

```rust
// Gunakan model quantized yang ringan
const MODEL_NAME: &str = "paddleocr-vl:q4k";  // ✅ Sudah diubah!
```

### 3. Run Client dari macOS

```bash
cd /tmp/ktp-ocr
cp /Users/yericoalexander/Documents/PROJECT-SMARTELCO/deepseek-ocr.rs/examples/007_analyze_ai_deepseek_ocr_server.rs src/main.rs

# Run dengan token
OPENWEBUI_TOKEN="sk-your-token" cargo run
```

**Atau set permanent:**

```bash
# Edit ~/.zshrc atau ~/.bashrc
echo 'export OPENWEBUI_TOKEN="sk-your-token"' >> ~/.zshrc
source ~/.zshrc

# Lalu cukup:
cargo run
```

---

## 🔍 Troubleshooting

### Error: "401 Unauthorized"

**Penyebab:** Token invalid atau expired

**Solusi:**
1. Generate token baru di OpenWebUI
2. Update environment variable

### Error: "404 Model Not Found"

**Penyebab:** Model belum di-pull di server

**Solusi:**
```bash
docker exec -it open-webui ollama pull paddleocr-vl:q4k
```

### Error: "500 Out of Memory" (Masih Terjadi)

**Penyebab:** Server masih kehabisan memory

**Solusi:**
1. **Check memory dengan nvtop/htop**
2. **Stop aplikasi lain yang pakai GPU/RAM**
3. **Gunakan model lebih kecil** (q4k → q2 jika ada)
4. **Restart server** jika perlu

```bash
# Check process yang pakai banyak memory
htop

# Kill process jika perlu
kill -9 <PID>
```

### Model Load Sangat Lama

**Normal!** Model quantized pertama kali load bisa 30-60 detik.

Monitor dengan:
```bash
# Terminal 1: Monitor VRAM
nvtop

# Terminal 2: Check OpenWebUI logs
docker logs -f open-webui
```

---

## 📊 Perbandingan Model

| Model | VRAM | Akurasi KTP | Speed | Recommendation |
|-------|------|-------------|-------|----------------|
| `paddleocr-vl:q4k` | 2-3GB | ⭐⭐⭐⭐⭐ | Fast | ✅ **BEST for KTP** |
| `paddleocr-vl:q8` | 4-5GB | ⭐⭐⭐⭐⭐ | Medium | Good |
| `deepseek-ocr:q4k` | 4-6GB | ⭐⭐⭐⭐ | Medium | OK |
| `deepseek-ocr` (full) | 13GB+ | ⭐⭐⭐⭐⭐ | Slow | ❌ Too heavy |

---

## 🎯 Expected Output

Setelah setup benar, hasilnya seperti ini:

```bash
✅ Configuration:
   Server  : https://openwebui.3ddm.my.id/v1/chat/completions
   Model   : paddleocr-vl:q4k (optimized for low memory)
   Image   : /Users/yericoalexander/Pictures/ktp.jpg

📤 Reading image: /Users/yericoalexander/Pictures/ktp.jpg
   Image size: 245.32 KB
📡 Sending request to OpenWebUI server...
   Using model: paddleocr-vl:q4k
📥 Response status: 200 OK

✅ HASIL OCR - Indonesian ID Card (KTP)
═══════════════════════════════════════════
{
  "NIK": "7371030303980002",
  "Nama": "JAYADI",
  "TempatTglLahir": "PEMATANGSIANTAR, 03-03-1998",
  "JenisKelamin": "LAKI-LAKI",
  "Alamat": "JL. SETIA BUDI NO. 123",
  ...
}
═══════════════════════════════════════════
```

---

## 📞 Support

Jika masih ada error:

1. **Screenshot error message** (full)
2. **Hasil `nvtop`** (memory usage)
3. **Hasil `ollama list`** (installed models)
4. **Send ke developer**

---

**Updated:** 26 November 2025  
**Untuk:** Gracia Rizka Pasfica (Client)  
**Developer:** Yerico Alexander
