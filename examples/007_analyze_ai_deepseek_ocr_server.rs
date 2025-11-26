use std::fs;
use std::env;
use base64::{Engine as _, engine::general_purpose};
use serde_json::json;
use std::error::Error;

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    // --- KONFIGURASI ---
    // Server URL - DeepSeek-OCR Server via SSH Tunnel
    // Pastikan sudah connect ke SSH: ssh stb37
    // Tunnel akan map localhost:23333 -> 192.168.17.7:23333 (Rocky Linux)
    const SERVER_URL: &str = "http://localhost:23333/v1/chat/completions";
    
    // Path ke gambar KTP di macOS Anda
    const IMAGE_PATH: &str = "/Users/yericoalexander/Pictures/ktp.jpg"; 
    
    // ⚠️ PENTING: Model Selection berdasarkan Available Memory Server
    // Server Rocky Linux 192.168.17.7 dengan deepseek-ocr-server
    //
    // Pilihan model (dari ringan ke berat):
    // 1. "paddleocr-vl:q4k"      - 2-3GB VRAM (RECOMMENDED untuk server terbatas)
    // 2. "paddleocr-vl:q8"       - 4-5GB VRAM
    // 3. "deepseek-ocr:q4k"      - 4-6GB VRAM
    // 4. "deepseek-ocr"          - 13GB+ VRAM (Full precision)
    //
    // Note: Jika server sudah running model tertentu, gunakan model yang sama
    // paddleocr-vl terbukti berhasil extract text (dengan XML tags)
    const MODEL_NAME: &str = "paddleocr-vl"; 
    
    // API Token - Untuk deepseek-ocr-server biasanya tidak perlu token
    // Tapi jika server memerlukan, set via environment variable
    let api_token = env::var("DEEPSEEK_API_TOKEN")
        .unwrap_or_else(|_| {
            // Default token dummy jika server tidak require authentication
            "sk-dummy-token".to_string()
        });
    
    println!("✅ Configuration:");
    println!("   Server  : {}", SERVER_URL);
    println!("   Model   : {} (optimized for low memory)", MODEL_NAME);
    println!("   Image   : {}", IMAGE_PATH);
    println!();
    // -------------------

    println!("📤 Reading image: {}", IMAGE_PATH);

    // 1. Baca file gambar dan ubah ke Base64
    let image_data = fs::read(IMAGE_PATH)
        .map_err(|e| format!("❌ Gagal membaca gambar: {}. Pastikan file ada!", e))?;
    
    println!("   Image size: {:.2} KB", image_data.len() as f64 / 1024.0);
    
    let base64_image = general_purpose::STANDARD.encode(&image_data);
    let data_url = format!("data:image/jpeg;base64,{}", base64_image);

    // 2. Siapkan Payload JSON (Format OpenAI/OpenWebUI)
    let payload = json!({
        "model": MODEL_NAME,
        
        // Parameter optimized untuk OCR extraction (bukan generative text)
        "temperature": 0.1,        // Rendah = deterministik, tidak kreatif
        "top_p": 0.1,              // Fokus pada token dengan probability tinggi
        "frequency_penalty": 0.8,  // Hukuman keras untuk repetisi
        "max_tokens": 2048,        // Cukup untuk data KTP lengkap
        
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": data_url
                        }
                    },
                    {
                        "type": "text",
                        // Prompt sederhana untuk testing
                        "text": "What text do you see in this image?"
                    }
                ]
            }
        ]
    });
    
    println!("📡 Sending request to OpenWebUI server...");
    println!("   Using model: {}", MODEL_NAME);

    // 3. Kirim Request HTTP POST dengan timeout yang cukup
    let client = reqwest::Client::builder()
        .timeout(std::time::Duration::from_secs(120)) // 2 menit timeout untuk processing
        .build()?;
        
    let res = client.post(SERVER_URL)
        .header("Content-Type", "application/json")
        .header("Authorization", format!("Bearer {}", api_token))
        .json(&payload)
        .send()
        .await?;

    // 4. Proses Response dengan error handling detail
    let status = res.status();
    println!("📥 Response status: {}", status);
    
    if status.is_success() {
        let response_body: serde_json::Value = res.json().await?;
        
        // ALWAYS print full response for debugging
        println!("\n🔍 Full Response:");
        println!("{}", serde_json::to_string_pretty(&response_body)?);
        
        // Ambil content dari berbagai format response yang mungkin
        let content = response_body["choices"][0]["message"]["content"].as_str()
            .or_else(|| response_body["message"]["content"].as_str())
            .or_else(|| response_body["response"].as_str())
            .or_else(|| response_body["text"].as_str());
        
        if let Some(content) = content {
            println!("\n✅ HASIL OCR - Indonesian ID Card (KTP)");
            println!("═══════════════════════════════════════════");
            println!("{}", content);
            println!("═══════════════════════════════════════════\n");
        } else {
            println!("⚠️  Response tidak mengandung content yang diharapkan");
            println!("Response structure: {:?}", response_body);
        }
    } else {
        let error_text = res.text().await?;
        eprintln!("\n❌ ERROR dari server OpenWebUI");
        eprintln!("═══════════════════════════════════════════");
        eprintln!("Status Code: {}", status);
        eprintln!("Detail: {}", error_text);
        eprintln!("═══════════════════════════════════════════");
        
        // Diagnostic hints berdasarkan error code
        match status.as_u16() {
            401 => {
                eprintln!("\n💡 Solusi:");
                eprintln!("   Token tidak valid atau expired.");
                eprintln!("   Buat token baru di: https://openwebui.3ddm.my.id/");
                eprintln!("   Settings → Account → API Keys → Create New");
            },
            500 => {
                if error_text.contains("memory") || error_text.contains("load") {
                    eprintln!("\n💡 Solusi:");
                    eprintln!("   Server kehabisan memory saat load model.");
                    eprintln!("   Model '{}' terlalu besar.", MODEL_NAME);
                    eprintln!("\n   Saran:");
                    eprintln!("   1. Pastikan model sudah ter-install di server:");
                    eprintln!("      ssh rocky@server");
                    eprintln!("      docker exec -it open-webui ollama list");
                    eprintln!("\n   2. Jika belum ada, pull model quantized:");
                    eprintln!("      docker exec -it open-webui ollama pull paddleocr-vl:q4k");
                    eprintln!("\n   3. Monitor memory dengan nvtop atau htop");
                    eprintln!("      Pastikan VRAM/RAM cukup (minimal 4GB free)");
                }
            },
            404 => {
                eprintln!("\n💡 Solusi:");
                eprintln!("   Model '{}' tidak ditemukan di server.", MODEL_NAME);
                eprintln!("   Jalankan di server: ollama pull {}", MODEL_NAME);
            },
            _ => {}
        }
        
        return Err(format!("Server error: {}", status).into());
    }

    Ok(())
}