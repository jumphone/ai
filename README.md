# AI Assistant Tool

**Date:** 2026.03.30

**Author:** ZF, https://github.com/jumphone/

**Python:** 3.12+ required

A command-line AI assistant supporting multiple interaction modes: basic chat, local document retrieval (RAG), web search, and combined capabilities. Built with Moonshot AI's Kimi models and FastAPI proxy for secure API key management. Includes optional voice input support for macOS.

---

## Feature Matrix

| Command | Mode | RAG | Web Search | Verbose Output | Description |
|---------|------|-----|------------|----------------|-------------|
| `ai` | Basic Chat | ❌ | ❌ | ✅ | Standard conversation with history |
| `air` | AI + RAG | ✅ | ❌ | ✅ | Search local documents |
| `aiw` | AI + Web | ❌ | ✅ | ✅ | Search internet |
| `aiwr` | AI + Web + RAG | ✅ | ✅ | ✅ | Combined search |
| `aiq` | Quiet Chat | ❌ | ❌ | ❌ | Non-streaming output |
| `aiwq` | Quiet Web | ❌ | ✅ | ❌ | Non-streaming web search |
| `ragindex` | Index Builder | - | - | - | Build FAISS vector store |

---

## Installation

```bash
# Clone repository
git clone https://github.com/jumphone/ai.git
cd ai

# Install Python 3.12 dependencies
pip install -r docs/requirements.txt

# Verify installation
python3 bin/ai.py "who are you"  # Will prompt for API key on first run
```

---

## Configuration

### Initial Setup

On first run, the tool prompts for an "ai-key". You can provide:

