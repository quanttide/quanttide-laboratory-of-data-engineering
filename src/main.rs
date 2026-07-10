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
    /// 接收：从客户共享目录下载文件
    Receive {
        /// 客户共享目录路径，如 /Customers/ABC/input.csv
        remote_path: String,
        /// 本地保存路径，默认与远程文件名相同
        local_path: Option<String>,
    },
    /// 交付：上传处理结果到客户共享目录
    Deliver {
        /// 本地文件路径
        local_path: String,
        /// 客户共享目录路径，如 /Customers/ABC/output.csv
        remote_path: String,
    },
    /// 列出客户目录内容
    Ls {
        /// 远程文件夹路径，默认为 /Customers
        path: Option<String>,
    },
}

#[tokio::main]
async fn main() {
    let cli = Cli::parse();

    let token =
        std::env::var("DROPBOX_ACCESS_TOKEN").expect("请设置 DROPBOX_ACCESS_TOKEN 环境变量");

    match &cli.command {
        Commands::Receive {
            remote_path,
            local_path,
        } => {
            let path = local_path.clone().unwrap_or_else(|| {
                remote_path
                    .rsplit('/')
                    .next()
                    .unwrap_or("download")
                    .to_string()
            });
            dropbox::download(&token, remote_path, &path).await;
        }
        Commands::Deliver {
            local_path,
            remote_path,
        } => {
            dropbox::upload(&token, local_path, remote_path).await;
        }
        Commands::Ls { path } => {
            let p = path.as_deref().unwrap_or("/Customers");
            dropbox::list_files(&token, p).await;
        }
    }
}
