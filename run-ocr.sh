#!/bin/zsh

# DeepSeek-OCR CLI Helper Script
# Automatically loads Rust environment and runs deepseek-ocr-cli

# Load Rust environment
source "$HOME/.cargo/env"

# Run deepseek-ocr-cli with all arguments passed to this script
deepseek-ocr-cli "$@"
