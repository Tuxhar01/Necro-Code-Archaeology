"""
Artifact Generator
Generates appropriate artifacts based on classification verdict.
"""

from pathlib import Path
from typing import Dict, Any
from dataclasses import asdict

from necro.config import config
from necro.bob_wrapper import BobWrapper
from necro.classifier import ClassificationResult


class ArtifactGenerator:
    """Generates appropriate artifacts based on verdict."""
    
    def __init__(self, bob_wrapper: BobWrapper):
        """
        Initialize artifact generator.
        
        Args:
            bob_wrapper: Bob wrapper instance for generating artifacts
        """
        self.bob = bob_wrapper
        self.artifacts_dir = config.ARTIFACTS_DIR
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_for_verdict(self, classification_result: ClassificationResult) -> str:
        """
        Route to appropriate generator based on verdict.
        
        Args:
            classification_result: The classification result
            
        Returns:
            Path to generated artifact (empty string if no artifact)
        """
        verdict = classification_result.verdict
        
        print(f"\nGenerating artifact for verdict: {verdict}")
        
        if verdict == "Safe to Delete":
            return self.generate_deletion_artifact(classification_result)
        elif verdict == "Secretly Load-Bearing":
            return self.generate_adr_artifact(classification_result)
        elif verdict == "Undocumented but Valuable":
            return self.generate_documentation(classification_result)
        else:
            print(f"No artifact needed for verdict: {verdict}")
            return ""
    
    def generate_deletion_artifact(self, result: ClassificationResult) -> str:
        """
        Create deletion patch and safety note.
        
        Args:
            result: Classification result
            
        Returns:
            Path to generated artifact
        """
        print(f"  > Generating deletion patch...")
        
        # Generate artifact using Bob
        artifact_content = self.bob.generate_artifact(asdict(result), "deletion")
        
        # Save to file
        artifact_dir = self.artifacts_dir / "deletions"
        artifact_dir.mkdir(exist_ok=True)
        
        artifact_path = artifact_dir / f"{self._sanitize_name(result.module_name)}_deletion.patch"
        artifact_path.write_text(artifact_content, encoding='utf-8')
        
        print(f"  [OK] Saved to: {artifact_path.relative_to(config.PROJECT_ROOT)}")
        return str(artifact_path.relative_to(config.PROJECT_ROOT))
    
    def generate_adr_artifact(self, result: ClassificationResult) -> str:
        """
        Create ADR snippet and enhanced docstring.
        
        Args:
            result: Classification result
            
        Returns:
            Path to generated artifact
        """
        print(f"  > Generating ADR and enhanced docstring...")
        
        # Generate artifact using Bob
        artifact_content = self.bob.generate_artifact(asdict(result), "adr")
        
        # Save to file
        artifact_dir = self.artifacts_dir / "adrs"
        artifact_dir.mkdir(exist_ok=True)
        
        artifact_path = artifact_dir / f"{self._sanitize_name(result.module_name)}_adr.md"
        artifact_path.write_text(artifact_content, encoding='utf-8')
        
        print(f"  [OK] Saved to: {artifact_path.relative_to(config.PROJECT_ROOT)}")
        return str(artifact_path.relative_to(config.PROJECT_ROOT))
    
    def generate_documentation(self, result: ClassificationResult) -> str:
        """
        Create comprehensive documentation.
        
        Args:
            result: Classification result
            
        Returns:
            Path to generated artifact
        """
        print(f"  > Generating documentation...")
        
        # Generate artifact using Bob
        artifact_content = self.bob.generate_artifact(asdict(result), "documentation")
        
        # Save to file
        artifact_dir = self.artifacts_dir / "documentation"
        artifact_dir.mkdir(exist_ok=True)
        
        artifact_path = artifact_dir / f"{self._sanitize_name(result.module_name)}_docs.md"
        artifact_path.write_text(artifact_content, encoding='utf-8')
        
        print(f"  [OK] Saved to: {artifact_path.relative_to(config.PROJECT_ROOT)}")
        return str(artifact_path.relative_to(config.PROJECT_ROOT))
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize module name for use as filename."""
        return name.replace(".", "_").replace("/", "_").replace("\\", "_")

# Made with Bob
