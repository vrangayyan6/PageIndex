<div align="center">
  


# PageIndex: Vectorless, Reasoning-based RAG

<p align="center"><b>Reasoning-based RAG&nbsp; ◦ &nbsp;No Vector DB&nbsp; ◦ &nbsp;No Chunking&nbsp; ◦ &nbsp;Human-like Retrieval</b></p>

<h4 align="center">
  <a href="https://vectify.ai">🏠 Homepage</a>&nbsp; • &nbsp;
  
  <a href="https://docs.pageindex.ai">📚 Docs</a>&nbsp; • &nbsp;
  
</h4>
  
</div>


### 📍 Explore PageIndex

To learn more, please see a detailed introduction of the [PageIndex framework](https://pageindex.ai/blog/pageindex-intro). Check out this GitHub repo for open-source code, and the [cookbooks](https://docs.pageindex.ai/cookbook), [tutorials](https://docs.pageindex.ai/tutorials), and [blog](https://pageindex.ai/blog) for additional usage guides and examples. 



### 🛠️ Deployment Options
- Self-host — run locally with this open-source repo.


### 🧪 Quick Hands-on

- Try the [**Vectorless RAG**](https://github.com/VectifyAI/PageIndex/blob/main/cookbook/pageindex_RAG_simple.ipynb) notebook — a *minimal*, hands-on example of reasoning-based RAG using PageIndex.

  
<div align="center">
  <a href="https://colab.research.google.com/github/VectifyAI/PageIndex/blob/main/cookbook/pageindex_RAG_simple.ipynb" target="_blank" rel="noopener">
    <img src="https://img.shields.io/badge/Open_In_Colab-Vectorless_RAG-orange?style=for-the-badge&logo=googlecolab" alt="Open in Colab: Vectorless RAG" />
  </a>
  &nbsp;&nbsp;
  <a href="https://colab.research.google.com/github/VectifyAI/PageIndex/blob/main/cookbook/vision_RAG_pageindex.ipynb" target="_blank" rel="noopener">
    <img src="https://img.shields.io/badge/Open_In_Colab-Vision_RAG-orange?style=for-the-badge&logo=googlecolab" alt="Open in Colab: Vision RAG" />
  </a>
</div>

---

# 🌲 PageIndex Tree Structure
PageIndex can transform lengthy PDF documents into a semantic **tree structure**, similar to a _"table of contents"_ but optimized for use with Large Language Models (LLMs). It's ideal for: financial reports, regulatory filings, academic textbooks, legal or technical manuals, and any document that exceeds LLM context limits.

Below is an example PageIndex tree structure. Also see more example [documents](https://github.com/VectifyAI/PageIndex/tree/main/tests/pdfs) and generated [tree structures](https://github.com/VectifyAI/PageIndex/tree/main/tests/results).

```jsonc
...
{
  "title": "Financial Stability",
  "node_id": "0006",
  "start_index": 21,
  "end_index": 22,
  "summary": "The Federal Reserve ...",
  "nodes": [
    {
      "title": "Monitoring Financial Vulnerabilities",
      "node_id": "0007",
      "start_index": 22,
      "end_index": 28,
      "summary": "The Federal Reserve's monitoring ..."
    },
    {
      "title": "Domestic and International Cooperation and Coordination",
      "node_id": "0008",
      "start_index": 28,
      "end_index": 31,
      "summary": "In 2023, the Federal Reserve collaborated ..."
    }
  ]
}
...
```

You can generate the PageIndex tree structure with this open-source repo, or use our [API](https://docs.pageindex.ai/quickstart) 

---

# ⚙️ Package Usage

You can follow these steps to generate a PageIndex tree from a PDF document.

### 1. Install dependencies

```bash
pip3 install --upgrade -r requirements.txt
```

### 2. Set your API key

Create a `.env` file in the root directory and add your API key. PageIndex supports multiple LLM providers:

```bash
# OpenAI
CHATGPT_API_KEY=your_openai_key_here

# Google Gemini / AI Studio
GOOGLE_API_KEY=your_gemini_key_here

# AWS Bedrock (uses boto3 credentials — see AWS docs for setup)
```

### 3. Run PageIndex on your PDF

```bash
python3 run_pageindex.py --pdf_path /path/to/your/document.pdf
```

<details>
<summary><strong>Optional parameters</strong></summary>
<br>
You can customize the processing with additional optional arguments:
```
--model                 Model to use (default: gemini/gemini-3.1-flash-lite-preview)
--toc-check-pages       Pages to check for table of contents (default: 20)
--max-pages-per-node    Max pages per node (default: 10)
--max-tokens-per-node   Max tokens per node (default: 20000)
--if-add-node-id        Add node ID (yes/no, default: yes)
--if-add-node-summary   Add node summary (yes/no, default: yes)
--if-add-doc-description Add doc description (yes/no, default: no)
--if-add-node-text      Add page text to each node (yes/no, default: no)
```
</details>

<details>
<summary><strong>Markdown support</strong></summary>
<br>
We also provide markdown support for PageIndex. You can use the `--md_path` flag to generate a tree structure for a markdown file.

```bash
python3 run_pageindex.py --md_path /path/to/your/document.md
```

Additional markdown-specific options:
```
--if-thinning           Apply tree thinning to merge small nodes (yes/no, default: no)
--thinning-threshold    Minimum token count to keep a node during thinning (default: 5000)
--summary-token-threshold  Minimum token count required to generate a node summary (default: 200)
```

> Note: in this function, we use "#" to determine node headings and their levels. For example, "##" is level 2, "###" is level 3, etc. Make sure your markdown file is formatted correctly. If your Markdown file was converted from a PDF or HTML, we don't recommend using this function, since most existing conversion tools cannot preserve the original hierarchy. Instead, use our [PageIndex OCR](https://pageindex.ai/blog/ocr), which is designed to preserve the original hierarchy, to convert the PDF to a markdown file and then use this function.
</details>

