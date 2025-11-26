#!/bin/bash

# =============================================================================
# DeepSeek-OCR OpenWebUI Client Runner
# =============================================================================
# Script untuk menjalankan OCR client yang connect ke OpenWebUI server
# Updated: 26 Nov 2025 - Fixed for low memory server (Gracia's request)
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
echo "  DeepSeek-OCR → OpenWebUI Client"
echo "  Indonesian KTP Extraction"
echo "════════════════════════════════════════════════════════════"
echo -e "${NC}"

# Check if token is set
if [ -z "$OPENWEBUI_TOKEN" ]; then
    echo -e "${RED}❌ ERROR: OPENWEBUI_TOKEN tidak ditemukan!${NC}"
    echo ""
    echo -e "${YELLOW}📋 Cara setup:${NC}"
    echo "   1. Buka: https://openwebui.3ddm.my.id/"
    echo "   2. Login dengan akun Anda"
    echo "   3. Settings → Account → API Keys"
    echo "   4. Create New Secret Key"
    echo "   5. Copy token tersebut"
    echo ""
    echo -e "${YELLOW}🔧 Set token dengan:${NC}"
    echo "   export OPENWEBUI_TOKEN=\"sk-xxxxxxxxxxxxxxxx\""
    echo ""
    echo -e "${YELLOW}💡 Atau jalankan script dengan:${NC}"
    echo "   OPENWEBUI_TOKEN=\"sk-xxx\" $0"
    echo ""
    exit 1
fi

# Configuration
PROJECT_DIR="/tmp/ktp-ocr-openwebui"
SOURCE_FILE="/Users/yericoalexander/Documents/PROJECT-SMARTELCO/deepseek-ocr.rs/examples/007_analyze_ai_deepseek_ocr_server.rs"
IMAGE_PATH="${1:-/Users/yericoalexander/Pictures/ktp.jpg}"

echo -e "${GREEN}✅ Token found${NC}"
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

# Set environment and run
export OPENWEBUI_TOKEN="$OPENWEBUI_TOKEN"
cargo run --release

# Success
echo ""
echo -e "${GREEN}"
echo "════════════════════════════════════════════════════════════"
echo "  ✅ Completed!"
echo "════════════════════════════════════════════════════════════"
echo -e "${NC}"
