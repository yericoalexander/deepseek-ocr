# 🚀 Quick Start - DeepSeek-OCR via SSH Tunnel

**Last Updated:** 26 November 2025  
**Server:** Rocky Linux 192.168.17.7 (via STB37)

---

## ⚡ Quick Steps (3 Commands)

### Terminal 1: Start SSH Tunnel
```bash
ssh stb37
# Keep this running! Don't close this terminal.
```

### Terminal 2: Run OCR
```bash
cd /Users/yericoalexander/Documents/PROJECT-SMARTELCO/deepseek-ocr.rs
./run-openwebui-client.sh /Users/yericoalexander/Pictures/ktp.jpg
```

**That's it!** ✅

---

## 📋 Complete Workflow

### Step 1: Start SSH Tunnel (One Time - Keep Running)

```bash
# Terminal 1
ssh stb37
```

**What happens:**
- ✅ Connects to STB37 via Cloudflared
- ✅ Creates port forward: `localhost:23333` → `192.168.17.7:23333`
- ✅ Enables access to DeepSeek-OCR server

**Important:** Leave this terminal open! The tunnel stays active as long as this SSH session is running.

---

### Step 2: Test Connection (Optional but Recommended)

```bash
# Terminal 2
# Test if server is accessible
curl http://localhost:23333/v1/models

# Expected output:
# {"object":"list","data":[{"id":"paddleocr-vl",...}]}
```

**If fails:**
```bash
# Check server via SSH
ssh rocky37
docker ps | grep deepseek
docker logs deepseek-ocr-server

# Start server if not running
docker start deepseek-ocr-server
```

---

### Step 3: Run OCR Extraction

#### Option A: Using Script (Recommended)

```bash
# Terminal 2
cd /Users/yericoalexander/Documents/PROJECT-SMARTELCO/deepseek-ocr.rs
./run-openwebui-client.sh /Users/yericoalexander/Pictures/ktp.jpg
```

#### Option B: Manual Run

```bash
# Terminal 2
cd /tmp/ktp-ocr
mkdir -p src

# Copy latest code
cp /Users/yericoalexander/Documents/PROJECT-SMARTELCO/deepseek-ocr.rs/examples/007_analyze_ai_deepseek_ocr_server.rs src/main.rs

# Ensure Cargo.toml exists
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

# Run
cargo run
```

---

## 🎯 Expected Output

### ✅ Success

```
════════════════════════════════════════════════════════════
  DeepSeek-OCR → Rocky Linux Server (via SSH Tunnel)
  Indonesian KTP Extraction
════════════════════════════════════════════════════════════

🔍 Checking SSH tunnel status...
✅ SSH tunnel active (localhost:23333)
🔍 Testing server connectivity...
✅ Server responding
📁 Project dir: /tmp/ktp-ocr-ssh-tunnel
🖼️  Image: /Users/yericoalexander/Pictures/ktp.jpg

✅ Configuration:
   Server  : http://localhost:23333/v1/chat/completions
   Model   : paddleocr-vl
   Image   : /Users/yericoalexander/Pictures/ktp.jpg

📤 Reading image: /Users/yericoalexander/Pictures/ktp.jpg
   Image size: 245.32 KB
📡 Sending request to DeepSeek-OCR server via SSH tunnel...
   Using model: paddleocr-vl
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

════════════════════════════════════════════════════════════
  ✅ Completed!

  💡 Jangan lupa: Keep SSH tunnel running!
     Terminal dengan 'ssh stb37' harus tetap active.
════════════════════════════════════════════════════════════
```

---

## ⚠️ Common Errors

### ❌ SSH tunnel tidak active

```
❌ ERROR: SSH tunnel tidak active!

📋 Cara setup tunnel:
   1. Buka terminal baru
   2. Run: ssh stb37
   3. Biarkan terminal itu tetap running
   4. Kembali ke terminal ini dan run script lagi
```

**Fix:**
```bash
# Terminal 1
ssh stb37
# Keep running!

# Terminal 2
./run-openwebui-client.sh ktp.jpg
```

---

### ⚠️ Server tidak merespon

