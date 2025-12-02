#!/bin/bash
# Quick fix untuk SSH tunnel error
# Run this when: "Connection refused" error

echo "🔧 Fixing SSH Tunnel..."
echo ""

# Kill existing tunnel
echo "1️⃣  Killing old tunnel..."
pkill -f "ssh.*stb37" 2>/dev/null
sleep 1

# Start new tunnel
echo "2️⃣  Starting new tunnel..."
ssh -f -N stb37
if [ $? -ne 0 ]; then
    echo "   ❌ Failed to start tunnel!"
    echo "   💡 Check SSH config (~/.ssh/config)"
    exit 1
fi

# Wait for tunnel to establish
echo "3️⃣  Waiting for tunnel..."
sleep 2

# Verify tunnel
echo "4️⃣  Verifying tunnel..."
if lsof -i :23333 >/dev/null 2>&1; then
    echo "   ✅ Port 23333: LISTENING"
else
    echo "   ❌ Port 23333: NOT listening"
    exit 1
fi

if lsof -i :2221 >/dev/null 2>&1; then
    echo "   ✅ Port 2221: LISTENING"
else
    echo "   ❌ Port 2221: NOT listening"
    exit 1
fi

# Test SSH connection
echo "5️⃣  Testing SSH to rocky37..."
if ssh -o ConnectTimeout=5 rocky37 "echo OK" 2>/dev/null | grep -q OK; then
    echo "   ✅ SSH Connection: WORKING"
else
    echo "   ❌ SSH Connection: FAILED"
    exit 1
fi

# Test server
echo "6️⃣  Testing DeepSeek-OCR server..."
if curl -s http://localhost:23333/v1/models >/dev/null 2>&1; then
    echo "   ✅ Server: RESPONDING"
else
    echo "   ❌ Server: NOT responding"
    exit 1
fi

# Success
echo ""
echo "╔════════════════════════════════════════════════╗"
echo "║   ✅ ALL FIXED! Ready to proceed               ║"
echo "╚════════════════════════════════════════════════╝"
echo ""
echo "Now you can:"
echo "  → ssh rocky37"
echo "  → nvtop"
echo ""
