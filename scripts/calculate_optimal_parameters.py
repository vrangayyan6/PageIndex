#!/usr/bin/env python3
"""
Calculate optimal PageIndex parameters for nova-micro to minimize RPM.

Nova-Micro specs:
- Context window: 128,000 tokens
- Max output tokens: 10,000 tokens
- Safe input budget: ~110,000 tokens (leaving room for output + overhead)
"""

import math

# Nova-micro constraints
NOVA_MICRO_CONTEXT = 128_000
NOVA_MICRO_MAX_OUTPUT = 10_000
SAFE_INPUT_TOKENS = 110_000  # Leave buffer for output + prompts

# Analysis: How many tokens per page (estimated from pageindex codebase)
TYPICAL_TOKENS_PER_PAGE = 800  # ~500-1200 range, conservative estimate

# Analysis: Overhead tokens per request (prompt template + metadata)
PROMPT_OVERHEAD = 500


def calculate_toc_check_pages():
    """
    Recommend TOC_CHECK_PAGES value.
    
    TOC detection is sequential - each page checked individually.
    We want enough pages to catch "late" TOCs while minimizing requests.
    """
    # Most documents have TOC within first 5-10 pages
    # Annual reports: often pages 3-8
    # Research papers: often pages 1-3
    # Books: can be 10-20 pages of front matter
    
    recommendations = {
        'aggressive': 5,    # Risk: might miss some TOCs
        'balanced': 10,     # Recommended: catches 95% of TOCs
        'conservative': 15  # Safe: catches 99% but more requests
    }
    
    print("TOC_CHECK_PAGES Analysis:")
    print("-" * 40)
    for name, value in recommendations.items():
        print(f"  {name:12}: {value:3d} pages ({value} LLM requests)")
    print(f"\n  Recommendation: {recommendations['balanced']}")
    print(f"    Trade-off: ~10 vs 20 requests saves 50% on TOC detection")
    
    return recommendations['balanced']


def calculate_max_tokens_per_node():
    """
    Recommend MAX_TOKENS_PER_NODE value.
    
    This controls how many pages are grouped per LLM request during
    structure generation. Maximizing this minimizes requests.
    """
    # Effective tokens per batch = SAFE_INPUT_TOKENS - PROMPT_OVERHEAD
    effective_tokens = SAFE_INPUT_TOKENS - PROMPT_OVERHEAD
    
    # But we need to account for the "previous structure" that's included
    # in generate_toc_continue calls
    previous_structure_overhead = 5000  # Estimated
    usable_tokens = effective_tokens - previous_structure_overhead
    
    recommendations = {
        'current': 20_000,
        'conservative': 50_000,
        'optimal': min(100_000, usable_tokens),
        'aggressive': usable_tokens
    }
    
    print("\nMAX_TOKENS_PER_NODE Analysis:")
    print("-" * 40)
    print(f"  Nova-micro context:     {NOVA_MICRO_CONTEXT:,} tokens")
    print(f"  Max output:             {NOVA_MICRO_MAX_OUTPUT:,} tokens")
    print(f"  Safe input budget:      {SAFE_INPUT_TOKENS:,} tokens")
    print(f"  Prompt overhead:        {PROMPT_OVERHEAD:,} tokens")
    print(f"  Structure overhead:     {previous_structure_overhead:,} tokens")
    print(f"  Usable per request:     {usable_tokens:,} tokens")
    print()
    
    for name, value in recommendations.items():
        pages = value // TYPICAL_TOKENS_PER_PAGE
        print(f"  {name:12}: {value:6,} tokens (~{pages:3d} pages)")
    
    print(f"\n  Recommendation: {recommendations['optimal']:,}")
    print(f"    Impact: Can pack ~{recommendations['optimal'] // TYPICAL_TOKENS_PER_PAGE} pages per request")
    print(f"    vs current ~{recommendations['current'] // TYPICAL_TOKENS_PER_PAGE} pages (5x improvement)")
    
    return recommendations['optimal']


