"""
Secure ZIP upload handler for Necro.
Handles multipart/form-data uploads with security constraints.
"""

import os
import tempfile
import zipfile
import io
from pathlib import Path
from typing import Tuple, Optional


class UploadRejected(Exception):
    """Raised when an upload is rejected for security reasons."""
    pass


class UploadHandler:
    """Handles secure ZIP file uploads and extraction."""
    
    # Security limits (configurable via environment variables)
    MAX_UPLOAD_SIZE = int(os.getenv("NECRO_MAX_UPLOAD_MB", "20")) * 1024 * 1024  # 20 MB default
    MAX_EXTRACTED_SIZE = int(os.getenv("NECRO_MAX_EXTRACTED_MB", "80")) * 1024 * 1024  # 80 MB default
    MAX_FILE_COUNT = int(os.getenv("NECRO_MAX_FILE_COUNT", "2000"))  # 2000 files default
    CHUNK_SIZE = 64 * 1024  # 64 KB chunks
    
    @classmethod
    def safe_extract_zip(cls, zip_data: bytes, extract_to: Optional[Path] = None) -> Path:
        """
        Safely extract a ZIP file with security checks.
        
        Args:
            zip_data: Raw ZIP file bytes
            extract_to: Optional extraction directory (creates temp dir if None)
            
        Returns:
            Path to extraction directory
            
        Raises:
            UploadRejected: If security checks fail
        """
        # Check compressed size
        if len(zip_data) > cls.MAX_UPLOAD_SIZE:
            raise UploadRejected(
                f"Upload too large: {len(zip_data)} bytes exceeds {cls.MAX_UPLOAD_SIZE} bytes"
            )
        
        # Create extraction directory
        if extract_to is None:
            extract_to = Path(tempfile.mkdtemp(prefix="necro_upload_"))
        else:
            extract_to.mkdir(parents=True, exist_ok=True)
        
        try:
            # Validate ZIP file
            with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
                # Check file count
                if len(zf.namelist()) > cls.MAX_FILE_COUNT:
                    raise UploadRejected(
                        f"Too many files: {len(zf.namelist())} exceeds {cls.MAX_FILE_COUNT}"
                    )
                
                # Check total uncompressed size and validate paths
                total_size = 0
                for info in zf.infolist():
                    # Security check: reject symlinks
                    if cls._is_symlink(info):
                        raise UploadRejected(
                            f"Symlinks not allowed: {info.filename}"
                        )
                    
                    # Security check: validate path
                    if not cls._is_safe_path(info.filename, extract_to):
                        raise UploadRejected(
                            f"Path traversal attempt detected: {info.filename}"
                        )
                    
                    # Check uncompressed size
                    total_size += info.file_size
                    if total_size > cls.MAX_EXTRACTED_SIZE:
                        raise UploadRejected(
                            f"Extracted size {total_size} bytes exceeds {cls.MAX_EXTRACTED_SIZE} bytes"
                        )
                
                # Extract all files (already validated)
                for info in zf.infolist():
                    # Skip directories and symlinks
                    if info.is_dir() or cls._is_symlink(info):
                        continue
                    
                    # Extract file
                    target_path = extract_to / info.filename
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with zf.open(info) as source, open(target_path, 'wb') as target:
                        while True:
                            chunk = source.read(cls.CHUNK_SIZE)
                            if not chunk:
                                break
                            target.write(chunk)
            
            return extract_to
            
        except zipfile.BadZipFile:
            raise UploadRejected("Invalid ZIP file")
        except Exception as e:
            # Clean up on error
            if extract_to and extract_to.exists():
                cls._cleanup_directory(extract_to)
            raise
    
    @staticmethod
    def _is_symlink(zip_info: zipfile.ZipInfo) -> bool:
        """Check if a ZIP entry is a symlink."""
        # Check for symlink flag in external attributes
        return (zip_info.external_attr >> 16) & 0o170000 == 0o120000
    
    @staticmethod
    def _is_safe_path(filename: str, extract_to: Path) -> bool:
        """
        Validate that a ZIP entry path is safe.
        Rejects absolute paths, drive letters, and path traversal attempts.
        """
        # Reject absolute paths
        if os.path.isabs(filename):
            return False
        
        # Reject Windows drive letters
        if len(filename) >= 2 and filename[1] == ':':
            return False
        
        # Normalize and resolve the path
        try:
            target_path = (extract_to / filename).resolve()
            # Ensure the resolved path is within extract_to
            target_path.relative_to(extract_to.resolve())
            return True
        except (ValueError, OSError):
            return False
    
    @staticmethod
    def _cleanup_directory(directory: Path) -> None:
        """Recursively remove a directory and its contents."""
        import shutil
        try:
            shutil.rmtree(directory)
        except Exception:
            pass  # Best effort cleanup
    
    @classmethod
    def find_analysis_root(cls, extract_dir: Path) -> Path:
        """
        Find the root directory for analysis.
        Handles cases where ZIP contains a single top-level directory.
        
        Args:
            extract_dir: Extracted ZIP directory
            
        Returns:
            Path to analysis root
        """
        # List top-level items
        items = list(extract_dir.iterdir())
        
        # If there's exactly one directory at the top level, use it as root
        if len(items) == 1 and items[0].is_dir():
            return items[0]
        
        # Otherwise, use the extract directory itself
        return extract_dir
    
    @classmethod
    def cleanup(cls, extract_dir: Path) -> None:
        """
        Clean up extracted files.
        
        Args:
            extract_dir: Directory to clean up
        """
        cls._cleanup_directory(extract_dir)


def parse_multipart_data(content_type: str, body: bytes) -> Tuple[Optional[bytes], Optional[str]]:
    """
    Parse multipart/form-data to extract ZIP file.
    
    Args:
        content_type: Content-Type header value
        body: Request body bytes
        
    Returns:
        Tuple of (zip_data, filename) or (None, None) if not found
    """
    if not content_type or not content_type.startswith('multipart/form-data'):
        return None, None
    
    # Extract boundary
    boundary = None
    for part in content_type.split(';'):
        part = part.strip()
        if part.startswith('boundary='):
            boundary = part.split('=', 1)[1].strip('"')
            break
    
    if not boundary:
        return None, None
    
    # Parse multipart data
    boundary_bytes = ('--' + boundary).encode()
    parts = body.split(boundary_bytes)
    
    for part in parts:
        if not part or part == b'--\r\n' or part == b'--':
            continue
        
        # Split headers and content
        if b'\r\n\r\n' in part:
            headers_section, content = part.split(b'\r\n\r\n', 1)
        elif b'\n\n' in part:
            headers_section, content = part.split(b'\n\n', 1)
        else:
            continue
        
        # Parse headers
        headers = headers_section.decode('utf-8', errors='ignore')
        
        # Check if this is a file upload
        if 'filename=' in headers and 'Content-Disposition' in headers:
            # Extract filename
            filename = None
            for line in headers.split('\n'):
                if 'filename=' in line:
                    # Extract filename from Content-Disposition header
                    parts = line.split('filename=')
                    if len(parts) > 1:
                        filename = parts[1].strip().strip('"').strip("'")
                        break
            
            # Remove trailing boundary markers
            content = content.rstrip(b'\r\n').rstrip(b'--')
            
            return content, filename
    
    return None, None

# Made with Bob
