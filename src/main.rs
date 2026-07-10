mod dropbox;

use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(name = "dropbox", about = "基于 Dropbox 的客户数据传输工具")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// 存到自己的网盘：从共享链接或本地文件存入 Dropbox
    Store {
        /// 共享链接 或 本地文件路径
        source: String,
        /// Dropbox 存储路径，如 /Customers/ABC/data.csv
        /// 不指定则自动生成
        destination: Option<String>,
    },
    /// 生成分享链接：输出可发给客户/合作伙伴的下载链接
    Share {
        /// Dropbox 中的文件路径，或本地文件路径（自动先上传）
        path: String,
        /// 将链接写入文件（不指定则直接打印）
        output: Option<String>,
    },
    /// 列出自己网盘中的客户目录
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
        Commands::Store {
            source,
            destination,
        } => {
            let dest = destination.clone().unwrap_or_else(|| {
                format!(
                    "/Customers/incoming/{}",
                    source.rsplit('/').next().unwrap_or("unknown")
                )
            });
            dropbox::store(&token, source, &dest).await;
        }
        Commands::Share { path, output } => {
            let remote_path = if path.starts_with('/') {
                // 已经是 Dropbox 路径，直接生成链接
                path.clone()
            } else {
                // 本地文件，先上传到 Dropbox
                let remote = format!(
                    "/Customers/deliver/{}",
                    path.rsplit('/').next().unwrap_or("result")
                );
                dropbox::upload(&token, path, &remote).await;
                remote
            };

            match dropbox::create_shared_link(&token, &remote_path).await {
                Ok(url) => {
                    if let Some(out) = output {
                        std::fs::write(out, &url).expect("写入链接文件失败");
                        println!("✓ 分享链接已写入: {out}");
                    } else {
                        println!("{url}");
                    }
                }
                Err(e) => eprintln!("生成分享链接失败: {e}"),
            }
        }
        Commands::Ls { path } => {
            let p = path.as_deref().unwrap_or("/Customers");
            dropbox::list_files(&token, p).await;
        }
    }
}
