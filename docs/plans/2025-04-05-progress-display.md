# Progress Display Implementation Plan

> **REQUIRED SUB-SKILL:** Use the executing-plans skill to implement this plan task-by-task.

**Goal:** Add real-time progress display during document processing for both PDF and Markdown paths, showing users which stage is active and overall completion percentage.

**Architecture:** Create a `ProgressTracker` class in `utils.py` that manages progress state with stage tracking and percentage calculation. Integrate progress callbacks at key processing milestones in both PDF and Markdown processing pipelines. Display updates via a simple console-based progress bar with stage descriptions.

**Tech Stack:** Python's built-in `sys.stdout` for real-time updates, tqdm-style progress bar implementation (without external dependencies for lightweight approach).

---

## Analysis of Current Processing Stages

### PDF Path (`pageindex/page_index.py`):
1. PDF text extraction → get_page_tokens()
2. TOC detection → check_toc(), find_toc_pages()
3. TOC transformation → toc_transformer(), toc_index_extractor()
4. Structure building → tree_parser() → meta_processor() → post_processing()
5. Large node recursive processing → process_large_node_recursively()
6. Optional: Summary generation → generate_summaries_for_structure()

### Markdown Path (`pageindex/page_index_md.py`):
1. Node extraction → extract_nodes_from_markdown()
2. Text extraction → extract_node_text_content()
3. Optional thinning → tree_thinning_for_index()
4. Tree building → build_tree_from_nodes()
5. Optional: Summary generation → generate_summaries_for_structure_md()

---

## Task 1: Create ProgressTracker Class

**TDD scenario:** New feature — full TDD cycle

**Files:**
- Create: `tests/test_progress_tracker.py`
- Modify: `pageindex/utils.py` (add ProgressTracker class)

**Step 1: Write the failing test**

```python
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pageindex.utils import ProgressTracker

def test_progress_tracker_initialization():
    tracker = ProgressTracker(total_stages=5, description="Processing document")
    assert tracker.current_stage == 0
    assert tracker.total_stages == 5
    assert tracker.description == "Processing document"
    assert tracker.current_stage_name is None

def test_progress_tracker_next_stage():
    tracker = ProgressTracker(total_stages=3, description="Test")
    tracker.start_stage("Stage 1")
    assert tracker.current_stage == 1
    assert tracker.current_stage_name == "Stage 1"
    assert tracker.get_percentage() == pytest.approx(33.33, 0.01)
    
    tracker.start_stage("Stage 2")
    assert tracker.current_stage == 2
    assert tracker.current_stage_name == "Stage 2"
    assert tracker.get_percentage() == pytest.approx(66.67, 0.01)

def test_progress_tracker_get_percentage():
    tracker = ProgressTracker(total_stages=4)
    assert tracker.get_percentage() == 0.0
    
    tracker.start_stage("Stage 1")
    assert tracker.get_percentage() == 25.0
    
    tracker.start_stage("Stage 2")
    tracker.start_stage("Stage 3")
    assert tracker.get_percentage() == 75.0
    
    tracker.start_stage("Stage 4")
    assert tracker.get_percentage() == 100.0

def test_progress_tracker_format_progress():
    tracker = ProgressTracker(total_stages=4, description="PDF Processing")
    tracker.start_stage("Extracting text")
    formatted = tracker.format_progress()
    assert "PDF Processing" in formatted
    assert "Stage 1/4" in formatted
    assert "Extracting text" in formatted
    assert "25%" in formatted or "25.0%" in formatted

def test_progress_tracker_finish():
    tracker = ProgressTracker(total_stages=2)
    tracker.start_stage("Stage 1")
    tracker.finish()
    assert tracker.current_stage == 2
    assert tracker.get_percentage() == 100.0
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_progress_tracker.py -v`
Expected: FAIL with "ImportError: cannot import name 'ProgressTracker' from 'pageindex.utils'"

**Step 3: Write minimal implementation**

Add to `pageindex/utils.py` at the end of the file (before any `if __name__ == "__main__"` block):

