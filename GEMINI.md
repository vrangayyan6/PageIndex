# PageIndex: Vectorless, Reasoning-based RAG

PageIndex is a Python library and framework for building reasoning-based Retrieval-Augmented Generation (RAG) systems. Unlike traditional vector-based RAG, PageIndex creates a hierarchical tree index of documents and uses LLMs to perform reasoning-driven retrieval, simulating how human experts navigate complex documents.

## Project Structure

- `pageindex/`: Core library containing logic for document parsing and tree structure generation.
  - `page_index.py`: Main logic for processing PDF documents.
  - `page_index_md.py`: Logic for processing Markdown documents.
  - `utils.py`: Utility functions for PDF manipulation, LLM interaction (via `litellm`), and JSON processing.
  - `config.yaml`: Default configuration for models and indexing parameters.
- `run_pageindex.py`: Command-line interface for generating PageIndex tree structures from PDF or Markdown files.
- `cookbook/`: Collection of Jupyter notebooks demonstrating various use cases, including vectorless RAG and vision-based RAG.
- `tests/`: Sample PDFs and their corresponding generated tree structures for verification.
- `scripts/`: GitHub workflow scripts for issue management.

## Getting Started

### Installation

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Set up environment variables:**
    Create a `.env` file in the root directory and add your API key:
    ```bash
    OPENAI_API_KEY=your_openai_key_here
    # OR
    CHATGPT_API_KEY=your_openai_key_here
    ```

### Running PageIndex

Generate a tree structure for a PDF:
```bash
python run_pageindex.py --pdf_path /path/to/your/document.pdf
```

Generate a tree structure for a Markdown file:
```bash
python run_pageindex.py --md_path /path/to/your/document.md
```

### Configuration

You can customize the indexing process using command-line arguments or by modifying `pageindex/config.yaml`. Key parameters include:
- `--model`: The LLM to use (default: `gemini/gemini-3.1-flash-lite-preview`).
- `--toc-check-pages`: Number of pages to check for a table of contents.
- `--max-pages-per-node`: Maximum number of pages per node in the tree.
- `--max-tokens-per-node`: Maximum number of tokens per node.

## Development Conventions

- **Asynchronous Processing:** The library uses `asyncio` for concurrent LLM calls and document processing.
- **LLM Interaction:** `litellm` is used for standardized access to various LLM providers.
- **Error Handling:** Retries are implemented for LLM completions to ensure robustness.
- **Logging:** A custom `JsonLogger` in `utils.py` provides detailed logs in JSON format.

## Key Technologies

- **Python 3.x**
- **litellm**: Unified interface for LLM APIs.
- **PyPDF2 / PyMuPDF**: PDF parsing and text extraction.
- **asyncio**: Asynchronous I/O for concurrency.
- **dotenv**: Environment variable management.
