"""
Module Classifier
Orchestrates the classification of suspect modules using Bob 2.0.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass, asdict

from necro.config import config
from necro.bob_wrapper import BobWrapper
from necro.evidence_logger import EvidenceLogger


@dataclass
class ClassificationResult:
    """Structured classification result."""
    module_name: str
    module_path: str
    verdict: str
    confidence: str
    evidence: List[str]
    reasoning: str
    timestamp: str
    bob_session_id: str
    artifact_path: str = ""
    evidence_path: str = ""


class ModuleClassifier:
    """Orchestrates the classification of suspect modules."""
    
    def __init__(self, bob_wrapper: BobWrapper, evidence_logger: EvidenceLogger):
        """
        Initialize classifier.
        
        Args:
            bob_wrapper: Bob wrapper instance
            evidence_logger: Evidence logger instance
        """
        self.bob = bob_wrapper
        self.logger = evidence_logger
        self.repo_context = self._gather_repo_context()
    
    def classify_module(self, module_info: Dict[str, Any]) -> ClassificationResult:
        """
        Full classification workflow for one module.
        
        Args:
            module_info: Dictionary with module details
            
        Returns:
            ClassificationResult object
        """
        print(f"\n{'='*80}")
        print(f"Classifying: {module_info['name']}")
        print(f"{'='*80}")
        
        # Load module code
        module_code = self._load_module_code(module_info['path'])
        module_info['code'] = module_code
        
        # Call Bob for analysis
        print(f"[1/4] Sending to Bob for analysis...")
        classification = self.bob.analyze_module(module_info, self.repo_context)
        
        # Parse and validate response
        print(f"[2/4] Parsing Bob's response...")
        result = self._parse_classification(module_info, classification)
        
        # Log evidence
        print(f"[3/4] Logging evidence...")
        session_data = {
            "session_id": result.bob_session_id,
            "timestamp": result.timestamp,
            "mode": "chat",
            "module_name": result.module_name,
            "module_path": result.module_path,
            "classification": asdict(result),
            "prompt": f"Classification prompt for {result.module_name}",
            "raw_response": classification
        }
        evidence_dir = self.logger.log_session(result.module_name, session_data)
        result.evidence_path = str(evidence_dir.relative_to(config.PROJECT_ROOT))
        
        print(f"[4/4] Classification complete!")
        print(f"Verdict: {result.verdict} (Confidence: {result.confidence})")
        print(f"Evidence: {len(result.evidence)} items")
        
        return result
    
    def classify_all(self, module_list: List[Dict[str, Any]]) -> List[ClassificationResult]:
        """
        Process all modules in sequence.
        
        Args:
            module_list: List of module info dictionaries
            
        Returns:
            List of ClassificationResult objects
        """
        results = []
        
        print(f"\n{'#'*80}")
        print(f"# NECRO CLASSIFICATION PIPELINE")
        print(f"# Analyzing {len(module_list)} modules")
        print(f"{'#'*80}\n")
        
        for i, module_info in enumerate(module_list, 1):
            print(f"\n[Module {i}/{len(module_list)}]")
            try:
                result = self.classify_module(module_info)
                results.append(result)
            except Exception as e:
                print(f"ERROR classifying {module_info['name']}: {e}")
                # Create error result
                error_result = ClassificationResult(
                    module_name=module_info['name'],
                    module_path=module_info['path'],
                    verdict="Error",
                    confidence="Low",
                    evidence=[f"Classification failed: {str(e)}"],
                    reasoning=f"An error occurred during classification: {str(e)}",
                    timestamp=datetime.now().isoformat(),
                    bob_session_id="error"
                )
                results.append(error_result)
        
        print(f"\n{'#'*80}")
        print(f"# CLASSIFICATION COMPLETE")
        print(f"# {len(results)} modules processed")
        print(f"{'#'*80}\n")
        
        return results
    
    def _load_module_code(self, module_path: str) -> str:
        """Load the source code of a module."""
        full_path = config.PROJECT_ROOT / module_path
        
        if not full_path.exists():
            return f"# File not found: {module_path}"
        
        try:
            return full_path.read_text()
        except Exception as e:
            return f"# Error reading file: {e}"
    
    def _gather_repo_context(self) -> str:
        """
        Gather repository context for Bob.
        Includes file structure and key files.
        """
        context_lines = [
            "REPOSITORY STRUCTURE:",
            "",
            "demo_repo/",
            "├── src/",
            "│   ├── main.py          # Main application entry point",
            "│   ├── utils.py         # Utility functions",
            "│   ├── router.py        # Dynamic routing with string-based dispatch",
            "│   ├── analytics.py     # Analytics tracking functions",
            "│   └── legacy_feature.py # Old metrics system",
            "└── config/",
            "    └── routes.json     # Route configuration with handler mappings",
            "",
            "KEY PATTERNS TO LOOK FOR:",
            "- Direct imports and function calls",
            "- String-based dispatch in router.py (HANDLERS dict)",
            "- Config file references in routes.json",
            "- Dynamic imports using importlib",
            "",
        ]
        
        # Include router.py content (critical for detecting indirect usage)
        router_path = config.DEMO_REPO_PATH / "src" / "router.py"
        if router_path.exists():
            context_lines.extend([
                "ROUTER.PY CONTENT (shows string-based dispatch):",
                "-" * 60,
                router_path.read_text(),
                "-" * 60,
                "",
            ])
        
        # Include routes.json content
        routes_path = config.DEMO_REPO_PATH / "config" / "routes.json"
        if routes_path.exists():
            context_lines.extend([
                "ROUTES.JSON CONTENT (config-driven references):",
                "-" * 60,
                routes_path.read_text(),
                "-" * 60,
                "",
            ])
        
        return "\n".join(context_lines)
    
    def _parse_classification(self, module_info: Dict[str, Any], 
                            classification: Dict[str, Any]) -> ClassificationResult:
        """
        Parse and validate Bob's classification response.
        
        Args:
            module_info: Original module information
            classification: Bob's response
            
        Returns:
            ClassificationResult object
        """
        # Generate session ID
        session_id = f"bob_session_{int(time.time())}_{module_info['name']}"
        
        # Extract fields with defaults
        return ClassificationResult(
            module_name=module_info['name'],
            module_path=module_info['path'],
            verdict=classification.get('verdict', 'Unknown'),
            confidence=classification.get('confidence', 'Low'),
            evidence=classification.get('evidence', []),
            reasoning=classification.get('reasoning', 'No reasoning provided'),
            timestamp=datetime.now().isoformat(),
            bob_session_id=session_id
        )

# Made with Bob
