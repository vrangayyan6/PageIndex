# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚀 Common Commands

### Installation & Setup
```bash
# Install dependencies
pip3 install --upgrade -r requirements.txt

# Set up environment (create .env file)
echo "CHATGPT_API_KEY=your_openai_key_here" > .env
# or for Gemini/Google AI Studio
echo "GOOGLE_API_KEY=your_gemini_key_here" > .env
```

### Running PageIndex
```bash
# Process a PDF document
python3 run_pageindex.py --pdf_path /path/to/document.pdf

# Process a Markdown document
python3 run_pageindex.py --md_path /path/to/document.md

# Customize processing with optional parameters
python3 run_pageindex.py --pdf_path document.pdf \
  --model gemini/gemini-1.5-flash \
  --toc-check-pages 30 \
  --max-pages-per-node 15 \
  --if-add-node-summary yes
```

### Testing
```bash
# Run the example notebooks in cookbook/
# (Open in Jupyter or Google Colab)

# Validate outputs by comparing with expected results in tests/results/
```

## 🏗️ Code Architecture

### Core Components
- **`run_pageindex.py`**: Main CLI entry point that handles argument parsing and orchestrates processing
- **`pageindex/`**: Core package containing:
  - `page_index.py`: Main PDF processing logic with tree structure generation
  - `page_index_md.py`: Markdown-specific processing logic
  - `utils.py`: Utility functions including:
    - LLM completion wrappers (litellm-based)
    - PDF text extraction (PyPDF2/PyMuPDF)
    - Token counting and text processing
    - Tree structure manipulation and formatting
    - Configuration loading (ConfigLoader class)
    - Logging and helper functions

### Key Data Structures
- **Tree Structure**: Hierarchical JSON representing document sections with:
  - `title`: Section title
  - `node_id`: Unique 4-digit identifier
  - `start_index`/`end_index`: Page range
  - `summary`: AI-generated section summary
  - `nodes`: Child sections (recursive structure)

### Processing Flow
1. **Input Validation**: Check file type and existence
2. **Configuration Loading**: Merge user args with defaults from `config.yaml`
3. **Document Processing**:
   - **PDF Path**: Extract text, generate tree structure via LLM reasoning
   - **Markdown Path**: Parse heading hierarchy, apply optional thinning
4. **Post-processing**: Add node IDs, summaries, and structural cleanup
5. **Output**: Save JSON tree structure to `./results/`

### Configuration
- Defaults stored in `pageindex/config.yaml`
- Overridable via command-line arguments
- Handles API key aliases (CHATGPT_API_KEY → OPENAI_API_KEY, GOOGLE_API_KEY → GEMINI_API_KEY)

## 🔧 Development Guidelines

### Working with LLMs
- Uses `litellm` for unified LLM API access
- Supports OpenAI, Gemini, and other providers via model prefixes
- Temperature set to 0 for deterministic outputs
- Built-in retry mechanism (10 attempts) with exponential backoff

### Extending Functionality
1. **Adding New LLM Providers**: Configure via `litellm` model string
2. **Modifying Tree Generation**: Edit prompt templates in `page_index.py` and `page_index_md.py`
3. **Custom Post-processing**: Modify functions in `utils.py` like `post_processing()` or `clean_structure_post()`
4. **Alternative Parsers**: Extend `get_page_tokens()` in `utils.py` for additional PDF libraries

### Testing Approach
- Visual validation using sample PDFs in `tests/pdfs/`
- Compare generated structures against expected outputs in `tests/results/`
- Manual verification of tree structure correctness and summary quality

## 📁 Directory Structure
```
PageIndex/
├─ .env                  # Environment variables (API keys)
├─ .gitignore           # Git ignore rules
├─ requirements.txt     # Python dependencies
├─ run_pageindex.py     # Main CLI script
├─ README.md            # Project overview and usage guide
├─ CHANGELOG.md         # Release notes
├─ LICENSE              # MIT license
├─ pageindex/           # Core source code
│  ├─ __init__.py
│  ├─ page_index.py     # PDF processing logic
│  ├─ page_index_md.py  # Markdown processing logic
│  ├─ utils.py          # Utilities, LLM wrappers, config
│  └─ config.yaml       # Default configuration
├─ tests/               # Test data
│  ├─ pdfs/             # Sample PDF documents
│  └─ results/          # Expected output structures
├─ cookbook/            # Jupyter notebook examples
├─ scripts/             # Utility scripts
├─ tutorials/           # Step-by-step guides
└─ results/             # Generated output (created at runtime)
```