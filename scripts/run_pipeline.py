#!/usr/bin/env python3
"""
Main execution script for Necro pipeline.
Runs full classification and artifact generation.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from necro.config import config
from necro.bob_wrapper import BobWrapper
from necro.classifier import ModuleClassifier
from necro.artifact_generator import ArtifactGenerator
from necro.evidence_logger import EvidenceLogger


def main():
    """Main pipeline execution."""
    print("""
    ================================================================
    
       NECRO - AI-Powered Code Archaeologist
    
       Analyzing legacy code with IBM Bob 2.0
    
    ================================================================
    """)
    
    # Ensure directories exist
    print("Setting up directories...")
    config.ensure_directories()
    
    # Initialize components
    print("Initializing components...")
    bob_wrapper = BobWrapper()
    evidence_logger = EvidenceLogger()
    classifier = ModuleClassifier(bob_wrapper, evidence_logger)
    artifact_generator = ArtifactGenerator(bob_wrapper)
    
    print(f"Target modules: {len(config.TARGET_MODULES)}")
    
    # Run classification pipeline
    print("\n" + "="*80)
    print("PHASE 1: CLASSIFICATION")
    print("="*80)
    
    results = classifier.classify_all(config.TARGET_MODULES)
    
    # Generate artifacts
    print("\n" + "="*80)
    print("PHASE 2: ARTIFACT GENERATION")
    print("="*80)
    
    for result in results:
        if result.verdict != "Normal" and result.verdict != "Error":
            artifact_path = artifact_generator.generate_for_verdict(result)
            result.artifact_path = artifact_path
    
    # Save results
    print("\n" + "="*80)
    print("PHASE 3: SAVING RESULTS")
    print("="*80)
    
    results_data = {
        "generated_at": datetime.now().isoformat(),
        "demo_repo": str(config.DEMO_REPO_PATH.relative_to(config.PROJECT_ROOT)),
        "modules_analyzed": len(results),
        "bob_mode": "chat",
        "results": [
            {
                "module_name": r.module_name,
                "module_path": r.module_path,
                "verdict": r.verdict,
                "confidence": r.confidence,
                "evidence": r.evidence,
                "reasoning": r.reasoning,
                "artifact_path": r.artifact_path,
                "evidence_path": r.evidence_path,
                "timestamp": r.timestamp
            }
            for r in results
        ]
    }
    
    results_path = config.RESULTS_DIR / "results.json"
    with open(results_path, 'w') as f:
        json.dump(results_data, f, indent=2)
    
    print(f"[OK] Results saved to: {results_path.relative_to(config.PROJECT_ROOT)}")
    
    # Generate evidence summary
    print("\n" + "="*80)
    print("PHASE 4: EVIDENCE SUMMARY")
    print("="*80)
    
    summary_path = evidence_logger.create_evidence_summary()
    print(f"[OK] Evidence summary: {summary_path}")
    
    # Print summary
    print("\n" + "="*80)
    print("PIPELINE COMPLETE - SUMMARY")
    print("="*80)
    
    verdict_counts = {}
    for result in results:
        verdict_counts[result.verdict] = verdict_counts.get(result.verdict, 0) + 1
    
    print(f"\nTotal modules analyzed: {len(results)}")
    print("\nVerdict breakdown:")
    for verdict, count in sorted(verdict_counts.items()):
        print(f"  {verdict}: {count}")
    
    artifacts_generated = sum(1 for r in results if r.artifact_path)
    print(f"\nArtifacts generated: {artifacts_generated}")
    
    print(f"\nResults location: {results_path.relative_to(config.PROJECT_ROOT)}")
    print(f"Evidence location: {config.EVIDENCE_DIR.relative_to(config.PROJECT_ROOT)}")
    print(f"Artifacts location: {config.ARTIFACTS_DIR.relative_to(config.PROJECT_ROOT)}")
    
    print("\n" + "="*80)
    print("Next step: Run 'python scripts/serve_dashboard.py' to view results")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPipeline interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Made with Bob
