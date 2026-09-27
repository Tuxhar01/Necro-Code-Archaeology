# Necro Quick Start Guide
## Get Up and Running in 5 Minutes

---

## Prerequisites

- Python 3.10 or higher
- IBM Bob 2.0 API access
- Git
- Modern web browser

---

## Installation

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd necro_bob

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Bob 2.0 Access

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your Bob API credentials
# BOB_API_KEY=your_api_key_here
# BOB_API_ENDPOINT=https://bob.ibm.com/api/v2
```

---

## Running Necro

### Step 1: Seed the Demo Repository

```bash
python scripts/seed_demo_repo.py
```

This creates a demo repository with 5 carefully crafted test cases:
- 2 genuinely dead functions
- 1 secretly load-bearing function (string-based dispatch)
- 1 undocumented but used function
- 1 normal control case

### Step 2: Run the Classification Pipeline

```bash
python scripts/run_pipeline.py
```

This will:
1. Analyze each module using Bob 2.0
2. Generate classification verdicts with evidence
3. Create appropriate artifacts (patches, docs, ADRs)
4. Save results to `results/results.json`
5. Log evidence to `results/evidence/`

**Expected runtime:** 2-5 minutes for all 5 modules

### Step 3: View Results in Dashboard

```bash
python scripts/serve_dashboard.py
```

Opens the dashboard at `http://localhost:8000`

The dashboard shows:
- Summary statistics
- Interactive results table
- Expandable evidence details
- Downloadable artifacts

---

## Project Structure Overview

```
necro_bob/
├── demo_repo/              # Seeded test repository
├── necro/                  # Core application code
│   ├── bob_wrapper.py     # Bob 2.0 integration
│   ├── classifier.py      # Classification pipeline
│   ├── artifact_generator.py
│   └── evidence_logger.py
├── prompts/               # Bob prompt templates
├── results/               # Output directory
│   ├── results.json      # Structured results
│   └── evidence/         # Bob session logs
├── artifacts/            # Generated artifacts
├── dashboard/            # Web interface
└── scripts/              # Utility scripts
```

---

## Understanding the Results

### Verdict Types

| Verdict | Meaning | Artifact Generated |
|---------|---------|-------------------|
| **Safe to Delete** | No references found, safe to remove | Deletion patch + safety note |
| **Secretly Load-Bearing** | Used indirectly (config, reflection) | ADR + enhanced docstring |
| **Undocumented but Valuable** | Used but lacks documentation | Comprehensive docs |
| **Normal** | Well-documented, clearly used | None (control case) |

### Confidence Levels

- **High:** Strong evidence, clear verdict
- **Medium:** Some ambiguity, manual review recommended
- **Low:** Uncertain, requires human judgment

---

## Example Output

### Classification Result

```json
{
    "module_name": "legacy_feature.calculate_legacy_metrics",
    "verdict": "Safe to Delete",
    "confidence": "High",
    "evidence": [
        "No direct references in codebase",
        "Not imported in any file",
        "No string-based references in config"
    ],
    "reasoning": "Comprehensive scan shows no usage...",
    "artifact_path": "artifacts/deletions/legacy_feature_deletion.patch"
}
```

### Generated Artifact (Deletion Patch)

```diff
--- a/demo_repo/src/legacy_feature.py
+++ b/demo_repo/src/legacy_feature.py
@@ -1,5 +0,0 @@
-def calculate_legacy_metrics(data):
-    """Old metrics calculation - replaced by new system."""
-    return sum(data) / len(data)
```

---

## Troubleshooting

### Bob API Connection Issues

**Problem:** `ConnectionError: Unable to reach Bob API`

**Solution:**
1. Check your `.env` file has correct credentials
2. Verify Bob API endpoint is accessible
3. Check network/firewall settings

### Module Classification Fails

**Problem:** `ClassificationError: Unable to parse Bob response`

**Solution:**
1. Check Bob API is returning valid JSON
2. Review prompt templates in `prompts/`
3. Enable debug logging: `export NECRO_DEBUG=1`

### Dashboard Not Loading

**Problem:** Dashboard shows blank page

