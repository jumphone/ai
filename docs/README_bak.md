# AI Assistant Tool

Date: 2026.03.26 | Author: https://github.com/jumphone/

A command-line AI assistant supporting multiple interaction modes: basic chat, RAG retrieval, web search, and combined capabilities. Built with Moonshot AI's Kimi models.

## Features

- **ai**: Basic AI chat with conversation history
- **air**: AI chat with local document retrieval (RAG)
- **aiw**: AI chat with web search capability
- **aiwr**: AI chat with both web search and RAG
- **keyenc**: AES encryption for API keys
- **ragindex**: Build FAISS vector store from local documents

## Installation

```bash
# Python 3.12 required
pip install -r docs/requirements.txt
```

## Configuration

### API Key Setup

First run will ask for "api-key":

Users can input the "real api-key" (starting with "sk-") or the password shared by the host (~/hostdir/.ai/pkey.txt)

```bash
# For AI service host account
# Place the plain key in ~/.ai/key.txt:
# Place the password in ~/.ai/pkey.txt, share the password with other users
```

The tool tries:
1. `~/.ai/key.txt` (real api-key)
2. password for the password shared by the host

### Document Setup

Place text or markdown files in `~/.ai/database/` for RAG.

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
│   ├── safe.py               # Safe related functions
│   ├── prepare.py           # Initialization
│   ├── rag.py               # RAG implementation
│   └── util.py              # Utilities
└── docs/
    └── requirements.txt     # Python dependencies
```

## Key Paths

- `~/.ai/`: Main configuration folder (700 permissions)
- `~/.ai/bkg.txt`: System background rules
- `~/.ai/tmp/`: Conversation history
- `~/.ai/log/`: Interaction logs
- `~/.ai/database/`: RAG source documents
- `~/.ai/vectorstore/`: FAISS index

## Models

- **Chat**: `kimi-k2-thinking-turbo` (default)
- **RAG Keyword**: `kimi-k2-turbo-preview`
- **RAG Check**: `kimi-k2-turbo-preview`
- **Embeddings**: Local HuggingFace model at `/home/toolkit/tools/ai_local_src/models/multilingual-model`

## Background Rules

Default system prompt enforces:
- Factual statements only
- No speculation/fabrication
- No invented references
- Direct, concise responses
- Must answer even when uncertain

## Technical Details

- **RAG**: FAISS vector store with 5000-char chunks, 500-char overlap
- **Web Search**: Moonshot's builtin `$web_search` tool
- **History**: Daily temp files per user
- **Logging**: Daily log files per user

## Requirements

- Python 3.12
- Moonshot AI API key
- Local embedding model (for RAG)

## Security Notes

- Real API keys stored in the host account
- Configuration folder has 700 permissions
- Password input masked with asterisks