```python
class ProgressTracker:
    """
    A simple progress tracker for document processing stages.
    Displays progress percentage and current stage name to stdout.
    """
    
    def __init__(self, total_stages, description="Processing"):
        """
        Initialize the progress tracker.
        
        Args:
            total_stages: Total number of processing stages
            description: Description of the overall process
        """
        self.total_stages = total_stages
        self.description = description
        self.current_stage = 0
        self.current_stage_name = None
    
    def start_stage(self, stage_name):
        """
        Mark the start of a new processing stage.
        
        Args:
            stage_name: Name/description of the current stage
        """
        self.current_stage += 1
        self.current_stage_name = stage_name
        self._display()
    
    def get_percentage(self):
        """Calculate completion percentage."""
        return (self.current_stage / self.total_stages) * 100 if self.total_stages > 0 else 0
    
    def format_progress(self):
        """Format the current progress as a string."""
        percentage = self.get_percentage()
        return f"[{self.description}] Stage {self.current_stage}/{self.total_stages}: {self.current_stage_name} ({percentage:.1f}%)"
    
    def _display(self):
        """Display current progress to stdout."""
        import sys
        progress_str = self.format_progress()
        sys.stdout.write(f"\r{progress_str:<80}")
        sys.stdout.flush()
    
    def finish(self, message=None):
        """
        Mark the process as complete.
        
        Args:
            message: Optional completion message
        """
        self.current_stage = self.total_stages
        import sys
        if message:
            sys.stdout.write(f"\n{message}\n")
        else:
            completion_msg = f"✓ {self.description} complete ({self.total_stages}/{self.total_stages} stages)\n"
            sys.stdout.write(f"\r{completion_msg:<80}\n")
        sys.stdout.flush()
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_progress_tracker.py -v`
Expected: PASS on all 6 tests

**Step 5: Commit**

```bash
git add tests/test_progress_tracker.py pageindex/utils.py
git commit -m "feat: add ProgressTracker class for document processing stages"
```

---

## Task 2: Integrate Progress Display into PDF Processing

**TDD scenario:** Modify existing code — run existing tests first, then add progress tracking

**Files:**
- Modify: `pageindex/page_index.py` (integrate progress tracking in `page_index_main`)

**Pre-step: Verify current tests pass**

Run: `python -m pytest tests/ -v --tb=short 2>/dev/null || echo "No existing tests found or tests failed"`

Note: This is an existing project. Focus on manual verification instead.

**Step 1: Add progress tracking to PDF processing**

Modify `pageindex/page_index.py` - update the `page_index_main` function to include progress tracking.

Locate the `page_index_main` function and update it:

```python
def page_index_main(doc, model=None, toc_check_page_num=20, max_page_num_each_node=10, max_token_num_each_node=20000,
                    if_add_node_id='yes', if_add_node_summary='yes', if_add_doc_description='no', if_add_node_text='no'):
    # Import ProgressTracker
    from .utils import ProgressTracker
    
    logger = JsonLogger(doc)
    
    is_valid_pdf = (
        (isinstance(doc, str) and os.path.isfile(doc) and doc.lower().endswith(".pdf")) or 
        isinstance(doc, BytesIO)
    )
    if not is_valid_pdf:
        raise ValueError("Unsupported input type. Expected a PDF file path or BytesIO object.")

    # Initialize progress tracker with estimated stages
    # Stages: 1. Parsing, 2. Tree parsing, 3. Post-processing, 4. Large node processing, 5. Summaries (optional)
    estimated_stages = 4
    if if_add_node_summary == 'yes':
        estimated_stages += 1
    progress = ProgressTracker(total_stages=estimated_stages, description="Processing PDF")

    progress.start_stage("Parsing PDF text")
    print('')  # Newline after progress display
    page_list = get_page_tokens(doc, model=model)

    logger.info({'total_page_number': len(page_list)})
    logger.info({'total_token': sum([page[1] for page in page_list])})

    async def page_index_builder():
        progress.start_stage("Building document structure")
        print('')  # Newline after progress display
        structure = await tree_parser(page_list, doc=doc, logger=logger, model=model, 
                                     toc_check_page_num=toc_check_page_num, 
                                     max_page_num_each_node=max_page_num_each_node, 
                                     max_token_num_each_node=max_token_num_each_node)
        
        if if_add_node_id == 'yes':
            write_node_id(structure)    
        
        if if_add_node_text == 'yes':
            progress.start_stage("Extracting node text")
            print('')
            add_node_text(structure, page_list)
        
        if if_add_node_summary == 'yes':
            progress.start_stage("Generating summaries")
            print('')
            if if_add_node_text == 'no':
                add_node_text(structure, page_list)
            await generate_summaries_for_structure(structure, model=model)
            if if_add_node_text == 'no':
                remove_structure_text(structure)
            
            if if_add_doc_description == 'yes':
                progress.start_stage("Generating document description")
                print('')
                # Create a clean structure without unnecessary fields for description generation
                clean_structure = create_clean_structure_for_description(structure)
                doc_description = generate_doc_description(clean_structure, model=model)
                progress.finish()
                return {
                    'doc_name': get_pdf_name(doc),
                    'doc_description': doc_description,
                    'structure': structure,
                }
        
        progress.finish()
        return {
            'doc_name': get_pdf_name(doc),
            'structure': structure,
        }

    return asyncio.run(page_index_builder())
```

