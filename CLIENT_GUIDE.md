# 🎯 Quick Guide untuk Client (Gracia Rizka Pasfica)

## Problem yang Sudah Diperbaiki

✅ **Error "500: failed to load language model"** → Fixed dengan menggunakan model quantized  
✅ **Out of memory di server Rocky** → Model diganti ke `paddleocr-vl:q4k` (hanya butuh 2-3GB)  
✅ **Token authentication** → Sudah dihandle dengan environment variable  

---

## 📋 Yang Perlu Dilakukan

### Di Server Rocky Linux (Oleh Gracia)

```bash
# 1. SSH ke server
ssh rocky@your-server-ip

# 2. Masuk ke OpenWebUI container
docker exec -it open-webui bash

# 3. Pull model quantized yang ringan
ollama pull paddleocr-vl:q4k

# 4. Tunggu sampai selesai download (monitor dengan nvtop di terminal lain)
# Model size: ~2.5GB, butuh 2-3GB VRAM saat run

# 5. Verify model sudah terinstall
ollama list

# Output yang diharapkan:
# NAME                    ID              SIZE      MODIFIED
# paddleocr-vl:q4k        xyz789abc       2.5 GB    1 minute ago

# 6. Exit dari container
exit
```

### Di macOS Client (Oleh Yerico)

```bash
# 1. Set API Token (dapatkan dari OpenWebUI Settings → API Keys)
export OPENWEBUI_TOKEN="sk-xxxxxxxxxxxxxxxx"

# 2. Jalankan client
cd /Users/yericoalexander/Documents/PROJECT-SMARTELCO/deepseek-ocr.rs
./run-openwebui-client.sh /Users/yericoalexander/Pictures/ktp.jpg
```

---

## 🚀 Alternative: Manual Run

Jika script tidak jalan, run manual:

```bash
# 1. Prepare project
cd /tmp/ktp-ocr
mkdir -p src

# 2. Create Cargo.toml
cat > Cargo.toml << 'EOF'
[package]
name = "ktp-ocr"
version = "0.1.0"
edition = "2021"

[dependencies]
tokio = { version = "1.40", features = ["full"] }
reqwest = { version = "0.12", features = ["json"] }
serde_json = "1.0"
base64 = "0.22"
EOF

# 3. Copy source
cp /Users/yericoalexander/Documents/PROJECT-SMARTELCO/deepseek-ocr.rs/examples/007_analyze_ai_deepseek_ocr_server.rs src/main.rs

# 4. Run dengan token
OPENWEBUI_TOKEN="sk-xxx" cargo run
```

---

## 📊 Expected Output

### ✅ Success Case

```
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
  "RTRW": "001/002",
  "KelDesa": "SETIA BUDI",
  "Kecamatan": "MEDAN SELAYANG",
  "Agama": "ISLAM",
  "StatusPerkawinan": "BELUM KAWIN",
  "Pekerjaan": "PELAJAR/MAHASISWA",
  "Kewarganegaraan": "WNI"
}
═══════════════════════════════════════════
```

### ❌ Error Cases & Solutions

#### Error 401: Unauthorized

```
❌ ERROR dari server OpenWebUI
═══════════════════════════════════════════
Status Code: 401 Unauthorized
Detail: {"detail":"Your session has expired..."}

💡 Solusi:
   Token tidak valid atau expired.
   Buat token baru di: https://openwebui.3ddm.my.id/
   Settings → Account → API Keys → Create New
```

**Fix:**
```bash
# Generate new token, then:
export OPENWEBUI_TOKEN="sk-new-token-here"
./run-openwebui-client.sh
```

#### Error 500: Out of Memory

```
❌ ERROR dari server OpenWebUI
═══════════════════════════════════════════
Status Code: 500 Internal Server Error
Detail: {"detail":"failed to load language model"}

💡 Solusi:
   Server kehabisan memory saat load model.
   Model 'paddleocr-vl:q4k' terlalu besar.

   Saran:
   1. Pastikan model sudah ter-install di server:
      docker exec -it open-webui ollama list

   2. Jika belum ada, pull model quantized:
      docker exec -it open-webui ollama pull paddleocr-vl:q4k

   3. Monitor memory dengan nvtop atau htop
      Pastikan VRAM/RAM cukup (minimal 4GB free)
```

**Fix di Server:**
```bash
# Check memory terlebih dahulu
free -h
nvtop  # atau nvidia-smi

# Pastikan minimal 4GB free, lalu:
docker exec -it open-webui ollama pull paddleocr-vl:q4k
```

#### Error 404: Model Not Found

```
❌ ERROR dari server OpenWebUI
═══════════════════════════════════════════
Status Code: 404 Not Found

💡 Solusi:
   Model 'paddleocr-vl:q4k' tidak ditemukan di server.
   Jalankan di server: ollama pull paddleocr-vl:q4k
```

**Fix di Server:**
```bash
docker exec -it open-webui ollama pull paddleocr-vl:q4k
```

---

## 🔍 Debug Mode

Untuk melihat full response dari server:

```bash
DEBUG=1 OPENWEBUI_TOKEN="sk-xxx" cargo run
```

Output akan include full JSON response structure.

---

## 📝 Checklist Sebelum Run

Server Side (Rocky Linux):
- [ ] OpenWebUI container running (`docker ps`)
- [ ] Model `paddleocr-vl:q4k` sudah ter-install (`ollama list`)
- [ ] Memory cukup: minimal 4GB free (`free -h`, `nvtop`)

Client Side (macOS):
- [ ] Rust & Cargo ter-install (`cargo --version`)
- [ ] Token sudah di-set (`echo $OPENWEBUI_TOKEN`)
- [ ] Image KTP exists (`ls -lh /Users/yericoalexander/Pictures/ktp.jpg`)
- [ ] Network bisa akses server (`ping openwebui.3ddm.my.id`)

---

## 📞 Contact

**Developer:** Yerico Alexander  
**Client:** Gracia Rizka Pasfica  
**Date:** 26 November 2025  

Jika masih ada error, kirim screenshot full error + output dari:
```bash
# Di server
docker logs open-webui | tail -50
ollama list
free -h
```

---

**File Changes Summary:**

1. ✅ `examples/007_analyze_ai_deepseek_ocr_server.rs`
   - Model changed: `deepseek-ocr` → `paddleocr-vl:q4k`
   - Added detailed error handling
   - Added memory optimization
   - Better logging & diagnostics

2. ✅ `run-openwebui-client.sh`
   - New automated runner script
   - Auto-setup project structure
   - Token validation

3. ✅ `SETUP_SERVER_ROCKY.md`
   - Complete server setup guide
   - Troubleshooting steps
   - Memory optimization tips

4. ✅ `CLIENT_GUIDE.md` (this file)
   - Quick reference for client
   - Error solutions
   - Expected outputs
