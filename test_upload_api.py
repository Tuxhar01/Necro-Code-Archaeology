#!/usr/bin/env python3
"""Test script for upload API endpoint."""

import requests

def test_upload():
    """Test the upload endpoint."""
    url = 'http://localhost:8000/api/analyze-upload'
    
    print("Testing upload API endpoint...")
    print(f"URL: {url}")
    
    # Test with the test repository ZIP
    with open('test_repo.zip', 'rb') as f:
        files = {'file': ('test_repo.zip', f, 'application/zip')}
        
        print("\nUploading test_repo.zip...")
        response = requests.post(url, files=files)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✓ Upload successful!")
            print(f"\nSummary:")
            print(f"  Modules analyzed: {data['summary']['modules_analyzed']}")
            print(f"  Safe to delete: {data['summary']['safe_to_delete']}")
            print(f"  Load-bearing: {data['summary']['load_bearing']}")
            print(f"  Needs docs: {data['summary']['needs_docs']}")
            print(f"  Normal: {data['summary']['normal']}")
            
            print(f"\nResults:")
            for result in data['results']:
                print(f"  - {result['module_name']}: {result['verdict']} ({result['confidence']})")
        else:
            print(f"\n✗ Upload failed!")
            print(f"Response: {response.text}")

if __name__ == '__main__':
    test_upload()

# Made with Bob