**Step 2: Verify PDF processing still works**

Create a quick test script to validate:

```python
# test_pdf_progress.py
import sys
sys.path.insert(0, '.')

from pageindex import page_index_main

# Test with a sample PDF if available
import os
pdf_path = os.path.join('tests', 'pdfs', 'DeepSeek_R1.pdf')
if os.path.exists(pdf_path):
    print(f"Testing with {pdf_path}")
    result = page_index_main(
        doc=pdf_path,
        model='amazon_nova/nova-2-lite-v1',
        toc_check_page_num=5,  # Reduced for faster test
        if_add_node_summary='no',  # Skip summaries for faster test
        if_add_node_id='no'
    )
    print("Success! Structure keys:", result.keys())
else:
    print(f"No test PDF found at {pdf_path}")
    print("Progress tracker class exists:", 'ProgressTracker' in dir())
```

Run: `python test_pdf_progress.py` (if test PDF exists)

Verify that:
1. Progress messages appear showing stage progression
2. The PDF processing completes successfully
3. Output structure is returned correctly

**Step 3: Commit**

```bash
git add pageindex/page_index.py
git commit -m "feat: add progress tracking to PDF processing pipeline"
```

---

## Task 3: Integrate Progress Display into Markdown Processing

**TDD scenario:** Modify existing code — similar to Task 2

**Files:**
- Modify: `pageindex/page_index_md.py` (integrate progress tracking in `md_to_tree`)

**Step 1: Add progress tracking to Markdown processing**

Modify `pageindex/page_index_md.py` - update the `md_to_tree` function:

