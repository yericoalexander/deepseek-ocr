#!/bin/bash
# OpenWebUI + DeepSeek-OCR Setup Script
# Author: Yerico Alexander
# Client: Gracia Rizka Pasfica
# Date: 1 Desember 2025

set -e

echo "🚀 OpenWebUI + DeepSeek-OCR Setup Script"
echo "========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVER_URL="http://localhost:23333"
OPENWEBUI_URL="https://openwebui.3ddm.my.id/"
ROCKY_IP="192.168.17.7"
ROCKY_PORT="23333"

# Step 1: Check SSH Tunnel
echo -e "${BLUE}[STEP 1] Checking SSH Tunnel...${NC}"
if lsof -i :23333 >/dev/null 2>&1; then
    echo -e "${GREEN}✅ SSH tunnel is running (localhost:23333 → Rocky)${NC}"
else
    echo -e "${YELLOW}⚠️  SSH tunnel not found. Creating tunnel...${NC}"
    ssh -f -N stb37
    sleep 2
    if lsof -i :23333 >/dev/null 2>&1; then
        echo -e "${GREEN}✅ SSH tunnel created successfully${NC}"
    else
        echo -e "${RED}❌ Failed to create SSH tunnel${NC}"
        exit 1
    fi
fi
echo ""

# Step 2: Test Server Connectivity
echo -e "${BLUE}[STEP 2] Testing Server Connectivity...${NC}"
if curl -s -f ${SERVER_URL}/v1/models >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Server is responding${NC}"
    
    # Get models count
    MODELS_COUNT=$(curl -s ${SERVER_URL}/v1/models | jq '.data | length')
    echo -e "${GREEN}✅ Found ${MODELS_COUNT} models available${NC}"
else
    echo -e "${RED}❌ Server not responding at ${SERVER_URL}${NC}"
    echo -e "${YELLOW}💡 Check if server is running on Rocky Linux${NC}"
    exit 1
fi
echo ""

# Step 3: Display Available Models
echo -e "${BLUE}[STEP 3] Available Models:${NC}"
curl -s ${SERVER_URL}/v1/models | jq -r '.data[] | "  - \(.id)"'
echo ""
echo -e "${GREEN}📝 Recommended for KTP: paddleocr-vl${NC}"
echo ""

# Step 4: OpenWebUI Configuration Info
echo -e "${BLUE}[STEP 4] OpenWebUI Configuration${NC}"
echo "========================================="
echo -e "${YELLOW}Please configure OpenWebUI with these settings:${NC}"
echo ""
echo "  🌐 OpenWebUI URL:"
echo "     ${OPENWEBUI_URL}"
echo ""
echo "  ⚙️  Connection Settings:"
echo "     Provider: OpenAI"
echo "     Base URL: http://${ROCKY_IP}:${ROCKY_PORT}/v1"
echo "     API Key:  sk-dummy-token (any value)"
echo ""
echo "  🎯 Model Selection:"
echo "     Primary:   paddleocr-vl"
echo "     Fallback:  paddleocr-vl-q4k"
echo ""

# Step 5: SSH Command for nvtop
echo -e "${BLUE}[STEP 5] GPU Monitoring Setup${NC}"
echo "========================================="
echo -e "${YELLOW}To monitor GPU on Rocky server:${NC}"
echo ""
echo "  1. SSH ke Rocky:"
echo "     ${GREEN}ssh stb37${NC}"
echo ""
echo "  2. Run nvtop:"
echo "     ${GREEN}nvtop${NC}"
echo ""
echo "  3. Keep terminal open untuk monitoring"
echo ""
echo -e "${BLUE}Alternative (via screen/tmux):${NC}"
echo "     ${GREEN}ssh stb37 -t 'tmux new -s monitoring nvtop'${NC}"
echo "     Detach: Ctrl+B, then D"
echo "     Reattach: tmux attach -t monitoring"
echo ""

# Step 6: Test Request Example
echo -e "${BLUE}[STEP 6] Test OCR Request (Example)${NC}"
echo "========================================="
cat << 'EOF'

Example curl command (untuk testing):

curl -X POST http://localhost:23333/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "paddleocr-vl",
    "messages": [{
      "role": "user",
      "content": [
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/jpeg;base64,<BASE64_IMAGE>"
          }
        },
        {
          "type": "text",
          "text": "Extract all text from this Indonesian ID card"
        }
      ]
    }],
    "max_tokens": 2048,
    "temperature": 0.1
  }'

EOF

# Step 7: Summary
echo -e "${BLUE}[STEP 7] Setup Summary${NC}"
echo "========================================="
echo -e "${GREEN}✅ SSH Tunnel: READY${NC}"
echo -e "${GREEN}✅ Server Connection: VERIFIED${NC}"
echo -e "${GREEN}✅ Models Available: ${MODELS_COUNT}${NC}"
echo -e "${GREEN}✅ Documentation: OPENWEBUI_SETUP_GUIDE.md${NC}"
echo ""
echo -e "${YELLOW}📋 Next Steps for Grace:${NC}"
echo "  1. Login ke OpenWebUI (${OPENWEBUI_URL})"
echo "  2. Add connection dengan Base URL: http://${ROCKY_IP}:${ROCKY_PORT}/v1"
echo "  3. Select model: paddleocr-vl"
echo "  4. SSH ke Rocky dan run: nvtop"
echo "  5. Upload KTP dan test extraction"
echo ""
echo -e "${BLUE}Status: 🎯 READY FOR PRODUCTION${NC}"
echo ""

# Optional: Open monitoring in separate terminal
read -p "Open nvtop monitoring in new terminal? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    osascript -e 'tell application "Terminal" to do script "ssh stb37 -t nvtop"'
    echo -e "${GREEN}✅ Opened nvtop in new terminal window${NC}"
fi

echo ""
echo -e "${GREEN}✨ Setup script completed successfully!${NC}"
