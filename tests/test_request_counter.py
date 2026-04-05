"""Tests for LLM request counting instrumentation."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pageindex.utils import RequestCounter

def test_request_counter_initialization():
    counter = RequestCounter()
    assert counter.total_requests == 0
    assert counter.requests_by_stage == {}

def test_request_counter_increment():
    counter = RequestCounter()
    counter.increment('toc_detection')
    assert counter.total_requests == 1
    assert counter.requests_by_stage['toc_detection'] == 1
    
    counter.increment('toc_detection')
    counter.increment('toc_transform')
    assert counter.total_requests == 3
    assert counter.requests_by_stage['toc_detection'] == 2
    assert counter.requests_by_stage['toc_transform'] == 1

def test_request_counter_summary():
    counter = RequestCounter()
    counter.increment('stage1', tokens_in=1000, tokens_out=500)
    counter.increment('stage2', tokens_in=2000, tokens_out=800)
    
    summary = counter.get_summary()
    assert summary['total_requests'] == 2
    assert summary['total_tokens_in'] == 3000
    assert summary['total_tokens_out'] == 1300

def test_request_counter_reset():
    counter = RequestCounter()
    counter.increment('stage1')
    counter.reset()
    assert counter.total_requests == 0
    assert len(counter.requests_by_stage) == 0
