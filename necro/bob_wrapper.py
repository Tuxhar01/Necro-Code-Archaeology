"""
Bob 2.0 Integration Wrapper
Real integration: Bob 2.0 = the AI assistant analyzing code via chat.
Batch mode: Bob analyzes all modules and generates all artifacts in batch files.
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

from necro.config import config


class BobWrapper:
    """
    Wrapper for Bob 2.0 (AI assistant) integration - Batch Mode.
    
    Bob 2.0 is the AI assistant you're chatting with. The workflow is:
    1. Necro prepares batch prompts for classifications and artifacts
    2. User asks Bob (via chat) to analyze all modules and generate artifacts
    3. Bob provides real analysis as JSON arrays
    4. User saves Bob's responses to:
       - results/classification_batch.json (verdicts)
       - results/artifacts_batch.json (generated artifacts)
    5. Necro reads those files and matches by "item" field
    
    No mocks, no templates - everything comes from real AI analysis.
    """
    
    def __init__(self):
        """Initialize Bob wrapper."""
        self.session_logs = []
        self.batch_file = config.RESULTS_DIR / "classification_batch.json"
        self.artifacts_file = config.RESULTS_DIR / "artifacts_batch.json"
        self.batch_classifications = None
        self.batch_artifacts = None
    
    def load_batch_classifications(self):
        """
        Load all classifications from the batch file.
        This should be called once before analyzing any modules.
        """
        if not self.batch_file.exists():
            raise FileNotFoundError(
                f"Batch classification file not found: {self.batch_file}\n"
                f"Please save Bob's JSON array response to this file."
            )
        
        with open(self.batch_file) as f:
            self.batch_classifications = json.load(f)
        
        # Validate it's a list
        if not isinstance(self.batch_classifications, list):
            raise ValueError("Batch file must contain a JSON array of classifications")
        
        print(f"\n[OK] Loaded {len(self.batch_classifications)} classifications from batch file")
    
    def load_batch_artifacts(self):
        """
        Load all artifacts from the batch file.
        This should be called once before generating any artifacts.
        """
        if not self.artifacts_file.exists():
            raise FileNotFoundError(
                f"Batch artifacts file not found: {self.artifacts_file}\n"
                f"Please save Bob's JSON array of artifacts to this file."
            )
        
        with open(self.artifacts_file, encoding='utf-8') as f:
            self.batch_artifacts = json.load(f)
        
        # Validate it's a list
        if not isinstance(self.batch_artifacts, list):
            raise ValueError("Artifacts file must contain a JSON array")
        
        print(f"\n[OK] Loaded {len(self.batch_artifacts)} artifacts from batch file")
    
    def analyze_module(self, module_info: Dict[str, Any], repo_context: str) -> Dict[str, Any]:
        """
        Get classification for a module from the batch file.
        
        Args:
            module_info: Dictionary with module details (name, path, code)
            repo_context: Full repository context (not used in batch mode)
            
        Returns:
            Dictionary with verdict, confidence, evidence from Bob
        """
        # Load batch file if not already loaded
        if self.batch_classifications is None:
            self.load_batch_classifications()
        
        module_name = module_info['name']
        
        # Find this module's classification in the batch
        classification = None
        for item in self.batch_classifications:
            if item.get('item') == module_name:
                classification = item
                break
        
        if classification is None:
            raise ValueError(
                f"No classification found for module '{module_name}' in batch file. "
                f"Available items: {[c.get('item') for c in self.batch_classifications]}"
            )
        
        # Convert to expected format
        result = {
            'verdict': classification['verdict'],
            'confidence': classification['confidence'],
            'evidence': [classification['evidence']],  # Wrap single evidence string in list
            'reasoning': classification['evidence']  # Use evidence as reasoning
        }
        
        # Validate required fields
        required_fields = ['verdict', 'confidence']
        missing = [f for f in required_fields if f not in result]
        if missing:
            raise ValueError(f"Classification for '{module_name}' missing required fields: {missing}")
        
        return result
    
    def generate_artifact(self, classification_result: Dict[str, Any], artifact_type: str) -> str:
        """
        Get artifact content from the batch file.
        
        Args:
            classification_result: The classification result
            artifact_type: Type of artifact to generate
            
        Returns:
            Generated artifact content from Bob
        """
        # Load artifacts file if not already loaded
        if self.batch_artifacts is None:
            self.load_batch_artifacts()
        
        module_name = classification_result['module_name']
        
        # Find this module's artifact in the batch
        artifact = None
        for item in self.batch_artifacts:
            if item.get('item') == module_name and item.get('artifact_type') == artifact_type:
                artifact = item
                break
        
        if artifact is None:
            raise ValueError(
                f"No {artifact_type} artifact found for module '{module_name}' in batch file. "
                f"Available: {[(a.get('item'), a.get('artifact_type')) for a in self.batch_artifacts]}"
            )
        
        return artifact['content']
    
    def generate_batch_prompt(self, modules: List[Dict[str, Any]], repo_context: str) -> str:
        """
        Generate a single prompt for Bob to analyze all modules at once.
        
        Args:
            modules: List of module info dictionaries
            repo_context: Full repository context
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""ACT AS: A senior code auditor and legacy-systems archaeologist. You are skeptical by default — you never conclude code is dead without exhausting indirect usage paths, and you never hedge into "no verdict" as an easy out.

REQUEST: Using your full access to this repository right now, actually open and inspect these {len(modules)} files/functions — do not rely on any prior conclusions, re-derive each verdict from the current code:

"""
        
        for i, module in enumerate(modules, 1):
            prompt += f"{i}. {module['name']} — {module['path']}\n"
        
        prompt += f"""
Repository Context:
{repo_context}

For each, search the actual repository for direct calls, imports, string-based dispatch tables (e.g. router.py, config/routes.json), and any dynamic/reflection-based imports. Quote the specific line or file content you found as evidence — do not reuse phrasing from earlier responses.

TERMS:
- verdict: one of ["Safe to Delete", "Secretly Load-Bearing", "Undocumented but Valuable", "Normal - No Action"]
- confidence: "High" | "Medium" | "Low"
- evidence: 1-2 sentences citing the specific file/line you actually found

Return ONLY valid JSON, no other text, in this exact schema:
[
  {{"item": "...", "verdict": "...", "confidence": "...", "evidence": "..."}}
]
"""
        
        return prompt

# Made with Bob
