# AI Assistant Tool 中文说明书

**日期：** 2026.03.26  
**作者：** https://github.com/jumphone/  
**Python 版本要求：** 3.12+

一个支持多种交互模式的命令行 AI 助手，包括基础聊天、本地文档检索（RAG）、网络搜索及组合功能。基于 Moonshot AI 的 Kimi 模型和 FastAPI 代理实现安全的 API 密钥管理。

---

## 功能矩阵

| 命令 | 模式 | RAG | 网络搜索 | 流式输出 | 说明 |
|------|------|-----|----------|----------|------|
| `ai` | 基础聊天 | ❌ | ❌ | ✅ | 标准对话，支持历史记录 |
| `air` | AI + RAG | ✅ | ❌ | ✅ | 搜索本地文档 |
| `aiw` | AI + 网络 | ❌ | ✅ | ✅ | 搜索互联网 |
| `aiwr` | AI + 网络 + RAG | ✅ | ✅ | ✅ | 组合搜索 |
| `aiq` | 静默聊天 | ❌ | ❌ | ❌ | 非流式输出，适合脚本 |
| `aiwq` | 静默网络 | ❌ | ✅ | ❌ | 非流式网络搜索 |
| `ragindex` | 索引构建 | - | - | - | 构建 FAISS 向量存储 |

---

## 安装

```bash
# 克隆仓库
git clone <repository-url>
cd ai-assistant

# 安装 Python 3.12 依赖
pip install -r docs/requirements.txt

# 验证安装
python3 bin/ai.py --help  # 首次运行会提示输入 API 密钥
```

---

## 配置

### 初始设置

首次运行时，工具会提示输入 "ai-key"。可提供：

1. **真实的 Moonshot API 密钥**（格式：`sk-...`）
2. **代理密码**（来自主机的 `~/.ai/pkey.txt`）

密钥会验证两个端点：
- `API_URL='https://api.moonshot.cn/v1'`（真实端点）
- `PROXY_URL='http://127.0.0.1:5260/v1'`（本地代理）

验证通过的凭证存储在：
- `~/.ai/key.txt` - 真实 API 密钥（权限 700）
- `~/.ai/pkey.txt` - 代理密码（权限 700）

### 目录结构

工具创建 `~/.ai/` 目录，权限为 700：

```
~/.ai/
├── bkg.txt              # 系统背景规则
├── key.txt              # 真实 API 密钥
├── pkey.txt             # 代理密码
├── tmp/                 # 对话历史
│   └── YYYYMMDD_tmp_ai_<user>.txt
├── log/                 # 交互日志
│   └── YYYYMMDD_log_ai_<user>.txt
├── database/            # RAG 源文档（.txt, .md）
└── vectorstore/         # FAISS 索引
```

### 背景规则

默认系统提示（`src/prepare.py:DEFAULT_BKG`）：

```
1. 只陈述真实的内容，不猜测、不编造。
2. 不知道、不确定、没有把握的内容，直接说不知道，不要编造。
3. 不虚构人名、地名、时间、数据、论文、文献、标题、作者、来源。
4. 不夸张、不脑补、不美化。
5. 如果需要引用，只引用真实存在的内容，不编造引用。
6. 回答直接、无冗余的语气。
7. 一定要回答，不可靠也给一个最可靠的结论。
```

---

## 使用

### 基础聊天

```bash
# 简单查询
bin/ai.py "Python 是什么？"

# 包含文件内容
bin/ai.py document.txt "总结这个"

# 启用对话历史
bin/ai.py usetmp
```

### RAG 模式（本地文档）

```bash
# 1. 将文档放入 ~/.ai/database/
cp my_notes.md ~/.ai/database/

# 2. 构建向量索引
bin/ragindex.py

# 3. 查询文档
bin/air.py "我写了关于认证的什么内容？"
```

### 网络搜索模式

```bash
# 查询当前事件和互联网信息
bin/aiw.py "Python 3.12 最新特性"
```

### 组合模式

```bash
# 同时搜索互联网和本地文档
bin/aiwr.py "将云服务商与我的内部笔记进行比较"
```

### 静默模式（非流式）

```bash
# 适合脚本和管道
bin/aiq.py "计算 2+2" > result.txt
bin/aiwq.py "当前比特币价格" | grep -i price
```

### 对话管理

```bash
bin/ai.py usetmp     # 为当天启用历史记录
bin/ai.py cleantmp   # 重置历史（删除并重建）
bin/ai.py stoptmp    # 禁用历史（删除 tmp 文件）
```

### 代理服务器

```bash
# 启动 FastAPI 代理以保护密钥
bash server.sh

# 服务器运行在 http://127.0.0.1:5260
# 配置客户端使用此端点
```

---

## 架构

### 关键函数

- `loadBKG()` - 加载系统提示和时间戳
- `loadTMP()` - 从 `~/.ai/tmp/` 加载对话历史
- `loadNEW()` - 处理 CLI 参数（文件或文本）
- `getResult()` - 标准流式聊天
- `getResult_web()` - 带网络搜索工具的聊天
- `retrieve_rag()` - 带双重检查的 RAG 检索
- `build_vectorstore()` - FAISS 索引管理

### RAG 流程

1. **关键词生成**（`RAG_KEYWORD_MODEL`）：提取搜索意图
2. **向量检索**：FAISS 相似度搜索（`VECTOR_K=10`）
3. **双重检查**（`RAG_CHECK_MODEL`）：验证相关性（temperature=0.0）
4. **答案生成**：结合参考资料与用户查询

### 网络搜索集成

使用 Moonshot 内置的 `$web_search` 工具（`src/util.py:chat()`）。工具在每个请求中声明，自动处理工具调用。

