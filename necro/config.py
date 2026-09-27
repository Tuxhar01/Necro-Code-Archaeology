"""
Configuration management for Necro.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration settings for Necro."""
    
    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DEMO_REPO_PATH = PROJECT_ROOT / "demo_repo"
    RESULTS_DIR = PROJECT_ROOT / "results"
    EVIDENCE_DIR = RESULTS_DIR / "evidence"
    ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
    PROMPTS_DIR = PROJECT_ROOT / "prompts"
    
    # Bob 2.0 settings
    BOB_API_KEY = os.getenv("BOB_API_KEY", "")
    BOB_API_ENDPOINT = os.getenv("BOB_API_ENDPOINT", "https://bob.ibm.com/api/v2")
    BOB_MODE = os.getenv("BOB_MODE", "api")  # api, cli, or mock
    BOB_TIMEOUT = int(os.getenv("BOB_TIMEOUT", "60"))
    BOB_MAX_RETRIES = int(os.getenv("BOB_MAX_RETRIES", "3"))
    
    # Logging
    DEBUG = os.getenv("NECRO_DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Modules to analyze (hardcoded for MVP)
    TARGET_MODULES = [
        {
            "name": "calculate_legacy_metrics",
            "path": "demo_repo/src/legacy_feature.py",
            "function": "calculate_legacy_metrics",
            "expected_verdict": "Safe to Delete"
        },
        {
            "name": "format_old_date",
            "path": "demo_repo/src/utils.py",
            "function": "format_old_date",
            "expected_verdict": "Safe to Delete"
        },
        {
            "name": "track_user_event",
            "path": "demo_repo/src/analytics.py",
            "function": "track_user_event",
            "expected_verdict": "Secretly Load-Bearing"
        },
        {
            "name": "validate_input",
            "path": "demo_repo/src/utils.py",
            "function": "validate_input",
            "expected_verdict": "Undocumented but Valuable"
        },
        {
            "name": "process_request",
            "path": "demo_repo/src/main.py",
            "function": "process_request",
            "expected_verdict": "Normal"
        }
    ]
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist."""
        cls.RESULTS_DIR.mkdir(exist_ok=True)
        cls.EVIDENCE_DIR.mkdir(exist_ok=True)
        cls.ARTIFACTS_DIR.mkdir(exist_ok=True)
        (cls.ARTIFACTS_DIR / "deletions").mkdir(exist_ok=True)
        (cls.ARTIFACTS_DIR / "documentation").mkdir(exist_ok=True)
        (cls.ARTIFACTS_DIR / "adrs").mkdir(exist_ok=True)
        cls.PROMPTS_DIR.mkdir(exist_ok=True)


# Create singleton instance
config = Config()

# Made with Bob
