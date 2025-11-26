# 🔐 SSH Tunnel Setup untuk DeepSeek-OCR Server

**Date:** 26 November 2025  
**Developer:** Yerico Alexander  
**Server:** Rocky Linux 192.168.17.7 (via STB37)

---

## 📋 Arsitektur Koneksi

```
macOS Client (You)
    ↓ SSH via Cloudflared
STB37 (stb37.3ddm.my.id)
    ↓ Port Forward 23333
Rocky Linux (192.168.17.7:23333)
    ↓ DeepSeek-OCR Server
Model: paddleocr-vl / deepseek-ocr
```

---

## 🔧 SSH Configuration

File: `~/.ssh/config`

```ssh
Host stb37
  User ustb
  HostName stb37.3ddm.my.id
  ProxyCommand "/opt/homebrew/bin/cloudflared" access ssh --hostname %h
  IdentityFile ~/.ssh/id_rsa_stb37
  LocalForward 2221 192.168.17.7:22      # SSH Rocky
  LocalForward 5433 192.168.17.7:5433    # PostgreSQL
  LocalForward 5332 192.168.17.7:5332    # PostgreSQL Indico
  LocalForward 5901 192.168.17.7:5901    # VNC
  LocalForward 1234 192.168.17.7:1234    # LMStudio
  LocalForward 8001 192.168.17.7:8000    # SurrealDB
  LocalForward 19443 192.168.17.7:19443  # Portainer
  LocalForward 18080 192.168.17.7:8080   # AI
  LocalForward 19090 192.168.17.7:9090   # Cockpit Rocky
  LocalForward 17860 192.168.17.7:17860  # Langflow
  LocalForward 23000 192.168.17.7:23000  # Grafana
  LocalForward 29090 192.168.17.7:29090  # Prometheus
  LocalForward 29100 192.168.17.7:29100  # Node Exporter
  LocalForward 18123 192.168.17.7:18123  # ClickHouse HTTP
  LocalForward 19000 192.168.17.7:19000  # ClickHouse Native
  LocalForward 9030 192.168.17.7:9030    # Other
  LocalForward 23333 192.168.17.7:23333  # 🎯 DeepSeek-OCR Server
  ServerAliveInterval 60

Host rocky37
  HostName localhost
  Port 2221
  User rocky
  IdentityFile ~/.ssh/id_rsa_rocky37
  PubkeyAuthentication yes
```

**Key Port:** `23333` → DeepSeek-OCR Server

---

## 🚀 Step-by-Step Usage

### 1. Start SSH Tunnel (Terminal 1)

```bash
# Connect ke STB37 - ini akan create semua port forwards
ssh stb37
```

**Expected Output:**
```
Welcome to Ubuntu...
Last login: Tue Nov 26 ...
ustb@stb37:~$
```

**✅ Tunnel Active!** Jangan close terminal ini, biarkan running.

---

### 2. Verify Tunnel (Terminal 2)

```bash
# Test DeepSeek-OCR server accessibility
curl http://localhost:23333/v1/models

# Expected output (jika server running):
# {"object":"list","data":[{"id":"paddleocr-vl",...}]}
```

**Troubleshooting:**
```bash
# Jika connection refused:
curl: (7) Failed to connect to localhost port 23333: Connection refused

# Solusi:
# 1. Pastikan SSH tunnel masih active (Terminal 1)
# 2. Check server status di Rocky:
ssh rocky37
docker ps | grep deepseek
# atau
systemctl status deepseek-ocr-server
```

---

### 3. Run OCR Client (Terminal 2)

#### Option A: Using Script (Recommended)

```bash
cd /Users/yericoalexander/Documents/PROJECT-SMARTELCO/deepseek-ocr.rs
./run-openwebui-client.sh /Users/yericoalexander/Pictures/ktp.jpg
```

#### Option B: Manual Run

```bash
cd /tmp/ktp-ocr
cp /Users/yericoalexander/Documents/PROJECT-SMARTELCO/deepseek-ocr.rs/examples/007_analyze_ai_deepseek_ocr_server.rs src/main.rs
cargo run
```

---

## 🔍 Server Management via SSH

### Connect ke Rocky Linux

```bash
# Via tunnel (setelah ssh stb37 running)
ssh rocky37
```

### Check DeepSeek-OCR Server Status

```bash
# If running as Docker container
docker ps | grep deepseek
docker logs -f deepseek-ocr-server

# If running as systemd service
systemctl status deepseek-ocr-server
journalctl -u deepseek-ocr-server -f

# If running manually
ps aux | grep deepseek
```

### Start/Stop Server

```bash
# Docker
docker start deepseek-ocr-server
docker stop deepseek-ocr-server
docker restart deepseek-ocr-server

# Systemd
sudo systemctl start deepseek-ocr-server
sudo systemctl stop deepseek-ocr-server
sudo systemctl restart deepseek-ocr-server

# Check logs
docker logs --tail 100 deepseek-ocr-server
```

### Check Available Models

```bash
# Via API (dari macOS dengan tunnel active)
curl http://localhost:23333/v1/models | jq

# Di Rocky server
# Jika menggunakan ollama backend:
ollama list

# Expected output:
# NAME                ID        SIZE      MODIFIED
# paddleocr-vl:latest xyz123    4.7 GB    2 days ago
# deepseek-ocr:latest abc456    13 GB     3 days ago
```

---

## 🧪 Testing Workflow

### Complete Test Sequence

