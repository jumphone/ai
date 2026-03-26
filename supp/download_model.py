#/home/toolkit/local_py312/bin/python3

from huggingface_hub import snapshot_download

# 直接下载模型，不需要 CLI！
print("开始下载...")

snapshot_download(
    repo_id="Qwen/Qwen3-Embedding-8B",
    local_dir="/home/toolkit/tools/ai_local_src/models/Qwen3-Embedding-8B",
    local_dir_use_symlinks=False,
    resume_download=True,
)

print("下载完成")

