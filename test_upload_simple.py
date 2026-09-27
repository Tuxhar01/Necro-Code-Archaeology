#!/usr/bin/env python3
"""Simple test script for upload API endpoint using urllib."""

import urllib.request
import json

def test_upload():
    """Test the upload endpoint."""
    url = 'http://localhost:8000/api/analyze-upload'
    
    print("Testing upload API endpoint...")
    print(f"URL: {url}")
    
    # Read the ZIP file
    with open('test_repo.zip', 'rb') as f:
        zip_data = f.read()
    
    # Create multipart form data manually
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    body = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="file"; filename="test_repo.zip"\r\n'
        f'Content-Type: application/zip\r\n\r\n'
    ).encode() + zip_data + f'\r\n--{boundary}--\r\n'.encode()
    
    # Create request
    req = urllib.request.Request(url, data=body, method='POST')
    req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
    
    try:
        print("\nUploading test_repo.zip...")
        with urllib.request.urlopen(req) as response:
            status = response.status
            data = json.loads(response.read().decode())
            
            print(f"Status Code: {status}")
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
                
    except urllib.error.HTTPError as e:
        print(f"\n✗ Upload failed!")
        print(f"Status Code: {e.code}")
        print(f"Response: {e.read().decode()}")
    except Exception as e:
        print(f"\n✗ Error: {e}")

if __name__ == '__main__':
    test_upload()

# Made with Bob