---

## 文件结构

```
.
├── bin/                      # 可执行入口
│   ├── ai.py                # 基础聊天
│   ├── air.py               # + RAG
│   ├── aiw.py               # + 网络
│   ├── aiwr.py              # + 网络 + RAG
│   ├── aiq.py               # 静默模式
│   ├── aiwq.py              # 静默网络
│   └── ragindex.py          # 构建索引
├── mains/                    # 主逻辑模块
│   ├── main_ai.py
│   ├── main_air.py
│   ├── main_aiw.py
│   ├── main_aiwr.py
│   ├── main_aiq.py
│   ├── main_aiwq.py
│   └── main_ragindex.py
├── src/                      # 核心实现
│   ├── check.py             # API 密钥验证
│   ├── config.py            # 配置常量
│   ├── safe.py              # 安全密码输入
│   ├── prepare.py           # 目录初始化
│   ├── rag.py               # FAISS 和嵌入
│   ├── util.py              # 主要工具函数
│   └── server.py            # FastAPI 代理
├── docs/
│   └── requirements.txt     # Python 依赖
└── server.sh                # 代理启动脚本
```

---

## 安全特性

- **密钥保护**：代理服务器在转发到真实 API 前验证令牌
- **文件权限**：`~/.ai/` 目录以 700 权限创建
- **安全输入**：`getpass_star()` 实现密码掩码（`src/safe.py`）
- **密钥存储**：真实密钥和代理密码分开存储
- **无密钥暴露**：客户端应用使用代理密码，而非真实 API 密钥

### 代理服务器详情

- **端点**：`http://127.0.0.1:5260/v1`
- **验证**：对照 `PROXY_API_KEY` 列表检查令牌
- **转发**：注入真实 API 密钥，剥离敏感头
- **日志**：将请求体和流式响应打印到 stdout
- **CORS**：未配置（仅用于本地）

---

## 配置参考

### 模型（`src/config.py`）

```python
BASIC_MODEL = 'kimi-k2-thinking-turbo'  # 默认聊天模型
RAG_KEYWORD_MODEL = 'kimi-k2-turbo-preview'  # 搜索意图提取
RAG_CHECK_MODEL = 'kimi-k2-turbo-preview'  # 相关性验证
```

### RAG 参数

```python
CHUNK_SIZE = 5000          # 文档块大小
CHUNK_OVERLAP = 500        # 块重叠
VECTOR_K = 10              # 检索块数
RAG_KEYWORD_TEMPERATURE = 0.2
RAG_CHECK_TEMPERATURE = 0.0  # 确定性检查
```

### 路径

```python
AI_FOLDER = '~/.ai/'
RAG_SRC_DATABASE = '~/.ai/database/'
RAG_SRC_VECTOR = '~/.ai/vectorstore/'
SEARCH_MODEL_PATH = '/home/toolkit/tools/ai_local_src/models/multilingual-model'
```

---

## 故障排除

### "No sentence-transformers model found"

工具通过 `warnings.filterwarnings()` 和 `sys.stderr` 重定向在 `src/rag.py:init_huggingface_embeddings()` 中抑制此警告。确保 `SEARCH_MODEL_PATH` 包含有效的模型文件。

### 密钥验证失败

1. 检查到 `API_URL` 和 `PROXY_URL` 的网络连接
2. 验证密钥格式（应以 `sk-` 开头）
3. 检查 `~/.ai/key.txt` 和 `~/.ai/pkey.txt` 的权限
4. 使用 `src/safe.py` 中的 `fast_verify_key()` 进行手动测试

### RAG 无结果

1. 确认 `~/.ai/database/` 中的文档（`.txt` 或 `.md`）
2. 重建索引：`bin/ragindex.py`
3. 检查嵌入模型路径：`SEARCH_MODEL_PATH`
4. 验证 `VECTOR_K` 值是否过小

### 历史记录未保存

1. 运行 `bin/ai.py usetmp` 创建临时文件
2. 检查 `~/.ai/tmp/` 权限（应为 700）
3. 验证 `src/prepare.py` 中 `TMP_USE` 为 `True`

### 代理服务器错误

1. 确保端口 5260 可用：`lsof -i :5260`
2. 检查 `PROXY_KEY_FILE` 是否存在且包含有效令牌
3. 查看服务器日志获取请求/响应详情

---

## 开发

### 添加新命令

1. 创建 `bin/newcmd.py` 并添加 shebang 和导入
2. 添加 `mains/main_newcmd.py` 及 `run()` 函数
3. 在 `src/util.py` 或新模块中实现逻辑
4. 更新本 README 中的功能矩阵

### 修改模型

编辑 `src/config.py:MODEL_LIST` 和 `BASIC_MODEL`。更改在下次运行时立即生效。

### 自定义嵌入

更新 `src/config.py` 中的 `SEARCH_MODEL_PATH`。工具需要 HuggingFace 兼容模型。

### 扩展代理

修改 `src/server.py:PROXY_API_KEY` 以支持多个客户端令牌。在 FastAPI 应用中按需添加路由。

---

## 依赖

完整列表见 `docs/requirements.txt`。主要依赖：

- **AI/ML**：`torch==2.6.0`, `transformers==5.3.0`, `sentence-transformers==5.3.0`
- **RAG**：`langchain==1.2.13`, `faiss-cpu==1.8.0`, `langchain-huggingface==1.2.1`
- **API**：`openai==1.60.0`, `httpx==0.25.2`, `fastapi==0.135.2`
- **工具**：`pydantic==2.12.5`, `python-dotenv==1.2.2`, `PyYAML==6.0.3`

CUDA 库为可选，用于 GPU 加速支持。

---
