use reqwest::Client;
use std::fs;

const DROPBOX_API: &str = "https://api.dropboxapi.com/2";
const DROPBOX_CONTENT: &str = "https://content.dropboxapi.com/2";

pub async fn download(token: &str, remote_path: &str, local_path: &str) {
    let client = Client::new();
    let body = serde_json::json!({ "path": remote_path });

    let resp = client
        .post(format!("{DROPBOX_CONTENT}/files/download"))
        .header("Authorization", format!("Bearer {token}"))
        .header("Dropbox-API-Arg", body.to_string())
        .send()
        .await
        .expect("下载请求失败");

    if !resp.status().is_success() {
        let status = resp.status();
        let text = resp.text().await.unwrap_or_default();
        eprintln!("下载失败 [{status}]: {text}");
        return;
    }

    let bytes = resp.bytes().await.expect("读取响应失败");
    fs::write(local_path, &bytes).expect("写入本地文件失败");
    println!(
        "✓ 已下载: {remote_path} → {local_path} ({} 字节)",
        bytes.len()
    );
}

pub async fn upload(token: &str, local_path: &str, remote_path: &str) {
    let data = fs::read(local_path).expect("读取本地文件失败");
    let client = Client::new();

    let arg = serde_json::json!({
        "path": remote_path,
        "mode": "overwrite",
    });

    let resp = client
        .post(format!("{DROPBOX_CONTENT}/files/upload"))
        .header("Authorization", format!("Bearer {token}"))
        .header("Dropbox-API-Arg", arg.to_string())
        .header("Content-Type", "application/octet-stream")
        .body(data.clone())
        .send()
        .await
        .expect("上传请求失败");

    if !resp.status().is_success() {
        let status = resp.status();
        let text = resp.text().await.unwrap_or_default();
        eprintln!("上传失败 [{status}]: {text}");
        return;
    }

    println!(
        "✓ 已上传: {local_path} → {remote_path} ({} 字节)",
        data.len()
    );
}

pub async fn list_files(token: &str, path: &str) {
    let client = Client::new();
    let body = serde_json::json!({
        "path": if path.is_empty() { "" } else { path },
        "recursive": false,
    });

    let resp = client
        .post(format!("{DROPBOX_API}/files/list_folder"))
        .header("Authorization", format!("Bearer {token}"))
        .json(&body)
        .send()
        .await
        .expect("列出目录失败");

    if !resp.status().is_success() {
        let status = resp.status();
        let text = resp.text().await.unwrap_or_default();
        eprintln!("列出目录失败 [{status}]: {text}");
        return;
    }

    let json: serde_json::Value = resp.json().await.expect("解析响应失败");
    let entries = json["entries"].as_array().unwrap();

    if entries.is_empty() {
        println!("（空目录）");
        return;
    }

    for entry in entries {
        let name = entry["name"].as_str().unwrap_or("?");
        let tag = entry[".tag"].as_str().unwrap_or("?");
        let size = entry["size"].as_u64().unwrap_or(0);
        if tag == "folder" {
            println!("📁 {name}/");
        } else {
            let size_str = if size > 1024 * 1024 {
                format!("{:.1} MB", size as f64 / (1024.0 * 1024.0))
            } else if size > 1024 {
                format!("{:.1} KB", size as f64 / 1024.0)
            } else {
                format!("{size} B")
            };
            println!("📄 {name:50} {size_str:>10}");
        }
    }
}
