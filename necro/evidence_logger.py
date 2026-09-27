"""
Evidence Logger
Captures and stores Bob session evidence for submission.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from necro.config import config


class EvidenceLogger:
    """Captures and stores Bob session evidence."""
    
    def __init__(self):
        """Initialize evidence logger."""
        self.evidence_dir = config.EVIDENCE_DIR
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
    
    def log_session(self, module_name: str, session_data: Dict[str, Any]) -> Path:
        """
        Save session data to evidence/{module_name}/
        
        Args:
            module_name: Name of the module being analyzed
            session_data: Complete session information
            
        Returns:
            Path to the evidence directory for this module
        """
        # Create module-specific evidence directory
        module_evidence_dir = self.evidence_dir / self._sanitize_name(module_name)
        module_evidence_dir.mkdir(parents=True, exist_ok=True)
        
        # Save structured JSON
        session_json_path = module_evidence_dir / "session.json"
        with open(session_json_path, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        # Save human-readable text log
        session_txt_path = module_evidence_dir / "session.txt"
        with open(session_txt_path, 'w') as f:
            f.write(self._format_session_text(session_data))
        
        # Save classification details as markdown
        if "classification" in session_data:
            classification_md_path = module_evidence_dir / "classification.md"
            with open(classification_md_path, 'w') as f:
                f.write(self._format_classification_md(session_data["classification"]))
        
        return module_evidence_dir
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize module name for use as directory name."""
        return name.replace(".", "_").replace("/", "_").replace("\\", "_")
    
    def _format_session_text(self, session_data: Dict[str, Any]) -> str:
        """Format session data as human-readable text."""
        lines = [
            "=" * 80,
            "NECRO BOB SESSION LOG",
            "=" * 80,
            f"Session ID: {session_data.get('session_id', 'N/A')}",
            f"Timestamp: {session_data.get('timestamp', 'N/A')}",
            f"Mode: {session_data.get('mode', 'N/A')}",
            f"Module: {session_data.get('module_name', 'N/A')}",
            "",
            "-" * 80,
            "CLASSIFICATION RESULT",
            "-" * 80,
        ]
        
        if "classification" in session_data:
            cls = session_data["classification"]
            lines.extend([
                f"Verdict: {cls.get('verdict', 'N/A')}",
                f"Confidence: {cls.get('confidence', 'N/A')}",
                "",
                "Evidence:",
            ])
            for evidence in cls.get('evidence', []):
                lines.append(f"  - {evidence}")
            lines.extend([
                "",
                "Reasoning:",
                cls.get('reasoning', 'N/A'),
            ])
        
        if "prompt" in session_data:
            lines.extend([
                "",
                "-" * 80,
                "PROMPT SENT TO BOB",
                "-" * 80,
                session_data["prompt"],
            ])
        
        if "raw_response" in session_data:
            lines.extend([
                "",
                "-" * 80,
                "RAW BOB RESPONSE",
                "-" * 80,
                json.dumps(session_data["raw_response"], indent=2),
            ])
        
        lines.extend([
            "",
            "=" * 80,
            "END OF SESSION LOG",
            "=" * 80,
        ])
        
        return "\n".join(lines)
    
    def _format_classification_md(self, classification: Dict[str, Any]) -> str:
        """Format classification as markdown."""
        md_lines = [
            f"# Classification: {classification.get('module_name', 'Unknown')}",
            "",
            f"**Verdict:** {classification.get('verdict', 'N/A')}  ",
            f"**Confidence:** {classification.get('confidence', 'N/A')}  ",
            f"**Timestamp:** {classification.get('timestamp', 'N/A')}",
            "",
            "## Evidence",
            "",
        ]
        
        for evidence in classification.get('evidence', []):
            md_lines.append(f"- {evidence}")
        
        md_lines.extend([
            "",
            "## Reasoning",
            "",
            classification.get('reasoning', 'N/A'),
            "",
        ])
        
        if classification.get('artifact_path'):
            md_lines.extend([
                "## Generated Artifact",
                "",
                f"Path: `{classification['artifact_path']}`",
                "",
            ])
        
        return "\n".join(md_lines)
    
    def create_evidence_summary(self) -> str:
        """
        Generate markdown summary of all evidence.
        
        Returns:
            Path to the summary file
        """
        summary_path = self.evidence_dir / "EVIDENCE_SUMMARY.md"
        
        # Collect all evidence directories
        evidence_dirs = [d for d in self.evidence_dir.iterdir() if d.is_dir()]
        
        md_lines = [
            "# Necro Evidence Summary",
            "",
            f"Generated: {datetime.now().isoformat()}",
            f"Total Modules Analyzed: {len(evidence_dirs)}",
            "",
            "## Module Evidence",
            "",
        ]
        
        for evidence_dir in sorted(evidence_dirs):
            module_name = evidence_dir.name
            session_json = evidence_dir / "session.json"
            
            if session_json.exists():
                with open(session_json) as f:
                    session_data = json.load(f)
                
                classification = session_data.get("classification", {})
                
                md_lines.extend([
                    f"### {module_name}",
                    "",
                    f"- **Verdict:** {classification.get('verdict', 'N/A')}",
                    f"- **Confidence:** {classification.get('confidence', 'N/A')}",
                    f"- **Evidence Directory:** `{evidence_dir.relative_to(config.PROJECT_ROOT)}`",
                    "",
                ])
        
        md_lines.extend([
            "## Files Included",
            "",
            "For each module, the evidence directory contains:",
            "- `session.json` - Structured session data",
            "- `session.txt` - Human-readable log",
            "- `classification.md` - Classification details in markdown",
            "",
        ])
        
        with open(summary_path, 'w') as f:
            f.write("\n".join(md_lines))
        
        return str(summary_path)

# Made with Bob
