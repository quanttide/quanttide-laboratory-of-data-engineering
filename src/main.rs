mod dropbox;

use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(
    name = "dropbox",
    about = "基于 Dropbox 的数据传输工具（send / receive）"
)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// 发送文件：上传到网盘并生成分享链接，把链接给对方
    Send {
        /// 本地文件路径
        file: String,
        /// Dropbox 存储路径，如 /Customers/ABC/result.csv
        /// 不指定则用文件名
        remote_path: Option<String>,
        /// 将链接写入文件（不指定则直接打印到终端）
        output: Option<String>,
    },
    /// 接收文件：从共享链接下载并保存到本地
    Receive {
        /// 共享链接，或可下载的 URL
        url: String,
        /// 本地保存路径，不指定则自动取名
        output: Option<String>,
    },
    /// 列出网盘中的客户目录
    Ls {
        /// 目录路径，默认为 /Customers
        path: Option<String>,
    },
}

#[tokio::main]
async fn main() {
    let cli = Cli::parse();

    let token =
        std::env::var("DROPBOX_ACCESS_TOKEN").expect("请设置 DROPBOX_ACCESS_TOKEN 环境变量");

    match &cli.command {
        Commands::Send {
            file,
            remote_path,
            output,
        } => {
            let remote = remote_path.clone().unwrap_or_else(|| {
                format!(
                    "/Customers/send/{}",
                    file.rsplit('/').next().unwrap_or("result")
                )
            });
            dropbox::upload(&token, file, &remote).await;

            match dropbox::create_shared_link(&token, &remote).await {
                Ok(url) => {
                    if let Some(out) = output {
                        std::fs::write(out, &url).expect("写入链接文件失败");
                        println!("✓ 链接已写入: {out}");
                    } else {
                        println!("{url}");
                    }
                }
                Err(e) => eprintln!("⚠ 上传成功，但生成分享链接失败: {e}"),
            }
        }
        Commands::Receive { url, output } => {
            let path = output
                .clone()
                .unwrap_or_else(|| url.rsplit('/').next().unwrap_or("received").to_string());
            dropbox::download_and_save(&token, url, &path).await;
        }
        Commands::Ls { path } => {
            let p = path.as_deref().unwrap_or("/Customers");
            dropbox::list_files(&token, p).await;
        }
    }
}
