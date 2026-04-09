"""Validate optimal parameters by comparing request counts."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pageindex import page_index
from pageindex.utils import reset_request_counter, get_request_counter


def test_with_parameters(pdf_path, **kwargs):
    """Test processing and return request count."""
    reset_request_counter()
    
    result = page_index(
        doc=pdf_path,
        **kwargs
    )
    
    summary = get_request_counter().get_summary()
    return result, summary


def main():
    # Check for test PDFs
    test_pdfs = [
        os.path.join('tests', 'pdfs', 'tcs_annual-report-2024-2025-trunc.pdf'),
        os.path.join('tests', 'pdfs', 'DeepSeek_R1.pdf'),
    ]
    
    pdf_path = None
    for p in test_pdfs:
        if os.path.exists(p):
            pdf_path = p
            break
    
    if not pdf_path:
        print("No test PDF found. Create one in tests/pdfs/")
        return
    
    model = "bedrock/us.amazon.nova-micro-v1:0"
    
    configurations = [
        {
            'name': 'Current (Conservative)',
            'toc_check_page_num': 20,
            'max_pages_per_node': 10,
            'max_token_num_each_node': 20000
        },
        {
            'name': 'Optimized (Balanced)',
            'toc_check_page_num': 10,
            'max_pages_per_node': 125,
            'max_token_num_each_node': 100000
        },
    ]
    
    print("="*60)
    print("PARAMETER VALIDATION: REQUEST COUNT COMPARISON")
    print("="*60)
    print(f"\nDocument: {os.path.basename(pdf_path)}")
    print(f"Model: {model}")
    print()
    
    results = []
    
    for config in configurations:
        print(f"\nTesting: {config['name']}")
        print(f"  TOC_CHECK_PAGES: {config['toc_check_page_num']}")
        print(f"  MAX_PAGES_PER_NODE: {config['max_pages_per_node']}")
        print(f"  MAX_TOKENS_PER_NODE: {config['max_token_num_each_node']:,}")
        
        try:
            result, summary = test_with_parameters(
                pdf_path,
                model=model,
                toc_check_page_num=config['toc_check_page_num'],
                max_page_num_each_node=config['max_pages_per_node'],
                max_token_num_each_node=config['max_token_num_each_node'],
                if_add_node_summary='no',
                if_add_node_id='yes'
            )
            
            summary['config_name'] = config['name']
            results.append(summary)
            
            print(f"  Result: {summary['total_requests']} requests")
            
        except Exception as e:
            print(f"  ERROR: {e}")
    
    # Print comparison table
    print("\n" + "="*60)
    print("COMPARISON TABLE")
    print("="*60)
    
    if len(results) >= 2:
        baseline = results[0]['total_requests']
        optimized = results[1]['total_requests']
        reduction = (1 - optimized/baseline) * 100 if baseline > 0 else 0
        
        print(f"\nBaseline (Current):   {baseline} requests")
        print(f"Optimized (Balanced): {optimized} requests")
        print(f"Reduction:            {reduction:.1f}%")
    
    print("\nRequest breakdown by stage:")
    for result in results:
        print(f"\n{result['config_name']}:")
        for stage, count in sorted(result['requests_by_stage'].items()):
            print(f"  {stage:30s}: {count:3d}")
    
    return results


if __name__ == '__main__':
    main()
