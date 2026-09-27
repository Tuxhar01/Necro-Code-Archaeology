"""
Static repository inspector for uploaded code.
Performs heuristic analysis without executing code.
"""

import ast
import re
from pathlib import Path
from typing import List, Dict, Any, Set, Optional
from datetime import datetime


class RepoInspector:
    """Static code inspector for uploaded repositories."""
    
    # File size limit for analysis
    MAX_FILE_SIZE = 300 * 1024  # 300 KB
    
    # Maximum candidates to analyze
    MAX_CANDIDATES = 60
    
    # Directories to ignore
    IGNORE_DIRS = {
        '.git', 'node_modules', 'venv', '__pycache__', '.venv',
        'env', 'build', 'dist', '.pytest_cache', '.tox',
        'vendor', 'target', 'bin', 'obj'
    }
    
    # File extensions to analyze
    SUPPORTED_EXTENSIONS = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.go': 'Go',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.java': 'Java',
        '.c': 'C',
        '.cpp': 'C++',
        '.cc': 'C++',
        '.cxx': 'C++',
        '.cs': 'C#',
    }
    
    def __init__(self, repo_root: Path):
        """
        Initialize inspector.
        
        Args:
            repo_root: Root directory of repository to analyze
        """
        self.repo_root = repo_root
        self.candidates = []
        self.file_contents = {}  # Cache file contents
    
    def analyze(self) -> Dict[str, Any]:
        """
        Analyze the repository and return results.
        
        Returns:
            Dictionary with analysis results and summary
        """
        print(f"[RepoInspector] Analyzing repository at: {self.repo_root}")
        
        # Discover candidates
        self._discover_candidates()
        
        # Limit to MAX_CANDIDATES
        if len(self.candidates) > self.MAX_CANDIDATES:
            print(f"[RepoInspector] Limiting analysis to {self.MAX_CANDIDATES} candidates")
            self.candidates = self.candidates[:self.MAX_CANDIDATES]
        
        # Analyze each candidate
        results = []
        for candidate in self.candidates:
            result = self._analyze_candidate(candidate)
            if result:
                results.append(result)
        
        # Generate summary
        summary = self._generate_summary(results)
        
        return {
            'results': results,
            'summary': summary,
            'generated_at': datetime.now().isoformat(),
            'source': 'static_inspection',
            'repo_root': str(self.repo_root)
        }
    
    def _discover_candidates(self) -> None:
        """Discover function/class candidates in the repository."""
        print(f"[RepoInspector] Discovering candidates...")
        
        for file_path in self._walk_files():
            ext = file_path.suffix.lower()
            
            if ext not in self.SUPPORTED_EXTENSIONS:
                continue
            
            # Check file size
            try:
                if file_path.stat().st_size > self.MAX_FILE_SIZE:
                    continue
            except OSError:
                continue
            
            # Read file content
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                # Skip files with null bytes (binary)
                if '\x00' in content:
                    continue
                
                self.file_contents[file_path] = content
            except Exception:
                continue
            
            # Extract candidates based on language
            language = self.SUPPORTED_EXTENSIONS[ext]
            
            if language == 'Python':
                self._extract_python_candidates(file_path, content)
            else:
                self._extract_generic_candidates(file_path, content, language)
        
        print(f"[RepoInspector] Found {len(self.candidates)} candidates")
    
    def _walk_files(self):
        """Walk through repository files, respecting ignore rules."""
        for path in self.repo_root.rglob('*'):
            if not path.is_file():
                continue
            
            # Check if any parent directory should be ignored
            if any(ignored in path.parts for ignored in self.IGNORE_DIRS):
                continue
            
            yield path
    
    def _extract_python_candidates(self, file_path: Path, content: str) -> None:
        """Extract Python functions and classes using AST."""
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    self.candidates.append({
                        'name': node.name,
                        'type': 'function',
                        'file': file_path,
                        'line': node.lineno,
                        'language': 'Python',
                        'has_docstring': ast.get_docstring(node) is not None,
                        'node': node
                    })
                elif isinstance(node, ast.ClassDef):
                    self.candidates.append({
                        'name': node.name,
                        'type': 'class',
                        'file': file_path,
                        'line': node.lineno,
                        'language': 'Python',
                        'has_docstring': ast.get_docstring(node) is not None,
                        'node': node
                    })
        except SyntaxError:
            pass  # Skip files with syntax errors
    
    def _extract_generic_candidates(self, file_path: Path, content: str, language: str) -> None:
        """Extract candidates from non-Python files using regex."""
        # Generic function pattern (works for many C-style languages)
        func_pattern = r'(?:function\s+|def\s+|func\s+|fn\s+)?(\w+)\s*\([^)]*\)\s*\{'
        
        for match in re.finditer(func_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            self.candidates.append({
                'name': match.group(1),
                'type': 'function',
                'file': file_path,
                'line': line_num,
                'language': language,
                'has_docstring': False  # Can't reliably detect for non-Python
            })
    
    def _analyze_candidate(self, candidate: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyze a single candidate and determine verdict.
        
        Args:
            candidate: Candidate information
            
        Returns:
            Analysis result dictionary or None
        """
        name = candidate['name']
        file_path = candidate['file']
        language = candidate['language']
        
        # Count references
        direct_refs = self._count_direct_references(name, file_path)
        indirect_refs = self._count_indirect_references(name, file_path)
        
        # Determine verdict
        verdict, confidence, reasoning, evidence = self._determine_verdict(
            candidate, direct_refs, indirect_refs
        )
        
        # Build result
        rel_path = file_path.relative_to(self.repo_root)
        
        return {
            'module_name': name,
            'module_path': str(rel_path),
            'verdict': verdict,
            'confidence': confidence,
            'evidence': evidence,
            'reasoning': reasoning,
            'artifact_path': '',
            'evidence_path': '',
            'timestamp': datetime.now().isoformat(),
            'source': 'static_inspection',
            'bob_mode': 'not_analyzed_by_bob',
            'language': language,
            'line': candidate.get('line', 0),
            'type': candidate.get('type', 'unknown')
        }
    
    def _count_direct_references(self, name: str, exclude_file: Path) -> int:
        """Count direct code references (imports, calls) to a name."""
        count = 0
        
        # Use word boundary regex to match whole words only
        pattern = re.compile(r'\b' + re.escape(name) + r'\b')
        
        for file_path, content in self.file_contents.items():
            if file_path == exclude_file:
                continue
            
            # Count matches
            matches = pattern.findall(content)
            
            # Filter out matches in comments and strings (basic heuristic)
            for match in matches:
                # Get context around match
                idx = content.find(match)
                if idx == -1:
                    continue
                
                # Check if in comment (lines starting with #, //, /*)
                line_start = content.rfind('\n', 0, idx) + 1
                line = content[line_start:content.find('\n', idx)]
                
                # Skip if in comment
                if line.strip().startswith(('#', '//', '/*', '*')):
                    continue
                
                # Skip if in string literal (basic check)
                before = content[:idx]
                if before.count('"') % 2 == 1 or before.count("'") % 2 == 1:
                    continue
                
                count += 1
        
        return count
    
    def _count_indirect_references(self, name: str, exclude_file: Path) -> int:
        """Count indirect references (strings, configs, dynamic dispatch)."""
        count = 0
        
        # Look for name in strings, configs, etc.
        pattern = re.compile(r'["\'].*?' + re.escape(name) + r'.*?["\']')
        
        for file_path, content in self.file_contents.items():
            if file_path == exclude_file:
                continue
            
            # Count string/config references
            matches = pattern.findall(content)
            count += len(matches)
            
            # Look for dynamic dispatch patterns
            dispatch_patterns = [
                r'getattr\s*\([^,]+,\s*["\']' + re.escape(name) + r'["\']',
                r'__import__\s*\(["\']' + re.escape(name) + r'["\']',
                r'importlib\.import_module\s*\(["\'].*?' + re.escape(name),
                r'require\s*\(["\'].*?' + re.escape(name),
            ]
            
            for dp in dispatch_patterns:
                if re.search(dp, content):
                    count += 5  # Weight dynamic dispatch higher
        
        return count
    
    def _determine_verdict(self, candidate: Dict[str, Any], 
                          direct_refs: int, indirect_refs: int) -> tuple:
        """
        Determine verdict based on reference counts and other signals.
        
        Returns:
            Tuple of (verdict, confidence, reasoning, evidence)
        """
        name = candidate['name']
        has_docstring = candidate.get('has_docstring', False)
        language = candidate['language']
        
        evidence = []
        
        # Build evidence
        if direct_refs == 0 and indirect_refs == 0:
            evidence.append(f"No references found to '{name}' in codebase")
            verdict = "Safe to Delete"
            confidence = "Medium"
            reasoning = (
                f"Static analysis found zero direct or indirect references to '{name}'. "
                f"However, this is heuristic analysis and may miss runtime-only references, "
                f"reflection, external consumers, or generated code."
            )
        
        elif direct_refs == 0 and indirect_refs > 0:
            evidence.append(
                f"No direct code references, but {indirect_refs} string/config/dynamic references found"
            )
            verdict = "Secretly Load-Bearing"
            confidence = "Medium"
            reasoning = (
                f"'{name}' has no direct imports or calls, but appears in {indirect_refs} "
                f"string literals, config files, or dynamic dispatch patterns. This suggests "
                f"runtime-only usage that static analysis cannot fully verify."
            )
        
        elif direct_refs > 0 and not has_docstring and language == 'Python':
            evidence.append(
                f"Found {direct_refs} direct references but no docstring"
            )
            verdict = "Undocumented but Valuable"
            confidence = "Medium"
            reasoning = (
                f"'{name}' is referenced {direct_refs} times in the codebase but lacks "
                f"documentation. Static analysis suggests it's actively used but needs docs."
            )
        
        else:
            evidence.append(
                f"Found {direct_refs} direct references" + 
                (f" and {indirect_refs} indirect references" if indirect_refs > 0 else "")
            )
            verdict = "Normal - No Action"
            confidence = "Medium"
            reasoning = (
                f"'{name}' appears to be a normal, actively used component with "
                f"{direct_refs} direct references" +
                (f" and {indirect_refs} indirect references" if indirect_refs > 0 else "") +
                f". No issues detected by static analysis."
            )
        
        # Add disclaimer to evidence
        evidence.append(
            "⚠️ Static inspection only - may miss runtime behavior, reflection, "
            "external consumers, or dynamic code generation"
        )
        
        return verdict, confidence, reasoning, evidence
    
    def _generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics."""
        verdict_counts = {
            'Safe to Delete': 0,
            'Secretly Load-Bearing': 0,
            'Undocumented but Valuable': 0,
            'Normal - No Action': 0,
        }
        
        for result in results:
            verdict = result['verdict']
            if verdict in verdict_counts:
                verdict_counts[verdict] += 1
        
        return {
            'modules_analyzed': len(results),
            'safe_to_delete': verdict_counts['Safe to Delete'],
            'load_bearing': verdict_counts['Secretly Load-Bearing'],
            'needs_docs': verdict_counts['Undocumented but Valuable'],
            'normal': verdict_counts['Normal - No Action'],
        }

# Made with Bob