```bash
# Terminal 1: Start tunnel
ssh stb37
# Keep this running!

# Terminal 2: Test & run
# 1. Verify tunnel
curl http://localhost:23333/v1/models

# 2. Check image exists
ls -lh /Users/yericoalexander/Pictures/ktp.jpg

# 3. Run OCR
cd /Users/yericoalexander/Documents/PROJECT-SMARTELCO/deepseek-ocr.rs
./run-openwebui-client.sh /Users/yericoalexander/Pictures/ktp.jpg
```

---

## 🎯 Expected Output

### ✅ Success Case

```
✅ Configuration:
   Server  : http://localhost:23333/v1/chat/completions
   Model   : paddleocr-vl (optimized for low memory)
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
```

---

## ⚠️ Troubleshooting

### Error: "Connection refused" on localhost:23333

**Cause:** SSH tunnel tidak active atau server tidak running

**Solution:**
```bash
# 1. Check SSH tunnel status
ps aux | grep "ssh stb37"

# 2. Check port forwarding
lsof -i :23333
# Expected: ssh process

# 3. If not active, reconnect
ssh stb37

# 4. Verify di Terminal baru
curl http://localhost:23333/v1/models
```

### Error: "Connection timeout"

**Cause:** Server di Rocky tidak running atau firewall block

**Solution:**
```bash
# Via SSH ke Rocky
ssh rocky37

# Check server status
docker ps | grep deepseek
# atau
systemctl status deepseek-ocr-server

# Check port listening
sudo netstat -tulpn | grep 23333
# Expected: deepseek-ocr-server listening

# Start server jika mati
docker start deepseek-ocr-server
```

### Error: "Model not found"

**Cause:** Model belum di-load di server

**Solution:**
```bash
# Check available models via API
curl http://localhost:23333/v1/models | jq

# Atau via SSH ke Rocky
ssh rocky37
ollama list

# Pull model jika belum ada
ollama pull paddleocr-vl
# atau
ollama pull deepseek-ocr:q4k
```

### SSH Tunnel Terputus

**Cause:** Network issue atau timeout

**Solution:**
```bash
# Reconnect
ssh stb37

# Atau gunakan autossh untuk auto-reconnect
brew install autossh
autossh -M 0 -o "ServerAliveInterval 60" -o "ServerAliveCountMax 3" stb37
```

---

## 🔐 Security Notes

### SSH Keys

Pastikan SSH keys sudah ter-setup:

```bash
# Check keys exist
ls -lh ~/.ssh/id_rsa_stb37
ls -lh ~/.ssh/id_rsa_rocky37

# Set proper permissions
chmod 600 ~/.ssh/id_rsa_stb37
chmod 600 ~/.ssh/id_rsa_rocky37
chmod 600 ~/.ssh/config
```

### Cloudflared

```bash
# Verify cloudflared installed
which cloudflared
# /opt/homebrew/bin/cloudflared

# Test cloudflared access
/opt/homebrew/bin/cloudflared access ssh --hostname stb37.3ddm.my.id
```

---

## 📊 Port Mapping Reference

| Local Port | Remote Server | Service | Description |
|-----------|---------------|---------|-------------|
| 2221 | 192.168.17.7:22 | SSH | Rocky Linux SSH |
| 5433 | 192.168.17.7:5433 | PostgreSQL | Main DB |
| 5332 | 192.168.17.7:5332 | PostgreSQL | Indico DB |
| 5901 | 192.168.17.7:5901 | VNC | Remote Desktop |
| 1234 | 192.168.17.7:1234 | LMStudio | AI Server |
| 8001 | 192.168.17.7:8000 | SurrealDB | NoSQL DB |
| 19443 | 192.168.17.7:19443 | Portainer | Docker Management |
| 18080 | 192.168.17.7:8080 | AI Service | AI API |
| 19090 | 192.168.17.7:9090 | Cockpit | Server Management |
| 17860 | 192.168.17.7:17860 | Langflow | AI Workflow |
| 23000 | 192.168.17.7:23000 | Grafana | Monitoring Dashboard |
| 29090 | 192.168.17.7:29090 | Prometheus | Metrics |
| 29100 | 192.168.17.7:29100 | Node Exporter | System Metrics |
| 18123 | 192.168.17.7:18123 | ClickHouse | HTTP Interface |
| 19000 | 192.168.17.7:19000 | ClickHouse | Native Client |
| **23333** | **192.168.17.7:23333** | **DeepSeek-OCR** | **🎯 OCR Server** |

---

## 🚦 Quick Commands Reference

```bash
# Connect
ssh stb37                    # Start tunnel (Terminal 1 - keep running)

# Test
curl http://localhost:23333/v1/models     # Verify server
curl http://localhost:23333/health        # Health check

# Server Management (via ssh rocky37)
docker ps                                 # List containers
docker logs -f deepseek-ocr-server       # View logs
docker restart deepseek-ocr-server       # Restart
ollama list                               # List models

# Run OCR
./run-openwebui-client.sh ktp.jpg        # Run OCR extraction

# Debug
DEBUG=1 cargo run                         # Debug mode
lsof -i :23333                            # Check port
ps aux | grep ssh                         # Check tunnel
```

---

## 📞 Support

**Issues:**
1. Tunnel tidak connect → Check cloudflared & SSH keys
2. Server tidak response → Check di Rocky via `ssh rocky37`
3. Model error → Verify model availability

**Logs Location:**
- SSH: `~/.ssh/` (local)
- Server: `/var/log/deepseek-ocr/` (Rocky)
- Docker: `docker logs deepseek-ocr-server`

---

**Updated:** 26 November 2025  
**Developer:** Yerico Alexander  
**Configuration:** STB37 → Rocky37 → DeepSeek-OCR
