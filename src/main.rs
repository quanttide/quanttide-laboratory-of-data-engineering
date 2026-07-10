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
    /// 接收：从客户（共享链接或本地文件）存到自己的网盘
    Receive {
        /// 客户共享链接，或本地文件路径
        source: String,
        /// 存到 Dropbox 的路径，如 /Customers/ABC/raw.csv
        /// 不指定则自动生成路径
        destination: Option<String>,
    },
    /// 交付：将结果上传到自己的网盘，输出分享链接
    Deliver {
        /// 本地结果文件路径
        file: String,
        /// Dropbox 存储路径，如 /Customers/ABC/result.csv
        /// 不指定则用文件名
        remote_path: Option<String>,
        /// 直接打印分享链接（不写入文件）
        #[arg(long)]
        print: bool,
        /// 将分享链接写入文件
        #[arg(long)]
        output: Option<String>,
    },
    /// 列出自己网盘中的客户目录
    Ls {
        /// 目录路径，默认为 /Customers
        path: Option<String>,
    },
    /// 生成文件的分享链接
    Share {
        /// Dropbox 中的文件路径
        path: String,
    },
}

#[tokio::main]
async fn main() {
    let cli = Cli::parse();

    let token =
        std::env::var("DROPBOX_ACCESS_TOKEN").expect("请设置 DROPBOX_ACCESS_TOKEN 环境变量");

    match &cli.command {
        Commands::Receive {
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
            println!("✓ 已存到自己的网盘: {dest}");
        }
        Commands::Deliver {
            file,
            remote_path,
            print,
            output,
        } => {
            let path = remote_path.clone().unwrap_or_else(|| {
                format!(
                    "/Customers/deliver/{}",
                    file.rsplit('/').next().unwrap_or("result")
                )
            });
            dropbox::upload(&token, file, &path).await;

            // 生成分享链接
            let link = dropbox::create_shared_link(&token, &path).await;
            match link {
                Ok(url) => {
                    if *print {
                        println!("{url}");
                    } else if let Some(out) = output {
                        std::fs::write(out, &url).expect("写入链接文件失败");
                        println!("✓ 分享链接已写入: {out}");
                    } else {
                        println!("📎 客户下载链接: {url}");
                    }
                }
                Err(e) => eprintln!("⚠ 文件已上传，但生成分享链接失败: {e}"),
            }
        }
        Commands::Ls { path } => {
            let p = path.as_deref().unwrap_or("/Customers");
            dropbox::list_files(&token, p).await;
        }
        Commands::Share { path } => match dropbox::create_shared_link(&token, path).await {
            Ok(url) => println!("{url}"),
            Err(e) => eprintln!("生成分享链接失败: {e}"),
        },
    }
}
