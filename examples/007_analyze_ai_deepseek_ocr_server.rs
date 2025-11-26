use std::fs;
use std::env;
use base64::{Engine as _, engine::general_purpose};
use serde_json::json;
use std::error::Error;

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    // --- KONFIGURASI ---
    // Server URL - OpenWebUI biasanya menggunakan endpoint /api/chat atau /ollama/api/chat
    // Coba beberapa kemungkinan endpoint:
    const SERVER_URL: &str = "https://openwebui.3ddm.my.id/ollama/api/chat";
    // Alternatif lain jika gagal:
    // const SERVER_URL: &str = "https://openwebui.3ddm.my.id/api/chat";
    // const SERVER_URL: &str = "https://openwebui.3ddm.my.id/v1/chat/completions";
    
    // Path ke gambar KTP di macOS Anda
    const IMAGE_PATH: &str = "/Users/yericoalexander/Pictures/ktp.jpg"; 
    
    // Model yang tersedia di OpenWebUI
    // Options: "deepseek-ocr", "paddleocr-vl", "dots-ocr", atau model quantized
    // Untuk KTP/ID Card, gunakan paddleocr-vl atau deepseek-ocr
    const MODEL_NAME: &str = "deepseek-ocr"; 
    
    // API Token dari environment variable
    // Set dengan: export OPENWEBUI_TOKEN="your_token_here"
    let api_token = env::var("OPENWEBUI_TOKEN")
        .unwrap_or_else(|_| {
            println!("⚠️  OPENWEBUI_TOKEN tidak ditemukan!");
            println!("Silakan set environment variable dengan:");
            println!("  export OPENWEBUI_TOKEN=\"your_api_key_here\"");
            println!("\nUntuk mendapatkan token:");
            println!("  1. Login ke https://openwebui.3ddm.my.id/");
            println!("  2. Buka Settings > Account > API Keys");
            println!("  3. Generate new API key");
            String::new()
        });
    
    if api_token.is_empty() {
        return Err("API token required".into());
    }
    // -------------------

    println!("Membaca gambar dari: {}", IMAGE_PATH);

    // 1. Baca file gambar dan ubah ke Base64
    let image_data = fs::read(IMAGE_PATH)?;
    let base64_image = general_purpose::STANDARD.encode(&image_data);
    let data_url = format!("data:image/jpeg;base64,{}", base64_image);

    // 2. Siapkan Payload JSON (Format OpenAI) dengan parameter pengekang
    let payload = json!({
        "model": MODEL_NAME,
        
        // --- PERUBAHAN PENTING DI SINI ---
        
        // 1. Temperature 0.1: Mematikan kreativitas. Model akan memilih kata yang paling mungkin (teks gambar).
        // Jangan set 0 pas (beberapa backend error), gunakan angka sangat kecil seperti 0.1 atau 0.01
        "temperature": 0.1, 
        
        // 2. Top_p rendah: Membatasi variasi pemilihan kata.
        "top_p": 0.1,

        // 3. Frequency Penalty: Memberi hukuman jika model mengulang-ulang kalimat (looping).
        "frequency_penalty": 0.5, 

        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        // Prompt khusus untuk ekstraksi KTP Indonesia
                        "text": "<image>\nExtract all text from this Indonesian ID card (KTP). Output as JSON with fields: NIK, Nama, Tempat/Tgl Lahir, Jenis Kelamin, Alamat, RT/RW, Kel/Desa, Kecamatan, Agama, Status Perkawinan, Pekerjaan, Kewarganegaraan. Do not translate. Do not add markdown formatting."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": data_url
                        }
                    }
                ]
            }
        ],
        // Max tokens tetap ada sebagai safety net, tapi dengan setting di atas
        // model seharusnya berhenti jauh sebelum mencapai angka ini.
        "max_tokens": 1000
    });
    println!("Mengirim request ke server Linux: {} ...", SERVER_URL);

    // 3. Kirim Request HTTP POST
    let client = reqwest::Client::new();
    let res = client.post(SERVER_URL)
        .header("Content-Type", "application/json")
        .header("Authorization", format!("Bearer {}", api_token))
        .json(&payload)
        .send()
        .await?;

    // 4. Proses Response
    if res.status().is_success() {
        let response_body: serde_json::Value = res.json().await?;
        
        // Ambil isi text dari struktur JSON OpenAI
        if let Some(content) = response_body["choices"][0]["message"]["content"].as_str() {
            println!("\n--- HASIL OCR ---");
            println!("{}", content);
        } else {
            println!("Format response tidak sesuai: {:?}", response_body);
        }
    } else {
        println!("Error dari server: Status: {}", res.status());
        let error_text = res.text().await?;
        println!("Detail: {}", error_text);
    }

    Ok(())
}