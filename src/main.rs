mod dropbox;

use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(name = "dropbox", about = "Dropbox 数据传输工具")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// 从 Dropbox 下载文件
    Pull {
        /// Dropbox 上的远程路径，如 /data/input.csv
        remote_path: String,
        /// 本地保存路径，默认与远程文件名相同
        local_path: Option<String>,
    },
    /// 上传文件到 Dropbox
    Push {
        /// 本地文件路径
        local_path: String,
        /// Dropbox 上的远程路径，如 /data/output.csv
        remote_path: String,
    },
    /// 列出 Dropbox 文件夹内容
    Ls {
        /// 远程文件夹路径，默认为 /
        path: Option<String>,
    },
}

#[tokio::main]
async fn main() {
    let cli = Cli::parse();

    let token =
        std::env::var("DROPBOX_ACCESS_TOKEN").expect("请设置 DROPBOX_ACCESS_TOKEN 环境变量");

    match &cli.command {
        Commands::Pull {
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
        Commands::Push {
            local_path,
            remote_path,
        } => {
            dropbox::upload(&token, local_path, remote_path).await;
        }
        Commands::Ls { path } => {
            let p = path.as_deref().unwrap_or("");
            dropbox::list_files(&token, p).await;
        }
    }
}
