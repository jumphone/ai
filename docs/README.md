# AI Assistant Tool

Date: 2026.03.26 | Author: https://github.com/jumphone/

A command-line AI assistant supporting multiple interaction modes: basic chat, RAG retrieval, web search, and combined capabilities. Built with Moonshot AI's Kimi models.

## Features

- **ai**: Basic AI chat with conversation history
- **air**: AI chat with local document retrieval (RAG)
- **aiw**: AI chat with web search capability
- **aiwr**: AI chat with both web search and RAG
- **ragindex**: Build FAISS vector store from local documents

## Installation

```bash
# Python 3.12 required
pip install -r docs/requirements.txt
```

## Configuration

### API Key Setup

First run will prompt for "ai-key". Users can input:
- Real Moonshot API key (sk-...)
- Password from host's `~/.ai/pkey.txt`

The tool validates against:
1. `API_URL='https://api.moonshot.cn/v1'` (real endpoint)
2. `PROXY_URL='http://127.0.0.1:5260/v1'` (local proxy)

Validated keys are stored in:
- `~/.ai/key.txt` (real key)
- `~/.ai/pkey.txt` (proxy password)

### Document Setup

Place text/markdown files in `~/.ai/database/` for RAG. Supported extensions: `.txt`, `.md`

### Vector Store

Build index before using RAG features:

```bash
bin/ragindex.py
```

## Usage

### Basic Chat
```bash
bin/ai.py "Your question"
bin/ai.py file.txt  # Include file content
```

### RAG Mode
```bash
bin/air.py "question about your documents"
```

### Web Search Mode
```bash
bin/aiw.py "current events question"
```

### Combined Mode
```bash
bin/aiwr.py "complex question needing both"
```

### Conversation Management
```bash
bin/ai.py usetmp    # Enable history
bin/ai.py cleantmp  # Reset history
bin/ai.py stoptmp   # Disable history
```

### Proxy Server
```bash
# Run FastAPI proxy for key protection
bash server.sh
# Server runs at http://127.0.0.1:5260
```

## File Structure

```
.
├── bin/                      # Executable scripts
│   ├── ai.py                # Basic AI
│   ├── air.py               # AI + RAG
│   ├── aiw.py               # AI + Web
│   ├── aiwr.py              # AI + Web + RAG
│   └── ragindex.py          # Build vector store
├── mains/                    # Main logic modules
│   ├── main_ai.py
│   ├── main_air.py
│   ├── main_aiw.py
│   ├── main_aiwr.py
│   └── main_ragindex.py
├── src/                      # Core modules
│   ├── check.py             # API verification
│   ├── config.py            # Configuration
│   ├── safe.py              # Safe functions
│   ├── prepare.py           # Initialization
│   ├── rag.py               # RAG implementation
│   ├── util.py              # Utilities
│   └── server.py            # FastAPI proxy
├── docs/
│   └── requirements.txt     # Python dependencies
└── server.sh                # Server startup script
```

## Key Paths

- `~/.ai/`: Main configuration folder (700 permissions)
- `~/.ai/bkg.txt`: System background rules
- `~/.ai/tmp/`: Conversation history (daily files per user)
- `~/.ai/log/`: Interaction logs (daily files per user)
- `~/.ai/database/`: RAG source documents
- `~/.ai/vectorstore/`: FAISS index
- `~/.ai/key.txt`: Real API key
- `~/.ai/pkey.txt`: Proxy password

## Models

- **Chat**: `kimi-k2-thinking-turbo` (default, `BASIC_MODEL`)
- **RAG Keyword**: `kimi-k2-turbo-preview` (`RAG_KEYWORD_MODEL`)
- **RAG Check**: `kimi-k2-turbo-preview` (`RAG_CHECK_MODEL`)
- **Embeddings**: Local HuggingFace model at `/home/toolkit/tools/ai_local_src/models/multilingual-model`

## Background Rules

Default system prompt (`DEFAULT_BKG`):
- Factual statements only
- No speculation/fabrication
- No invented references
- Direct, concise responses
- Must answer even when uncertain

## Technical Details

- **RAG**: FAISS vector store with `CHUNK_SIZE=5000`, `CHUNK_OVERLAP=500`, `VECTOR_K=10`
- **Web Search**: Moonshot's builtin `$web_search` tool
- **History**: Stored in `~/.ai/tmp/YYYYMMDD_tmp_ai_<user>.txt`
- **Logging**: Stored in `~/.ai/log/YYYYMMDD_log_ai_<user>.txt`
- **Temperature**: `TEMPERATURE=0.3` (chat), `RAG_KEYWORD_TEMPERATURE=0.2`, `RAG_CHECK_TEMPERATURE=0.0`
- **Proxy**: FastAPI server at port 5260 with token validation

## Security Notes

- Configuration folder has 700 permissions
- Password input masked with asterisks (`getpass_star`)
- Real API keys stored only in host account
- Proxy server validates tokens before forwarding
- Key files created with 700 permissions

## Requirements

- Python 3.12
- Moonshot AI API key
- Local embedding model (for RAG)
- CUDA libraries (optional, for GPU acceleration)