```python
async def md_to_tree(md_path, if_thinning=False, min_token_threshold=None, if_add_node_summary='no', summary_token_threshold=None, model=None, if_add_doc_description='no', if_add_node_text='no', if_add_node_id='yes'):
    # Import ProgressTracker (handle both module and direct import)
    try:
        from .utils import ProgressTracker
    except ImportError:
        from utils import ProgressTracker
    
    with open(md_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Calculate total stages
    total_stages = 4  # extract nodes, extract text, build tree, format
    if if_thinning:
        total_stages += 1
    if if_add_node_id == 'yes':
        total_stages += 1
    if if_add_node_summary == 'yes':
        total_stages += 1
    if if_add_doc_description == 'yes':
        total_stages += 1
    
    progress = ProgressTracker(total_stages=total_stages, description="Processing Markdown")
    
    progress.start_stage("Extracting nodes from markdown")
    print('')
    node_list, markdown_lines = extract_nodes_from_markdown(markdown_content)

    progress.start_stage("Extracting text content")
    print('')  
    nodes_with_content = extract_node_text_content(node_list, markdown_lines)
    
    if if_thinning:
        progress.start_stage("Updating token counts")
        print('')
        nodes_with_content = update_node_list_with_text_token_count(nodes_with_content, model=model)
        progress.start_stage("Thinning nodes")
        print('')
        nodes_with_content = tree_thinning_for_index(nodes_with_content, min_token_threshold, model=model)
    
    progress.start_stage("Building tree from nodes")
    print('')
    tree_structure = build_tree_from_nodes(nodes_with_content)

    if if_add_node_id == 'yes':
        progress.start_stage("Assigning node IDs")
        print('')
        write_node_id(tree_structure)

    progress.start_stage("Formatting tree structure")
    print('')
    
    if if_add_node_summary == 'yes':
        # Always include text for summary generation
        tree_structure = format_structure(tree_structure, order = ['title', 'node_id', 'summary', 'prefix_summary', 'text', 'line_num', 'nodes'])
        
        progress.start_stage("Generating summaries")
        print('')
        tree_structure = await generate_summaries_for_structure_md(tree_structure, summary_token_threshold=summary_token_threshold, model=model)
        
        if if_add_node_text == 'no':
            # Remove text after summary generation if not requested
            tree_structure = format_structure(tree_structure, order = ['title', 'node_id', 'summary', 'prefix_summary', 'line_num', 'nodes'])
        
        if if_add_doc_description == 'yes':
            progress.start_stage("Generating document description")
            print('')
            # Create a clean structure without unnecessary fields for description generation
            clean_structure = create_clean_structure_for_description(tree_structure)
            doc_description = generate_doc_description(clean_structure, model=model)
            progress.finish()
            return {
                'doc_name': os.path.splitext(os.path.basename(md_path))[0],
                'doc_description': doc_description,
                'structure': tree_structure,
            }
    else:
        # No summaries needed, format based on text preference
        if if_add_node_text == 'yes':
            tree_structure = format_structure(tree_structure, order = ['title', 'node_id', 'summary', 'prefix_summary', 'text', 'line_num', 'nodes'])
        else:
            tree_structure = format_structure(tree_structure, order = ['title', 'node_id', 'summary', 'prefix_summary', 'line_num', 'nodes'])
    
    progress.finish()
    return {
        'doc_name': os.path.splitext(os.path.basename(md_path))[0],
        'structure': tree_structure,
    }
```

**Step 2: Verify Markdown processing still works**

Create a quick test:

```python
# test_md_progress.py
import asyncio
import sys
sys.path.insert(0, '.')

from pageindex.page_index_md import md_to_tree
import os

md_path = os.path.join('tests', 'markdowns', 'cognitive-load.md')
if os.path.exists(md_path):
    print(f"Testing with {md_path}")
    result = asyncio.run(md_to_tree(
        md_path=md_path,
        if_thinning=False,
        if_add_node_summary='no',  # Skip for faster test
        model='amazon_nova/nova-2-lite-v1'
    ))
    print("Success! Structure keys:", result.keys())
else:
    print(f"No test markdown found at {md_path}")
    # Create a simple test markdown
    test_content = """# Chapter 1
Some content here.

## Section 1.1
More content.

# Chapter 2
Even more content.
"""
    with open('test_doc.md', 'w') as f:
        f.write(test_content)
    
    result = asyncio.run(md_to_tree(
        md_path='test_doc.md',
        if_thinning=False,
        if_add_node_summary='no'
    ))
    print("Success! Structure keys:", result.keys())
    os.remove('test_doc.md')
```

Run: `python test_md_progress.py`

Verify:
1. Progress messages appear with stage progression
2. Markdown processing completes successfully
3. Output structure is returned correctly

**Step 3: Commit**

```bash
git add pageindex/page_index_md.py
git commit -m "feat: add progress tracking to Markdown processing pipeline"
```

---

## Task 4: Update CLI Entry Point Messages

**TDD scenario:** Trivial change — use judgment

**Files:**
- Modify: `run_pageindex.py`

**Step 1: Add verbose/progress flag and clean up duplicate print statements**

Currently `run_pageindex.py` has `print()` statements that may duplicate progress output. Clean these up to work with the new progress tracking.

Modify `run_pageindex.py`:

```python
# In the pdf_path branch, update the processing call:
# OLD:
# toc_with_page_number = page_index_main(args.pdf_path, opt)
# print('Parsing done, saving to file...')

# NEW:
print(f"Processing PDF: {args.pdf_path}")
print("=" * 60)
toc_with_page_number = page_index_main(args.pdf_path, opt)
print("=" * 60)
print('Saving results...')
```