1. **Real Moonshot API key** (format: `sk-...`)
2. **Proxy password** (from host's `~/.ai/pkey.txt`)

The key is validated against two endpoints:
- `API_URL='https://api.moonshot.cn/v1'` (real endpoint)
- `PROXY_URL='http://127.0.0.1:5260/v1'` (local proxy)

Validated credentials are stored in:
- `~/.ai/key.txt` - Real API key (700 permissions)
- `~/.ai/pkey.txt` - Proxy password (700 permissions)

### Directory Structure

The tool creates `~/.ai/` with 700 permissions:

```
~/.ai/
├── bkg.txt              # System background rules
├── key.txt              # Real API key
├── pkey.txt             # Proxy password
├── tmp/                 # Conversation history
│   └── YYYYMMDD_tmp_ai_<user>.txt
├── log/                 # Interaction logs
│   └── YYYYMMDD_log_ai_<user>.txt
├── database/            # RAG source documents (.txt, .md)
└── vectorstore/         # FAISS index
```

### Background Rules

Default system prompt (`src/prepare.py:DEFAULT_BKG`):

```
1. Only state factual content, do not guess or fabricate.
2. For unknown, uncertain, or unconfirmed content, directly state "I don't know", do not invent.
3. Do not fabricate names of people, places, times, data, papers, literature, titles, authors, or sources.
4. Do not exaggerate, imagine, or embellish.
5. If citation is needed, only cite content that actually exists, do not fabricate citations.
6. Respond directly without redundant tone.
7. Must answer, provide the most reliable conclusion even if uncertain.
```

---

## Usage

### Basic Chat

```bash
# Simple query
bin/ai.py "What is Python?"

# Include file content
bin/ai.py document.txt "Summarize this"

# Enable conversation history
bin/ai.py usetmp
```

### RAG Quick Start Guide

```
0. Run "ai" at least once to initialize the ai resource folder.
1. Upload all PDF files (ending with lowercase ".pdf") to a new empty folder on your Linux server.
2. Use the "cd" command to enter that folder, then type "dirpdf2txt ./" (copy-paste the quoted content to avoid errors).
3. Use "cp ./*.txt ~/.ai/database/" (same principle, copy-paste the quoted content).
4. Type "ragindex". It may report errors, ignore them. If it errors, run again until it shows "finished".
5. Use "air" to ask questions that will search the database before responding.

# Note: If you only have txt documents, skip step 2. Run "cp ./*.txt ~/.ai/database/" then proceed to steps 4-5.
```

### RAG Mode (Local Documents)

```bash
# 1. Place documents in ~/.ai/database/
cp my_notes.md ~/.ai/database/

# 2. Build vector index
bin/ragindex.py

# 3. Query documents
bin/air.py "What did I write about authentication?"
```

### Web Search Mode

```bash
# Current events and internet queries
bin/aiw.py "Latest Python 3.12 features"
```

### Combined Mode

```bash
# Search both internet and local documents
bin/aiwr.py "Compare cloud providers with my internal notes"
```

### Quiet Mode (Non-Streaming)

```bash
# For scripting and piping
bin/aiq.py "Calculate 2+2" > result.txt
bin/aiwq.py "Current Bitcoin price" | grep -i price
```

### Conversation Management

```bash
bin/ai.py usetmp     # Enable history for current day
bin/ai.py cleantmp   # Reset history (remove and recreate)
bin/ai.py stoptmp    # Disable history (delete tmp file)
```

### Proxy Server

```bash
# Start FastAPI proxy for key protection
bash server.sh

# Server runs at http://127.0.0.1:5260
# Configure clients to use this endpoint
```

---

## Architecture

### Key Functions

- `loadBKG()` - Load system prompt and timestamp
- `loadTMP()` - Load conversation history from `~/.ai/tmp/`
- `loadNEW()` - Process CLI arguments (files or text)
- `getResult()` - Standard streaming chat
- `getResult_web()` - Chat with web search tool
- `retrieve_rag()` - RAG retrieval with double-check
- `build_vectorstore()` - FAISS index management

### RAG Pipeline

1. **Keyword Generation** (`RAG_KEYWORD_MODEL`): Extract search intent from user query
2. **Vector Retrieval**: FAISS similarity search (`VECTOR_K=10` chunks)
3. **Double-Check** (`RAG_CHECK_MODEL`): Verify relevance with temperature=0.0
4. **Answer Generation**: Combine verified references with user query using `RAG_ANSWER_PROMPT`

### Web Search Integration

Uses Moonshot's builtin `$web_search` tool (`src/util.py:chat()`). The tool is declared in each request and handles tool calls automatically through a loop that continues until `finish_reason` is not "tool_calls".

---

## File Structure

```
.
├── bin/                      # Executable entry points
│   ├── ai.py                # Basic chat
│   ├── air.py               # + RAG
│   ├── aiw.py               # + Web
│   ├── aiwr.py              # + Web + RAG
│   ├── aiq.py               # Quiet mode
│   ├── aiwq.py              # Quiet web
│   └── ragindex.py          # Build index
├── mains/                    # Main logic modules
│   ├── main_ai.py
│   ├── main_air.py
│   ├── main_aiw.py
│   ├── main_aiwr.py
│   ├── main_aiq.py
│   ├── main_aiwq.py
│   └── main_ragindex.py
├── src/                      # Core implementation
│   ├── check.py             # API key validation
│   ├── config.py            # Configuration constants
│   ├── safe.py              # Secure password input
│   ├── prepare.py           # Directory initialization
│   ├── rag.py               # FAISS and embeddings
│   ├── util.py              # Main utility functions
│   └── server.py            # FastAPI proxy
├── supp/                     # Supplementary tools
│   ├── voice2ssh_mac.py     # macOS voice input
│   └── ssh2ai.py            # Voice processing bridge
├── docs/
│   └── requirements.txt     # Python dependencies
├── server.sh                # Proxy startup script
└── README.md                # This file
```

---

## Security Features

- **Key Protection**: Proxy server validates tokens before forwarding to real API
- **File Permissions**: `~/.ai/` directory created with 700 permissions
- **Secure Input**: Password masking with `getpass_star()` (`src/safe.py`)
- **Key Storage**: Separate files for real key and proxy password
- **No Key Exposure**: Client applications use proxy password, not real API key

### Proxy Server Details

- **Endpoint**: `http://127.0.0.1:5260/v1`
- **Validation**: Checks token against `PROXY_API_KEY` list
- **Forwarding**: Injects real API key, strips sensitive headers
- **Logging**: Prints request bodies to stdout (configurable)
- **CORS**: Not configured (intended for local use only)

---

## Voice Input (macOS)

The tool includes optional voice input support for macOS:

1. **voice2ssh_mac.py**: Records audio using right Command key, transcribes with Faster-Whisper, sends text to Linux server via SSH
2. **ssh2ai.py**: Monitors for transcribed text on server and triggers `bin/ai` commands

Configuration required in `supp/voice2ssh_mac.py`:
- `LINUX_HOST`, `LINUX_USER`, `LINUX_PASS`, `LINUX_PORT`
- `MODEL_PATH` - Path to Faster-Whisper model
- `REMOTE_OUTPUT_FILE` - Where to store transcriptions

You can download the "turbo" from Baidu Cloud Disk:

https://pan.baidu.com/s/1l_GcVR1nBLaQfF_UodYjyw?pwd=biuh

---

## Configuration Reference

### Models (`src/config.py`)

```python
MODEL_LIST = [
  'kimi-k2-thinking-turbo',
  'kimi-k2-turbo-preview',
  'kimi-k2-0905-preview',
  'kimi-k2-thinking',
  'kimi-latest',
  'moonshot-v1-auto',
  'moonshot-v1-8k',
  'moonshot-v1-32k',
  'moonshot-v1-128k'
]
BASIC_MODEL = MODEL_LIST[0]
RAG_KEYWORD_MODEL = MODEL_LIST[1]
RAG_CHECK_MODEL = MODEL_LIST[1]
```

### RAG Parameters

```python
CHUNK_SIZE = 5000          # Document chunk size
CHUNK_OVERLAP = 500        # Chunk overlap
VECTOR_K = 10              # Retrieved chunks
RAG_KEYWORD_TEMPERATURE = 0.2
RAG_CHECK_TEMPERATURE = 0.0  # Deterministic checking
```

### Paths

```python
AI_FOLDER = '~/.ai/'
RAG_SRC_DATABASE = '~/.ai/database/'
RAG_SRC_VECTOR = '~/.ai/vectorstore/'
SEARCH_MODEL_PATH = '/home/toolkit/tools/ai_local_src/models/multilingual-model'
```

You can download the "multilingual-model" from Baidu Cloud Disk:

https://pan.baidu.com/s/1EnD5oFqJ7-mj2cr5NhJFMw?pwd=biuh

---

## Troubleshooting

### "No sentence-transformers model found"

The tool suppresses this warning via `warnings.filterwarnings()` and `sys.stderr` redirection in `src/rag.py:init_huggingface_embeddings()`. Ensure `SEARCH_MODEL_PATH` contains valid model files.

### Key Validation Fails

1. Check network connectivity to `API_URL` and `PROXY_URL`
2. Verify key format (should start with `sk-`)
3. Inspect `~/.ai/key.txt` and `~/.ai/pkey.txt` permissions
4. Use `fast_verify_key()` in `src/safe.py` for manual testing

### RAG Returns No Results

1. Confirm documents in `~/.ai/database/` (`.txt` or `.md` only)
2. Rebuild index: `bin/ragindex.py`
3. Check embedding model path: `SEARCH_MODEL_PATH`
4. Verify `VECTOR_K` value isn't too small

### History Not Saving

1. Run `bin/ai.py usetmp` to create temp file
2. Check `~/.ai/tmp/` permissions (should be 700)
3. Verify `TMP_USE` is `True` in `src/prepare.py`

### Proxy Server Errors

1. Ensure port 5260 is available: `lsof -i :5260`
2. Check `PROXY_KEY_FILE` exists and contains valid token
3. Review server logs for request/response details
4. Verify `REAL_KEY_FILE` contains valid Moonshot API key

---

## Development

### Adding New Commands

1. Create `bin/newcmd.py` with shebang and import pattern
2. Add `mains/main_newcmd.py` with `run()` function
3. Implement logic in `src/util.py` or new module
4. Update feature matrix in this README

### Modifying Models

Edit `src/config.py:MODEL_LIST` and `BASIC_MODEL`. Changes apply immediately on next run.

### Custom Embeddings

Update `SEARCH_MODEL_PATH` in `src/config.py`. The tool expects a HuggingFace-compatible model.

### Extending Proxy

Modify `src/server.py:PROXY_API_KEY` to support multiple client tokens. Add routes as needed in the FastAPI app.

---

## Requirements

See `docs/requirements.txt` for complete list. Key dependencies:

- **AI/ML**: `torch==2.6.0`, `transformers==5.3.0`, `sentence-transformers==5.3.0`
- **RAG**: `langchain==1.2.13`, `faiss-cpu==1.8.0`, `langchain-huggingface==1.2.1`
- **API**: `openai==1.60.0`, `httpx==0.25.2`, `fastapi==0.135.2`
- **Utilities**: `pydantic==2.12.5`, `python-dotenv==1.2.2`, `PyYAML==6.0.3`

CUDA libraries are optional and included for GPU acceleration support.

---
