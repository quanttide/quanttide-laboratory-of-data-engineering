use reqwest::Client;
use std::fs;

const DROPBOX_API: &str = "https://api.dropboxapi.com/2";
const DROPBOX_CONTENT: &str = "https://content.dropboxapi.com/2";

/// 上传文件到 Dropbox
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
        panic!("上传失败 [{status}]: {text}");
    }

    println!(
        "✓ 已上传: {local_path} → {remote_path} ({} 字节)",
        data.len()
    );
}

/// 从共享链接下载文件并保存到本地
pub async fn download_and_save(_token: &str, url: &str, local_path: &str) {
    let client = Client::new();

    // 确保 URL 以 ?dl=1 结尾以便直接下载
    let url = if url.contains("?dl=") {
        url.to_string()
    } else {
        format!("{url}?dl=1")
    };

    let resp = client.get(&url).send().await.expect("下载请求失败");

    if !resp.status().is_success() {
        let status = resp.status();
        let text = resp.text().await.unwrap_or_default();
        panic!("下载失败 [{status}]: {text}");
    }

    let bytes = resp.bytes().await.expect("读取响应失败");
    fs::write(local_path, &bytes).expect("写入本地文件失败");
    println!("✓ 已接收: {local_path} ({} 字节)", bytes.len());
}

/// 生成分享链接
pub async fn create_shared_link(token: &str, path: &str) -> Result<String, String> {
    let client = Client::new();
    let body = serde_json::json!({
        "path": path,
        "settings": { "requested_visibility": { ".tag": "public" } }
    });

    let resp = client
        .post(format!(
            "{DROPBOX_API}/sharing/create_shared_link_with_settings"
        ))
        .header("Authorization", format!("Bearer {token}"))
        .json(&body)
        .send()
        .await
        .map_err(|e| format!("请求失败: {e}"))?;

    let json: serde_json::Value = resp.json().await.map_err(|e| format!("解析失败: {e}"))?;

    if let Some(url) = json["url"].as_str() {
        Ok(url.replace("?dl=0", "?dl=1"))
    } else if let Some(error) = json["error_summary"].as_str() {
        Err(error.to_string())
    } else {
        Err(format!("未知响应: {json}"))
    }
}

/// 列出目录内容
pub async fn list_files(token: &str, path: &str) {
    let client = Client::new();
    let body = serde_json::json!({
        "path": path,
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