```python
# In the md_path branch, update similarly:
# OLD:
# print('Processing markdown file...')

# NEW:
print(f"Processing Markdown: {args.md_path}")
print("=" * 60)
```

Also update the final success messages for consistency:

```python
# For both branches, replace:
# print(f'Tree structure saved to: {output_file}')

# With:
print(f'✓ Results saved to: {output_file}')
```

**Step 2: Verify CLI works end-to-end**

Test with a small file if available:

```bash
# If a test markdown exists:
python run_pageindex.py --md_path tests/markdowns/cognitive-load.md --if-add-node-summary no

# Expected output should show:
# Processing Markdown: tests/markdowns/cognitive-load.md
# ============================================================
# [Processing Markdown] Stage 1/4: Extracting nodes from markdown (25.0%)
# ... (continuing with stages)
# ✓ Processing Markdown complete (4/4 stages)
# ============================================================
# Saving results...
# ✓ Results saved to: ./results/cognitive-load_structure.json
```

**Step 3: Commit**

```bash
git add run_pageindex.py
git commit -m "chore: clean up CLI output formatting for progress display"
```

---

## Task 5: Add Progress Tracking Tests for CLI

**TDD scenario:** New feature — full TDD cycle

**Files:**
- Create: `tests/test_cli_progress.py`

**Step 1: Write integration tests**

```python
# tests/test_cli_progress.py
"""Integration tests for progress display functionality."""
import subprocess
import sys
import os
import tempfile
import pytest

# Mark all tests as integration tests that may need external APIs
pytestmark = [pytest.mark.integration]


def test_cli_pdf_processing_shows_progress():
    """Test that PDF processing shows progress output."""
    # Create a minimal test PDF or skip if none exists
    pdf_path = os.path.join('tests', 'pdfs', 'sample.pdf')
    if not os.path.exists(pdf_path):
        pytest.skip("No test PDF available")
    
    result = subprocess.run(
        [sys.executable, 'run_pageindex.py', '--pdf_path', pdf_path],
        capture_output=True,
        text=True,
        timeout=120
    )
    
    # Check for expected output patterns
    assert result.returncode == 0, f"CLI failed with: {result.stderr}"
    assert "Processing PDF" in result.stdout or "Processing PDF" in result.stderr
    assert "Stage" in result.stdout


def test_cli_markdown_processing_shows_progress():
    """Test that Markdown processing shows progress output."""
    # Create a temporary markdown file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("# Chapter 1\n\nContent here.\n\n## Section 1.1\n\nMore content.\n")
        temp_path = f.name
    
    try:
        result = subprocess.run(
            [sys.executable, 'run_pageindex.py', '--md_path', temp_path],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        assert result.returncode == 0, f"CLI failed with: {result.stderr}"
        assert "Processing Markdown" in result.stdout
        assert "Stage" in result.stdout
        assert "Processing Markdown complete" in result.stdout
    finally:
        os.unlink(temp_path)


def test_progress_tracker_handles_empty_document():
    """Test that progress tracking handles edge cases."""
    # Create a very minimal markdown
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("# Single Section\n")
        temp_path = f.name
    
    try:
        result = subprocess.run(
            [sys.executable, 'run_pageindex.py', '--md_path', temp_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        assert result.returncode == 0
        assert "complete" in result.stdout.lower()
    finally:
        os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**Step 2: Run the integration tests**

Note: These tests may require API keys and network access.

Run: `pytest tests/test_cli_progress.py -v --tb=short`
Expected: Tests pass or are skipped if no test files available

**Step 3: Commit**

```bash
git add tests/test_cli_progress.py
git commit -m "test: add integration tests for progress display functionality"
```

---

## Task 6: Documentation and Cleanup

**TDD scenario:** Trivial change — documentation

**Files:**
- Create: `docs/progress-display.md` (usage documentation)
- Modify: `README.md` (update usage section)

**Step 1: Write progress display documentation**

Save to `docs/progress-display.md`:

```markdown
# Progress Display

PageIndex now displays real-time progress during document processing.