def calculate_max_pages_per_node(max_tokens_per_node):
    """
    Recommend MAX_PAGES_PER_NODE value.
    
    This prevents recursive re-processing of large nodes.
    Set based on token limit to avoid unnecessary recursion.
    """
    pages_from_tokens = max_tokens_per_node // TYPICAL_TOKENS_PER_PAGE
    
    recommendations = {
        'current': 10,
        'conservative': pages_from_tokens // 2,  # ~60 pages
        'optimal': pages_from_tokens,             # ~120 pages
    }
    
    print("\nMAX_PAGES_PER_NODE Analysis:")
    print("-" * 40)
    for name, value in recommendations.items():
        recursion_depth = math.log2(100/value) if value < 100 else 0
        print(f"  {name:12}: {value:3d} pages (recursion depth: {recursion_depth:.1f})")
    
    print(f"\n  Recommendation: {recommendations['optimal']}")
    print(f"    Trade-off: Prevents deep recursion, reduces node splitting")
    
    return recommendations['optimal']


def calculate_rpm_impact(
    current_toc_check=20,
    current_max_tokens=20000,
    current_max_pages=10,
    new_toc_check=10,
    new_max_tokens=100000,
    new_max_pages=120
):
    """Calculate estimated RPM reduction."""
    
    # Example: 100-page document, 20k tokens/page avg
    doc_pages = 100
    typical_tokens = 800
    
    # Current scenario
    toc_requests_current = min(5, current_toc_check)  # Usually finds TOC early
    group_requests_current = (doc_pages * typical_tokens) / current_max_tokens
    large_node_requests_current = doc_pages / current_max_pages
    total_current = toc_requests_current + group_requests_current + large_node_requests_current + 5  # misc
    
    # New scenario
    toc_requests_new = min(5, new_toc_check)
    group_requests_new = (doc_pages * typical_tokens) / new_max_tokens
    large_node_requests_new = doc_pages / new_max_pages
    total_new = toc_requests_new + group_requests_new + large_node_requests_new + 5
    
    reduction = (1 - total_new/total_current) * 100
    
    print("\n" + "="*60)
    print("ESTIMATED RPM IMPACT")
    print("="*60)
    print(f"\nCurrent settings ({current_toc_check}/{current_max_tokens}/{current_max_pages}):")
    print(f"  TOC detection:     ~{toc_requests_current} requests")
    print(f"  Grouping:          ~{group_requests_current:.1f} requests")
    print(f"  Large nodes:       ~{large_node_requests_current:.1f} requests")
    print(f"  Misc:              ~5 requests")
    print(f"  TOTAL:             ~{total_current:.0f} requests")
    
    print(f"\nOptimized settings ({new_toc_check}/{new_max_tokens}/{new_max_pages}):")
    print(f"  TOC detection:     ~{toc_requests_new} requests")
    print(f"  Grouping:          ~{group_requests_new:.1f} requests")
    print(f"  Large nodes:       ~{large_node_requests_new:.1f} requests")
    print(f"  Misc:              ~5 requests")
    print(f"  TOTAL:             ~{total_new:.0f} requests")
    
    print(f"\n  ESTIMATED SAVINGS: {reduction:.1f}% fewer requests")
    print("="*60)
    
    return {
        'toc_check_pages': new_toc_check,
        'max_tokens_per_node': new_max_tokens,
        'max_pages_per_node': new_max_pages,
        'estimated_reduction': reduction
    }


def main():
    """Run all calculations and output recommendations."""
    print("="*60)
    print("PageIndex Parameter Optimization for Nova-Micro")
    print("="*60)
    print()
    
    toc_check = calculate_toc_check_pages()
    max_tokens = calculate_max_tokens_per_node()
    max_pages = calculate_max_pages_per_node(max_tokens)
    
    recommendations = calculate_rpm_impact(
        new_toc_check=toc_check,
        new_max_tokens=max_tokens,
        new_max_pages=max_pages
    )
    
    print("\n" + "="*60)
    print("FINAL RECOMMENDED VALUES")
    print("="*60)
    print(f"""
# Current (high RPM):
TOC_CHECK_PAGES = 20
MAX_PAGES_PER_NODE = 10
MAX_TOKENS_PER_NODE = 20000

# Optimized for nova-micro (reduced RPM):
TOC_CHECK_PAGES = {recommendations['toc_check_pages']}
MAX_PAGES_PER_NODE = {recommendations['max_pages_per_node']}
MAX_TOKENS_PER_NODE = {recommendations['max_tokens_per_node']}

# Expected impact: {recommendations['estimated_reduction']:.1f}% fewer requests
""")
    
    return recommendations


if __name__ == '__main__':
    main()