```
⚠️  WARNING: Server tidak merespon!

📋 Troubleshooting:
   1. Check server status via: ssh rocky37
   2. Check container: docker ps | grep deepseek
   3. View logs: docker logs deepseek-ocr-server
   4. Restart: docker restart deepseek-ocr-server
```

**Fix:**
```bash
# Via SSH
ssh rocky37

# Check status
docker ps | grep deepseek

# View logs
docker logs --tail 50 deepseek-ocr-server

# Restart if needed
docker restart deepseek-ocr-server

# Verify server listening
sudo netstat -tulpn | grep 23333
```

---

### ❌ Image tidak ditemukan

```
❌ ERROR: Image tidak ditemukan: /path/to/image.jpg

💡 Usage:
   ./run-openwebui-client.sh /path/to/your/ktp.jpg
```

**Fix:**
```bash
# Check image exists
ls -lh /Users/yericoalexander/Pictures/ktp.jpg

# Use correct path
./run-openwebui-client.sh /Users/yericoalexander/Pictures/ktp.jpg
```

---

## 🔧 Advanced Usage

### Background SSH Tunnel

Jika tidak mau terminal tetap terbuka:

```bash
# Start tunnel in background
ssh -f -N stb37

# Verify tunnel active
lsof -i :23333
ps aux | grep "ssh stb37"

# Kill background tunnel when done
pkill -f "ssh stb37"
```

### Auto-Reconnect Tunnel

Install autossh untuk auto-reconnect jika putus:

```bash
# Install
brew install autossh

# Run with auto-reconnect
autossh -M 0 -f -N \
  -o "ServerAliveInterval 60" \
  -o "ServerAliveCountMax 3" \
  stb37

# Verify
lsof -i :23333
```

### Test Multiple Images

```bash
# Process multiple KTP images
for img in /Users/yericoalexander/Pictures/*.jpg; do
    echo "Processing: $img"
    ./run-openwebui-client.sh "$img"
    echo "---"
done
```

### Debug Mode

```bash
# Enable debug output
DEBUG=1 cargo run

# This will show full HTTP request/response
```

---

## 📊 Performance Tips

### Optimize Image Size

```bash
# Resize image for faster upload (optional)
convert input.jpg -resize 1600x1200 -quality 85 output.jpg

# Or use sips (macOS built-in)
sips -Z 1600 input.jpg --out output.jpg
```

### Batch Processing

Create script for batch:

```bash
#!/bin/bash
# batch-ocr.sh

for img in "$@"; do
    echo "Processing: $(basename "$img")"
    ./run-openwebui-client.sh "$img" > "$(basename "$img" .jpg).json"
done

# Usage:
# ./batch-ocr.sh *.jpg
```

---

## 🔍 Monitoring

### Watch Server Logs

```bash
# In separate terminal
ssh rocky37
docker logs -f deepseek-ocr-server

# Or with timestamps
docker logs -f --timestamps deepseek-ocr-server
```

### Monitor System Resources

```bash
# Via SSH to Rocky
ssh rocky37

# CPU/Memory usage
htop

# GPU usage (if available)
nvtop
# or
nvidia-smi -l 1

# Network traffic
iftop
```

---

## 📞 Quick Reference

```bash
# Start tunnel
ssh stb37                    # Terminal 1 - keep running

# Test
curl http://localhost:23333/v1/models     # Test connectivity
lsof -i :23333                            # Check tunnel
ps aux | grep ssh                         # Check SSH process

# Run OCR
./run-openwebui-client.sh ktp.jpg        # Extract KTP

# Server management
ssh rocky37                               # Connect to server
docker ps | grep deepseek                 # Check container
docker logs deepseek-ocr-server          # View logs
docker restart deepseek-ocr-server       # Restart

# Cleanup
pkill -f "ssh stb37"                     # Kill tunnel
```

---

## ✅ Checklist Sebelum Run

- [ ] SSH tunnel active (`ssh stb37` running)
- [ ] Server responding (`curl http://localhost:23333/v1/models`)
- [ ] Image file exists (`ls -lh image.jpg`)
- [ ] Cargo installed (`cargo --version`)
- [ ] Port 23333 forwarded (`lsof -i :23333`)

---

**Ready to go!** 🚀

For detailed setup: See `SSH_SETUP.md`  
For troubleshooting: See `CLIENT_GUIDE.md`