## Output Format

During processing, you'll see a progress bar that updates in real-time:

```
[Processing PDF] Stage 1/5: Parsing PDF text (20.0%)
[Processing PDF] Stage 2/5: Building document structure (40.0%)
[Processing PDF] Stage 3/5: Extracting node text (60.0%)
[Processing PDF] Stage 4/5: Generating summaries (80.0%)
[Processing PDF] Stage 5/5: Generating document description (100.0%)
✓ Processing PDF complete (5/5 stages)
```

## Stages

### PDF Processing
1. **Parsing PDF text** - Extracting text from each page
2. **Building document structure** - Detecting TOC and building the tree structure
3. **Extracting node text** (optional, with `--if-add-node-text yes`) - Getting text for each section
4. **Generating summaries** (optional, with `--if-add-node-summary yes`) - Creating AI summaries
5. **Generating document description** (optional, with `--if-add-doc-description yes`) - Creating overall description

### Markdown Processing
1. **Extracting nodes** - Parsing headings from markdown
2. **Extracting text content** - Getting content for each section
3. **Updating token counts** (optional, with thinning) - Calculating token usage
4. **Thinning nodes** (optional, with `--if-thinning yes`) - Merging small sections
5. **Building tree** - Creating the hierarchical structure
6. **Assigning node IDs** - Adding unique identifiers
7. **Formatting structure** - Preparing the output
8. **Generating summaries** (optional) - Creating AI summaries
9. **Generating document description** (optional) - Creating overall description

## Disabling Progress Display

To disable progress output (e.g., for programmatic use or logging to file), you can redirect stderr:

```bash
python run_pageindex.py --pdf_path doc.pdf 2>/dev/null
```

Or capture output in Python:

```python
import sys
from io import StringIO
from pageindex import page_index_main

# Capture progress output
old_stdout = sys.stdout
sys.stdout = StringIO()

result = page_index_main('doc.pdf', ...)

# Restore stdout
sys.stdout = old_stdout
```
```

**Step 2: Update the CLI usage section in README.md**

Look for the usage section in README.md and add a note about progress display.

After the basic usage examples, add:

```markdown
## Progress Display

PageIndex provides real-time progress updates during processing:

```
[Processing PDF] Stage 1/5: Parsing PDF text (20.0%)
[Processing PDF] Stage 2/5: Building document structure (40.0%)
...
✓ Processing PDF complete (5/5 stages)
```

The number of stages depends on your configuration options. See [docs/progress-display.md](docs/progress-display.md) for details.
```

**Step 3: Commit**

```bash
git add docs/progress-display.md README.md
git commit -m "docs: add progress display documentation"
```

---

## Final Verification

Run a comprehensive check:

```bash
# 1. Verify all tests pass
python -m pytest tests/test_progress_tracker.py -v

# 2. Verify imports work
python -c "from pageindex.utils import ProgressTracker; print('✓ Import works')"

# 3. Verify ProgressTracker works standalone
python -c "
from pageindex.utils import ProgressTracker
import time

progress = ProgressTracker(total_stages=3, description='Test')
progress.start_stage('Stage 1')
progress.start_stage('Stage 2')
progress.start_stage('Stage 3')
progress.finish()
print('✓ ProgressTracker works')
"

# 4. Check git status
git log --oneline -10
```

---

## Summary

This implementation adds real-time progress display to PageIndex document processing:

1. **ProgressTracker class** (`pageindex/utils.py`): A lightweight progress tracking utility with percentage calculation and stage management

2. **PDF processing integration** (`pageindex/page_index.py`): Progress tracking added to `page_index_main()` showing the 4-5 stages of processing

3. **Markdown processing integration** (`pageindex/page_index_md.py`): Progress tracking added to `md_to_tree()` showing the 4-9 stages depending on options

4. **CLI cleanup** (`run_pageindex.py`): Updated to work cleanly with new progress output

5. **Tests** (`tests/`):
   - `test_progress_tracker.py`: Unit tests for the ProgressTracker class
   - `test_cli_progress.py`: Integration tests for end-to-end progress display

6. **Documentation** (`docs/progress-display.md`): Complete documentation of progress output format and stages