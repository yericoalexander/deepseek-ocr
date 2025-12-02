#!/bin/bash
# Quick Start Guide untuk Grace
# Run script ini untuk cek semua ready

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   🚀 QUICK START - OpenWebUI + DeepSeek-OCR (Grace)       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check 1: Server connection
echo "📡 [1/4] Checking server connection..."
if curl -s http://192.168.17.7:23333/v1/models > /dev/null 2>&1; then
    echo "     ✅ Server READY di 192.168.17.7:23333"
else
    echo "     ❌ Server NOT reachable!"
    echo "     💡 Fix: Contact Yerico atau cek server Rocky"
    exit 1
fi

# Check 2: Models available
echo ""
echo "🎯 [2/4] Checking available models..."
MODEL_COUNT=$(curl -s http://192.168.17.7:23333/v1/models | grep -o '"id"' | wc -l)
if [ "$MODEL_COUNT" -eq 12 ]; then
    echo "     ✅ 12 models available"
else
    echo "     ⚠️  Found $MODEL_COUNT models (expected 12)"
fi

# Check 3: OpenWebUI accessible
echo ""
echo "🌐 [3/4] Checking OpenWebUI..."
if curl -s https://openwebui.3ddm.my.id/ > /dev/null 2>&1; then
    echo "     ✅ OpenWebUI accessible"
else
    echo "     ⚠️  OpenWebUI might be down"
    echo "     💡 Try: Open browser manually"
fi

# Check 4: SSH to Rocky (for nvtop)
echo ""
echo "🔐 [4/4] Testing SSH to Rocky..."
echo "     💡 Kalau minta password, masukkan password SSH kamu"
if ssh -o ConnectTimeout=5 rocky37 "echo OK" 2>/dev/null | grep -q OK; then
    echo "     ✅ SSH connection READY"
else
    echo "     ⚠️  SSH failed (normal kalau belum setup key)"
    echo "     💡 Nanti manual: ssh rocky37"
fi

# Summary
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    🎯 READY TO START!                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Next Steps untuk Grace:"
echo ""
echo "   1️⃣  Login OpenWebUI"
echo "       → https://openwebui.3ddm.my.id/"
echo ""
echo "   2️⃣  Setup Connection"
echo "       → Settings → Admin → Connections"
echo "       → Add OpenAI connection"
echo "       → Base URL: http://192.168.17.7:23333/v1"
echo "       → API Key: sk-dummy-token"
echo ""
echo "   3️⃣  Select Model"
echo "       → Choose: paddleocr-vl"
echo ""
echo "   4️⃣  Start Monitoring"
echo "       → Terminal: ssh rocky37"
echo "       → Run: nvtop"
echo ""
echo "   5️⃣  Upload KTP & Extract"
echo "       → Upload image"
echo "       → Prompt: 'Extract all text from this KTP'"
echo "       → Wait ~10 seconds"
echo ""
echo "📚 Detailed Guide:"
echo "   → STEP_BY_STEP_UNTUK_GRACE.md"
echo ""
echo "📞 Need Help?"
echo "   → Contact Yerico"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""
