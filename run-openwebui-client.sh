#!/bin/bash

# =============================================================================
# DeepSeek-OCR SSH Tunnel Client Runner
# =============================================================================
# Script untuk menjalankan OCR client yang connect ke server via SSH tunnel
# Server: Rocky Linux 192.168.17.7:23333 (via stb37)
# Updated: 26 Nov 2025 - SSH tunnel configuration
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "════════════════════════════════════════════════════════════"
echo "  DeepSeek-OCR → Rocky Linux Server (via SSH Tunnel)"
echo "  Indonesian KTP Extraction"
echo "════════════════════════════════════════════════════════════"
echo -e "${NC}"

# Check if SSH tunnel is active
echo -e "${YELLOW}🔍 Checking SSH tunnel status...${NC}"
if ! lsof -i :23333 > /dev/null 2>&1; then
    echo -e "${RED}❌ ERROR: SSH tunnel tidak active!${NC}"
    echo ""
    echo -e "${YELLOW}📋 Cara setup tunnel:${NC}"
    echo "   1. Buka terminal baru"
    echo "   2. Run: ssh stb37"
    echo "   3. Biarkan terminal itu tetap running"
    echo "   4. Kembali ke terminal ini dan run script lagi"
    echo ""
    echo -e "${YELLOW}💡 Atau jalankan di background:${NC}"
    echo "   ssh -f -N stb37"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ SSH tunnel active (localhost:23333)${NC}"

# Test server connectivity
echo -e "${YELLOW}🔍 Testing server connectivity...${NC}"
if curl -s --max-time 5 http://localhost:23333/v1/models > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Server responding${NC}"
else
    echo -e "${RED}⚠️  WARNING: Server tidak merespon!${NC}"
    echo ""
    echo -e "${YELLOW}📋 Troubleshooting:${NC}"
    echo "   1. Check server status via: ssh rocky37"
    echo "   2. Check container: docker ps | grep deepseek"
    echo "   3. View logs: docker logs deepseek-ocr-server"
    echo "   4. Restart: docker restart deepseek-ocr-server"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Configuration
PROJECT_DIR="/tmp/ktp-ocr-openwebui"
SOURCE_FILE="/Users/yericoalexander/Documents/PROJECT-SMARTELCO/deepseek-ocr.rs/examples/007_analyze_ai_deepseek_ocr_server.rs"
IMAGE_PATH="${1:-/Users/yericoalexander/Pictures/ktp.jpg}"

# Configuration
PROJECT_DIR="/tmp/ktp-ocr-ssh-tunnel"
SOURCE_FILE="/Users/yericoalexander/Documents/PROJECT-SMARTELCO/deepseek-ocr.rs/examples/007_analyze_ai_deepseek_ocr_server.rs"
IMAGE_PATH="${1:-/Users/yericoalexander/Pictures/ktp.jpg}"

echo -e "${BLUE}📁 Project dir: ${PROJECT_DIR}${NC}"
echo -e "${BLUE}🖼️  Image: ${IMAGE_PATH}${NC}"
echo ""

# Check if image exists
if [ ! -f "$IMAGE_PATH" ]; then
    echo -e "${RED}❌ ERROR: Image tidak ditemukan: ${IMAGE_PATH}${NC}"
    echo ""
    echo -e "${YELLOW}💡 Usage:${NC}"
    echo "   $0 /path/to/your/ktp.jpg"
    echo ""
    exit 1
fi

# Create project if not exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}📦 Creating project directory...${NC}"
    mkdir -p "$PROJECT_DIR/src"
    
    # Create Cargo.toml
    cat > "$PROJECT_DIR/Cargo.toml" << 'EOF'
[package]
name = "ktp-ocr-openwebui"
version = "0.1.0"
edition = "2021"

[dependencies]
tokio = { version = "1.40", features = ["full"] }
reqwest = { version = "0.12", features = ["json"] }
serde_json = "1.0"
base64 = "0.22"
EOF
    
    echo -e "${GREEN}✅ Project created${NC}"
fi

# Copy source code
echo -e "${YELLOW}📝 Copying latest source code...${NC}"
cp "$SOURCE_FILE" "$PROJECT_DIR/src/main.rs"

# Update image path in source code
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s|const IMAGE_PATH: &str = \".*\";|const IMAGE_PATH: &str = \"$IMAGE_PATH\";|" "$PROJECT_DIR/src/main.rs"
else
    # Linux
    sed -i "s|const IMAGE_PATH: &str = \".*\";|const IMAGE_PATH: &str = \"$IMAGE_PATH\";|" "$PROJECT_DIR/src/main.rs"
fi

echo -e "${GREEN}✅ Source updated${NC}"
echo ""

# Build and run
echo -e "${YELLOW}🔨 Building and running...${NC}"
echo ""

cd "$PROJECT_DIR"

# Run (no token needed for local server)
cargo run --release

# Success
echo ""
echo -e "${GREEN}"
echo "════════════════════════════════════════════════════════════"
echo "  ✅ Completed!"
echo ""
echo "  💡 Jangan lupa: Keep SSH tunnel running!"
echo "     Terminal dengan 'ssh stb37' harus tetap active."
echo "════════════════════════════════════════════════════════════"
echo -e "${NC}"
