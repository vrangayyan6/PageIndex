# Simple Vectorless RAG with PageIndex — AWS Bedrock (Local)

[This notebook](./cookbook/pageindex_RAG_simple_AWS_local.ipynb) demonstrates a minimal **vectorless RAG** pipeline using:
- **PageIndex** running **locally** (no PageIndex API key required)
- **AWS Bedrock** (`us.amazon.nova-micro-v1:0`) for both tree generation and retrieval

---

## Prerequisites

### 1. Clone and install PageIndex locally

```bash
git clone https://github.com/VectifyAI/PageIndex.git
cd PageIndex
pip install -r requirements.txt
```

### 2. Configure AWS credentials

The notebook uses AWS Bedrock via `litellm`. Make sure your credentials are set up:

```bash
aws configure
```

Or set environment variables or in .env:

```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

### 3. Enable model access in AWS Bedrock

Go to the [AWS Bedrock console](https://console.aws.amazon.com/bedrock/) and enable access to:
- `us.amazon.nova-micro-v1:0`

---

## Notebook Steps

| Step | Description |
|------|-------------|
| **0.1** | Install dependencies (`pageindex`, `boto3`) |
| **0.2** | Load local PageIndex repo and define helpers |
| **0.3** | Set up `call_llm` using AWS Bedrock via `litellm` |
| **1.1** | Generate PageIndex tree from a local PDF and save to `results/` |
| **1.2** | Inspect the tree structure (table of contents) |
| **2.1** | Use LLM to search the tree and identify relevant nodes |
| **2.2** | Print reasoning process and retrieved nodes |
| **3.1** | Extract text from retrieved nodes |
| **3.2** | Generate a final answer using the retrieved context |

---

## Key Differences from the API Version

| | [API version](./cookbook/pageindex_RAG_simple.ipynb) | [This notebook](./cookbook/pageindex_RAG_simple_AWS_local.ipynb) |
|---|---|---|
| PageIndex tree generation | PageIndex cloud API | Local (`page_index()`) |
| LLM | OpenAI | AWS Bedrock (Nova Micro) |
| API key required | PageIndex + LLM | LLM (AWS Bedrock) |
| Data privacy | PDF sent to PageIndex API | PDF stays local |
| Output saved | No | `results/<filename>_structure.json` |

---

## Notes

- **Python 3.14 compatibility**: `page_index()` is run inside a `ThreadPoolExecutor` to avoid `asyncio.run()` conflicts with Jupyter's event loop. `call_llm` uses synchronous `litellm.completion` via `loop.run_in_executor` for the same reason.
- **JSON parsing**: The Bedrock model may wrap JSON responses in markdown code fences; `utils.extract_json()` handles stripping them automatically.
- The local `pageindex` repo must take precedence over any pip-installed version — the notebook inserts the repo path at the front of `sys.path`.