**Solution:**
1. Ensure `results/results.json` exists
2. Check browser console for errors
3. Verify `serve_dashboard.py` is running
4. Try clearing browser cache

---

## Development Workflow

### Adding a New Module to Analyze

1. Add module path to `demo_repo/modules_to_analyze.txt`
2. Run pipeline: `python scripts/run_pipeline.py`
3. View results in dashboard

### Testing Prompt Changes

1. Edit prompt template in `prompts/`
2. Run single module test:
   ```bash
   python -c "from necro.classifier import ModuleClassifier; \
              c = ModuleClassifier(); \
              c.classify_module('demo_repo/src/utils.py')"
   ```
3. Review output and iterate

### Regenerating Artifacts

```bash
# Regenerate all artifacts
python scripts/run_pipeline.py --regenerate-artifacts

# Regenerate specific module
python scripts/run_pipeline.py --module legacy_feature.py
```

---

## Demo Preparation Checklist

### Before Demo
- [ ] Run full pipeline successfully
- [ ] Verify all 5 modules classified
- [ ] Check artifacts generated correctly
- [ ] Test dashboard in clean browser
- [ ] Prepare talking points for each verdict

### During Demo
1. Show demo repo (before state)
2. Run pipeline (or show pre-recorded)
3. Walk through dashboard results
4. Highlight Bob's reasoning for each case
5. Show generated artifacts
6. Emphasize business value (time saved, risk avoided)

### Demo Script (2-3 minutes)

**[0:00-0:30]** Problem Setup
- "Every codebase has untouchable code"
- Show demo repo with mysterious functions
- "Which is safe to delete? Which will break production?"

**[0:30-1:30]** Solution Demo
- Run Necro pipeline
- Show Bob analyzing each module
- Display dashboard with verdicts

**[1:30-2:30]** Evidence & Artifacts
- Expand evidence for "secretly load-bearing" case
- Show string-based dispatch Bob caught
- Display generated deletion patch
- Show auto-generated documentation

**[2:30-3:00]** Business Value
- "Saves hours of manual code archaeology"
- "Prevents production breakage"
- "Enables confident legacy code cleanup"

---

## Advanced Usage

### Custom Prompts

Create custom prompt templates in `prompts/custom/`:

```python
# In necro/config.py
CUSTOM_PROMPTS = {
    "classify_module": "prompts/custom/my_classifier.txt"
}
```

### Mock Mode (Testing Without Bob)

```bash
# Use mock responses for testing
export BOB_MODE=mock
python scripts/run_pipeline.py
```

### Batch Processing

```bash
# Analyze multiple repos
for repo in repo1 repo2 repo3; do
    python scripts/run_pipeline.py --repo $repo
done
```

---

## Performance Tips

### Speed Up Analysis
- Use Bob API caching if available
- Process modules in parallel (future enhancement)
- Reduce context size for large repos

### Reduce Costs
- Use mock mode for development
- Cache Bob responses locally
- Optimize prompt length

---

## Next Steps After MVP

### Immediate Improvements
1. Add unit tests for core modules
2. Improve error handling and logging
3. Add progress indicators to pipeline
4. Enhance dashboard styling

### Future Features
1. Real GitHub PR automation
2. CI/CD integration
3. Multi-repo support
4. Historical tracking
5. Custom rule definitions

---

## Getting Help

### Documentation
- [Implementation Plan](IMPLEMENTATION_PLAN.md) - Detailed build strategy
- [Architecture](ARCHITECTURE.md) - System design and data flow
- [PRD](PRD.md) - Product requirements

### Common Issues
- Check `logs/necro.log` for detailed error messages
- Review Bob session logs in `results/evidence/`
- Enable debug mode: `export NECRO_DEBUG=1`

### Support
- GitHub Issues: <your-repo-url>/issues
- Hackathon Slack: #necro-support

---

## Success Metrics

Your Necro installation is working correctly if:
- ✅ All 5 demo modules are classified
- ✅ At least 2 different artifact types generated
- ✅ Dashboard displays all results
- ✅ Evidence logs contain Bob session data
- ✅ No errors in pipeline execution

---

*Ready to start? Run `python scripts/seed_demo_repo.py` and begin your code archaeology journey!*