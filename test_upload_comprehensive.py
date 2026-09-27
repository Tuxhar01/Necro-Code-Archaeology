#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive test suite for repository upload MVP.
Tests all security and functionality requirements.
"""

import urllib.request
import urllib.error
import json
import tempfile
import zipfile
import io
from pathlib import Path
import time
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')


class TestResults:
    """Track test results."""
    def __init__(self):
        self.passed = []
        self.failed = []
    
    def add_pass(self, test_name):
        self.passed.append(test_name)
        print(f"[PASS] {test_name}")
    
    def add_fail(self, test_name, reason):
        self.failed.append((test_name, reason))
        print(f"[FAIL] {test_name}")
        print(f"  Reason: {reason}")
    
    def summary(self):
        total = len(self.passed) + len(self.failed)
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Total Tests: {total}")
        print(f"Passed: {len(self.passed)}")
        print(f"Failed: {len(self.failed)}")
        
        if self.failed:
            print("\nFailed Tests:")
            for name, reason in self.failed:
                print(f"  - {name}: {reason}")
        
        return len(self.failed) == 0


def make_request(url, data, boundary, expect_success=True):
    """Make HTTP request with multipart data."""
    body = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="file"; filename="test.zip"\r\n'
        f'Content-Type: application/zip\r\n\r\n'
    ).encode() + data + f'\r\n--{boundary}--\r\n'.encode()
    
    req = urllib.request.Request(url, data=body, method='POST')
    req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
    
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, response.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def create_test_zip(files):
    """Create a test ZIP file in memory."""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for filename, content in files.items():
            zf.writestr(filename, content)
    return zip_buffer.getvalue()


def test_demo_regression(results):
    """Test 1: Verify existing demo results are intact."""
    print("\n[Test 1] Demo Regression Test")
    print("-" * 70)
    
    try:
        results_file = Path('results/results.json')
        if not results_file.exists():
            results.add_fail("Demo Regression", "results.json not found")
            return
        
        with open(results_file) as f:
            data = json.load(f)
        
        # Verify structure
        if data.get('modules_analyzed') != 5:
            results.add_fail("Demo Regression", f"Expected 5 modules, got {data.get('modules_analyzed')}")
            return
        
        # Verify all 5 demo modules exist
        expected_modules = {
            'calculate_legacy_metrics',
            'format_old_date',
            'track_user_event',
            'validate_input',
            'process_request'
        }
        
        actual_modules = {r['module_name'] for r in data['results']}
        
        if expected_modules != actual_modules:
            results.add_fail("Demo Regression", f"Module mismatch: {expected_modules} vs {actual_modules}")
            return
        
        results.add_pass("Demo Regression")
        
    except Exception as e:
        results.add_fail("Demo Regression", str(e))


def test_successful_upload(results):
    """Test 2: Successful ZIP upload and analysis."""
    print("\n[Test 2] Successful ZIP Upload")
    print("-" * 70)
    
    try:
        # Create valid test ZIP
        test_files = {
            'test_module.py': '''
def test_function():
    """Test function."""
    return True

def unused_function():
    """This is unused."""
    pass
''',
            'main.py': '''
from test_module import test_function

def main():
    test_function()
'''
        }
        
        zip_data = create_test_zip(test_files)
        
        url = 'http://localhost:8000/api/analyze-upload'
        boundary = '----TestBoundary123'
        
        status, response = make_request(url, zip_data, boundary)
        
        if status != 200:
            results.add_fail("Successful Upload", f"HTTP {status}: {response}")
            return
        
        data = json.loads(response)
        
        # Verify response structure
        if 'summary' not in data or 'results' not in data:
            results.add_fail("Successful Upload", "Invalid response structure")
            return
        
        if data['summary']['modules_analyzed'] < 1:
            results.add_fail("Successful Upload", "No modules analyzed")
            return
        
        results.add_pass("Successful Upload")
        
    except Exception as e:
        results.add_fail("Successful Upload", str(e))


def test_invalid_zip(results):
    """Test 3: Invalid ZIP file rejection."""
    print("\n[Test 3] Invalid ZIP Rejection")
    print("-" * 70)
    
    try:
        # Send non-ZIP data
        invalid_data = b"This is not a ZIP file"
        
        url = 'http://localhost:8000/api/analyze-upload'
        boundary = '----TestBoundary123'
        
        status, response = make_request(url, invalid_data, boundary, expect_success=False)
        
        if status == 200:
            results.add_fail("Invalid ZIP Rejection", "Server accepted invalid ZIP")
            return
        
        if status != 400:
            results.add_fail("Invalid ZIP Rejection", f"Expected 400, got {status}")
            return
        
        results.add_pass("Invalid ZIP Rejection")
        
    except Exception as e:
        results.add_fail("Invalid ZIP Rejection", str(e))


def test_path_traversal(results):
    """Test 4: Path traversal attack prevention."""
    print("\n[Test 4] Path Traversal Prevention")
    print("-" * 70)
    
    try:
        # Create ZIP with path traversal attempt
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Try to write outside extraction directory
            zf.writestr('../../../etc/passwd', 'malicious content')
            zf.writestr('normal_file.py', 'print("hello")')
        
        zip_data = zip_buffer.getvalue()
        
        url = 'http://localhost:8000/api/analyze-upload'
        boundary = '----TestBoundary123'
        
        status, response = make_request(url, zip_data, boundary, expect_success=False)
        
        if status == 200:
            results.add_fail("Path Traversal Prevention", "Server accepted path traversal ZIP")
            return
        
        if status != 400:
            results.add_fail("Path Traversal Prevention", f"Expected 400, got {status}")
            return
        
        results.add_pass("Path Traversal Prevention")
        
    except Exception as e:
        results.add_fail("Path Traversal Prevention", str(e))


def test_oversized_upload(results):
    """Test 5: Oversized upload rejection."""
    print("\n[Test 5] Oversized Upload Rejection")
    print("-" * 70)
    
    try:
        # Create a ZIP that's too large (> 20 MB)
        large_content = b'x' * (21 * 1024 * 1024)  # 21 MB
        
        url = 'http://localhost:8000/api/analyze-upload'
        boundary = '----TestBoundary123'
        
        status, response = make_request(url, large_content, boundary, expect_success=False)
        
        if status == 200:
            results.add_fail("Oversized Upload Rejection", "Server accepted oversized upload")
            return
        
        if status not in (400, 413):
            results.add_fail("Oversized Upload Rejection", f"Expected 400/413, got {status}")
            return
        
        results.add_pass("Oversized Upload Rejection")
        
    except Exception as e:
        results.add_fail("Oversized Upload Rejection", str(e))


def test_temp_cleanup(results):
    """Test 6: Temporary directory cleanup."""
    print("\n[Test 6] Temporary Directory Cleanup")
    print("-" * 70)
    
    try:
        # Get temp directory before upload
        temp_dir = Path(tempfile.gettempdir())
        before_dirs = set(temp_dir.glob('necro_upload_*'))
        
        # Upload a file
        test_files = {'test.py': 'print("test")'}
        zip_data = create_test_zip(test_files)
        
        url = 'http://localhost:8000/api/analyze-upload'
        boundary = '----TestBoundary123'
        
        status, response = make_request(url, zip_data, boundary)
        
        # Wait a moment for cleanup
        time.sleep(0.5)
        
        # Check temp directory after upload
        after_dirs = set(temp_dir.glob('necro_upload_*'))
        
        # Should be no new temp directories
        new_dirs = after_dirs - before_dirs
        
        if new_dirs:
            results.add_fail("Temp Cleanup", f"Temp directories not cleaned: {new_dirs}")
            return
        
        results.add_pass("Temp Cleanup")
        
    except Exception as e:
        results.add_fail("Temp Cleanup", str(e))


def test_unrelated_post_404(results):
    """Test 7: Unrelated POST endpoints return 404."""
    print("\n[Test 7] Unrelated POST -> 404")
    print("-" * 70)
    
    try:
        url = 'http://localhost:8000/api/some-other-endpoint'
        
        req = urllib.request.Request(url, data=b'test', method='POST')
        
        try:
            with urllib.request.urlopen(req) as response:
                results.add_fail("Unrelated POST 404", f"Expected 404, got {response.status}")
                return
        except urllib.error.HTTPError as e:
            if e.code != 404:
                results.add_fail("Unrelated POST 404", f"Expected 404, got {e.code}")
                return
        
        results.add_pass("Unrelated POST 404")
        
    except Exception as e:
        results.add_fail("Unrelated POST 404", str(e))


def test_demo_button(results):
    """Test 8: Verify demo results can be loaded."""
    print("\n[Test 8] Demo Button Functionality")
    print("-" * 70)
    
    try:
        # This tests that the demo results.json is accessible
        url = 'http://localhost:8000/results/results.json'
        
        req = urllib.request.Request(url, method='GET')
        
        with urllib.request.urlopen(req) as response:
            if response.status != 200:
                results.add_fail("Demo Button", f"Cannot load results.json: {response.status}")
                return
            
            data = json.loads(response.read().decode())
            
            if data.get('modules_analyzed') != 5:
                results.add_fail("Demo Button", "Demo results corrupted")
                return
        
        results.add_pass("Demo Button")
        
    except Exception as e:
        results.add_fail("Demo Button", str(e))


def main():
    """Run all tests."""
    print("="*70)
    print("NECRO REPOSITORY UPLOAD MVP - COMPREHENSIVE TEST SUITE")
    print("="*70)
    print("\nServer must be running at http://localhost:8000")
    print("Start with: python scripts/serve_dashboard.py")
    print()
    
    # Check if server is running
    try:
        req = urllib.request.Request('http://localhost:8000', method='GET')
        urllib.request.urlopen(req, timeout=2)
    except Exception as e:
        print(f"X ERROR: Server not running at http://localhost:8000")
        print(f"  {e}")
        print("\nPlease start the server first:")
        print("  python scripts/serve_dashboard.py")
        return 1
    
    print("OK Server is running\n")
    
    results = TestResults()
    
    # Run all tests
    test_demo_regression(results)
    test_successful_upload(results)
    test_invalid_zip(results)
    test_path_traversal(results)
    test_oversized_upload(results)
    test_temp_cleanup(results)
    test_unrelated_post_404(results)
    test_demo_button(results)
    
    # Print summary
    success = results.summary()
    
    return 0 if success else 1


if __name__ == '__main__':
    exit(main())

# Made with Bob