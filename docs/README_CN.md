AI Assistant Tool 中文说明书  
（基于 2026-03-30 源码，作者 ZF）

一、工具定位  
一套命令行 AI 助手，支持 7 种运行模式：纯对话、本地文档检索（RAG）、联网搜索、混合检索、静默输出。所有模式共用同一套配置与历史记录，默认调用 Moonshot Kimi 系列模型，可通过本地代理隐藏真实 API-Key。

二、首次安装  
1. 系统要求  
   • Linux / macOS / WSL  
   • Python ≥ 3.12（必须，3.11 以下会缺 typing 特性）  
   • 端口 5260 未被占用（代理用）  

2. 一键安装  
git clone https://github.com/jumphone/ai.git  
cd ai  
pip install -r docs/requirements.txt          # 约 2.2 GB 依赖，含 torch、faiss、langchain  
chmod +x bin/*.py                             # 赋予可执行权限  

3. 初始化  
任意执行一次  
bin/ai.py “你好”  
首次会提示输入 ai-key：  
   • 若你有 Moonshot 官方 key，直接粘贴 sk- 开头字符串；  
   • 若你只想用同事搭好的代理，输入代理密码（对方会给）。  
验证通过后，~/.ai/ 目录自动生成，权限 700，内含 key 文件与背景规则。

三、目录结构速览  
~/.ai/  
├── bkg.txt              # 系统级背景规则（可改）  
├── key.txt              # 真实 API-Key（700 权限）  
├── pkey.txt             # 代理密码（700 权限）  
├── tmp/                 # 当日对话历史  
│   └── 20260330_tmp_ai_zhangfeng.txt  
├── log/                 # 运行日志  
├── database/            # 放本地文档（仅 .txt .md 被识别）  
└── vectorstore/         # FAISS 索引，由 ragindex 生成  

四、7 条命令对照表  
| 命令 | 本地文档 | 联网 | 流式输出 | 典型场景 |
|----|--------|------|--------|---------|
| ai | ×      | ×    | √      | 日常对话 |
| air | √     | ×    | √      | 查自己笔记 |
| aiw | ×     | √    | √      | 查实时信息 |
| aiwr | √    | √    | √      | 先全网搜，再对照本地笔记 |
| aiq | ×     | ×    | ×      | 脚本调用，无动画 |
| aiwq | ×    | √    | ×      | 静默联网，方便管道 |
| ragindex | - | - | - | 重建索引，文档变动后必跑 |

五、快速上手示例  
1. 纯对话  
bin/ai.py “用一句话解释量子计算”  

2. 把代码文件扔进去  
bin/ai.py src/config.py “帮我把 API_URL 改成 OpenAI 官方地址”  

3. 启用历史  
bin/ai.py usetmp                    # 当天再次执行 ai/air/aiw 会自动续写上下文  
bin/ai.py cleantmp                  # 清空并重建历史文件  
bin/ai.py stoptmp                   # 彻底关闭历史  

4. 本地知识库（RAG）  
# 步骤 1：把文档塞进数据库目录  
cp ~/论文/*.txt ~/.ai/database/  
# 步骤 2：建索引（首次或文档有变动都要跑）  
bin/ragindex.py                     # 看到 finished 即可  
# 步骤 3：提问  
bin/air.py “我去年写的关于微服务的段落在哪？”  

5. 联网搜索  
bin/aiw.py “2026 年 3 月 Python 3.13 发布了吗”  

6. 混合检索  
bin/aiwr.py “对比网上最新价格与我本地记录的采购价”  

7. 脚本静默调用  
bin/aiwq.py “北京今天气温” | grep -o ‘\d\+℃’  

六、代理服务器（多人共享 key）  
1. 在拥有真实 key 的机器启动代理  
bash server.sh                      # 默认 127.0.0.1:5260  
2. 其他同事只需在第一次输入代理密码（存在 ~/.ai/pkey.txt），即可通过本地代理转发请求，真实 key 不泄露。  
3. 代理日志实时打印请求与响应，方便审计。  

七、核心配置修改（src/config.py）  
• API_URL / PROXY_URL          # 换官方或其他中转  
• MODEL_LIST                   # 新增或调整模型别名  
• BASIC_MODEL                  # 默认对话模型  
• CHUNK_SIZE / CHUNK_OVERLAP   # RAG 文档切片大小  
• VECTOR_K                     # 检索返回条数  
• TEMPERATURE                  # 全局温度（默认 0.3）  

八、常见问题 FAQ  
1. 报错 “No sentence-transformers model found”  
   已自动屏蔽警告，不影响使用；若需彻底消除，请把 SEARCH_MODEL_PATH 指向完整模型目录（含 modules.json）。  

2. ragindex 失败  
   确认 ~/.ai/database/ 下有 .txt 或 .md；再跑一次即可，脚本会自动删除旧索引。  

3. 中文乱码  
   全部源码强制 UTF-8，如遇终端乱码，请设置  
   export LANG=zh_CN.UTF-8  

4. 端口被占  
   lsof -i :5260  
   kill 对应进程，或改 server.sh 里的端口。  

5. 历史文件越来越大  
   tmp 文件按天生成的，次日自动换文件；若单天记录过多可手动 cleantmp。  

九、语音输入（可选）  
supp/ 目录提供 macOS 语音方案：  
• voice2ssh_mac.py – 按住右 Command 录音，实时上传到 Linux 服务器；  
• ssh2ai.py – 在服务器端循环监听，把转写文本自动喂给 bin/ai。  
需额外安装 faster-whisper、sounddevice、paramiko。  

十、卸载  
pip uninstall -r docs/requirements.txt -y  
rm -rf ~/.ai/               # 配置与历史  
rm -rf ai/                  # 源码目录  

十一、更新日志  
2026-03-30 首版文档，对应代码 commit 日期。后续更新请跟踪 GitHub 仓库。
