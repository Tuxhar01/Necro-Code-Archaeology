# Necro Implementation Plan
## AI-Powered Code Archaeologist - Detailed Build Strategy

**Status:** Ready for Implementation  
**Backend:** Python 3.10+  
**Timeline:** 48-hour hackathon build  
**Last Updated:** 2026-09-26

---

## Executive Summary

Necro uses IBM Bob 2.0's full-repository reasoning to classify legacy code modules as:
- **Safe to Delete** (with deletion PR)
- **Secretly Load-Bearing** (with documentation explaining why)
- **Undocumented but Valuable** (with auto-generated docs)
- **Normal / No Action** (control case)

This plan provides a step-by-step implementation strategy optimized for a 48-hour build cycle.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     NECRO SYSTEM                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐      ┌─────────────────┐                │
│  │  Demo Repo   │─────▶│  Necro Backend  │                │
│  │  (5 seeded   │      │  (Python)       │                │
│  │   modules)   │      └────────┬────────┘                │
│  └──────────────┘               │                          │
│                                  │                          │
│                                  ▼                          │
│                      ┌──────────────────────┐              │
│                      │  Bob 2.0 Integration │              │
│                      │  Wrapper Module      │              │
│                      └──────────┬───────────┘              │
│                                  │                          │
│                                  ▼                          │
│                      ┌──────────────────────┐              │
│                      │  Classification      │              │
│                      │  Pipeline            │              │
│                      └──────────┬───────────┘              │
│                                  │                          │
│                                  ▼                          │
│                      ┌──────────────────────┐              │
│                      │  Artifact Generator  │              │
│                      └──────────┬───────────┘              │
│                                  │                          │
│                                  ▼                          │
│                      ┌──────────────────────┐              │
│                      │  results.json        │              │
│                      │  + evidence/         │              │
│                      └──────────┬───────────┘              │
│                                  │                          │
│                                  ▼                          │
│                      ┌──────────────────────┐              │
│                      │  Web Dashboard       │              │
│                      │  (HTML/JS)           │              │
│                      └──────────────────────┘              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
necro_bob/
├── README.md                      # Project overview and setup
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore rules
├── .env.example                   # Environment variables template
│
├── demo_repo/                     # Seeded test repository
│   ├── README.md                  # Demo repo documentation
│   ├── src/
│   │   ├── main.py               # Entry point
│   │   ├── utils.py              # Utility functions
│   │   ├── router.py             # String-based routing (for fake-dead case)
│   │   ├── legacy_feature.py    # Dead code from removed feature
│   │   └── analytics.py         # Undocumented but used
│   └── config/
│       └── routes.json           # Config-driven dispatch table
│
├── necro/                         # Main application package
│   ├── __init__.py
│   ├── bob_wrapper.py            # Bob 2.0 integration wrapper
│   ├── classifier.py             # Classification pipeline
│   ├── artifact_generator.py    # Artifact generation logic
│   ├── evidence_logger.py       # Session logging and evidence capture
│   └── config.py                # Configuration management
│
├── prompts/                       # Bob prompt templates
│   ├── classify_module.txt       # Classification prompt
│   ├── generate_deletion.txt    # Deletion artifact prompt
│   ├── generate_docs.txt        # Documentation prompt
│   └── generate_adr.txt         # ADR snippet prompt
│
├── results/                       # Output directory
│   ├── results.json              # Structured results
│   └── evidence/                 # Bob session logs
│       ├── module1/
│       │   ├── session.json
│       │   └── screenshot.png
│       └── ...
│
├── artifacts/                     # Generated artifacts
│   ├── deletions/
│   ├── documentation/
│   └── adrs/
│
├── dashboard/                     # Web interface
│   ├── index.html                # Main dashboard page
│   ├── styles.css                # Minimal styling
│   └── app.js                    # Frontend logic
│
└── scripts/                       # Utility scripts
    ├── run_pipeline.py           # Main execution script
    ├── seed_demo_repo.py         # Demo repo setup
    └── serve_dashboard.py        # Simple HTTP server
```

---

## Implementation Phases

### Phase 1: Foundation Setup (2-3 hours)

#### 1.1 Project Initialization
- Create project structure
- Set up Python virtual environment
- Install dependencies: `requests`, `python-dotenv`, `jinja2`
- Create `.gitignore` and `.env.example`

#### 1.2 Demo Repository Seeding
Create 5 carefully crafted test cases:

**Case 1: Genuinely Dead Function #1**
```python
# demo_repo/src/legacy_feature.py
def calculate_legacy_metrics(data):
    """Old metrics calculation - replaced by new system."""
    # No references anywhere in codebase
    return sum(data) / len(data)
```

**Case 2: Genuinely Dead Function #2**
```python
# demo_repo/src/utils.py
def format_old_date(timestamp):
    """Date formatter from v1.0 - no longer used."""
    # Different pattern: leftover from removed feature
    return timestamp.strftime("%d/%m/%Y")
```

**Case 3: Fake-Dead / Secretly Load-Bearing**
```python
# demo_repo/src/analytics.py
def track_user_event(event_type, user_id):
    """Called via string-based dispatch - static analysis misses it."""
    print(f"Event: {event_type} for user {user_id}")

# demo_repo/src/router.py
# String-based dispatch table
HANDLERS = {
    "user_event": "analytics.track_user_event",
    # ...
}

# demo_repo/config/routes.json
{
    "event_handlers": {
        "user_action": "analytics.track_user_event"
    }
}
```

**Case 4: Undocumented but Clearly Used**
```python
# demo_repo/src/utils.py
def validate_input(data):
    # No docstring, no comments, but called in main.py
    if not data or len(data) == 0:
        return False
    return True
```

**Case 5: Control Case (Normal)**
```python
# demo_repo/src/main.py
def process_request(request):
    """Main request processor - well documented and clearly used."""
    validated = validate_input(request.data)
    if validated:
        return handle_request(request)
    return error_response()
```

---

### Phase 2: Bob 2.0 Integration (3-4 hours)

#### 2.1 Bob Wrapper Module (`necro/bob_wrapper.py`)

```python
class BobWrapper:
    """Flexible wrapper for Bob 2.0 API/CLI integration."""
    
    def __init__(self, config):
        self.config = config
        self.session_logs = []
    
    def analyze_module(self, module_path, repo_context):
        """
        Send module to Bob for classification.
        Returns: {verdict, confidence, evidence, reasoning}
        """
        pass
    
    def generate_artifact(self, module_info, artifact_type):
        """
        Ask Bob to generate specific artifact.
        Returns: generated content
        """
        pass
    
    def capture_session(self):
        """Save session summary for evidence."""
        pass
```

**Key Design Decisions:**
- Abstract Bob's interface behind clean methods
- Support both API and CLI modes (configurable)
- Automatic session logging for every call
- Structured output parsing with fallback handling

#### 2.2 Prompt Engineering

**Classification Prompt Template:**
```
You are analyzing a code module in a legacy codebase to determine if it's safe to delete, secretly critical, or just undocumented.

Repository Context:
{repo_structure}

Target Module:
File: {module_path}
Code:
{module_code}

Analyze this module and provide:
1. VERDICT: One of [Safe to Delete, Secretly Load-Bearing, Undocumented but Valuable, Normal]
2. CONFIDENCE: [High, Medium, Low]
3. EVIDENCE: Specific references, call sites, or patterns that support your verdict
4. REASONING: Step-by-step explanation of your analysis

Consider:
- Direct function calls
- String-based dispatch (config files, routing tables)
- Reflection or dynamic imports
- Cross-file dependencies
- Indirect usage patterns

Format your response as JSON:
{
    "verdict": "...",
    "confidence": "...",
    "evidence": ["...", "..."],
    "reasoning": "..."
}
```

---

### Phase 3: Classification Pipeline (4-5 hours)

#### 3.1 Classifier Module (`necro/classifier.py`)

```python
class ModuleClassifier:
    """Orchestrates the classification of suspect modules."""
    
    def __init__(self, bob_wrapper, evidence_logger):
        self.bob = bob_wrapper
        self.logger = evidence_logger
    
    def classify_module(self, module_path):
        """
        Full classification workflow for one module.
        Returns: ClassificationResult object
        """
        # 1. Load module code
        # 2. Gather repo context
        # 3. Call Bob for analysis
        # 4. Parse and validate response
        # 5. Log evidence
        # 6. Return structured result
        pass
    
    def classify_all(self, module_list):
        """Process all modules in sequence."""
        results = []
        for module in module_list:
            result = self.classify_module(module)
            results.append(result)
        return results
```

#### 3.2 Evidence Logger (`necro/evidence_logger.py`)

```python
class EvidenceLogger:
    """Captures and stores Bob session evidence."""
    
    def log_session(self, module_name, session_data):
        """
        Save session data to evidence/{module_name}/
        - session.json: structured data
        - session.txt: human-readable log
        - screenshot.png: (if available from Bob)
        """
        pass
    
    def create_evidence_summary(self):
        """Generate markdown summary of all evidence."""
        pass
```

---

### Phase 4: Artifact Generation (3-4 hours)

#### 4.1 Artifact Generator (`necro/artifact_generator.py`)

```python
class ArtifactGenerator:
    """Generates appropriate artifacts based on verdict."""
    
    def __init__(self, bob_wrapper):
        self.bob = bob_wrapper
    
    def generate_for_verdict(self, classification_result):
        """Route to appropriate generator based on verdict."""
        verdict = classification_result.verdict
        
        if verdict == "Safe to Delete":
            return self.generate_deletion_artifact(classification_result)
        elif verdict == "Secretly Load-Bearing":
            return self.generate_adr_artifact(classification_result)
        elif verdict == "Undocumented but Valuable":
            return self.generate_documentation(classification_result)
        else:
            return None  # No artifact for Normal
    
    def generate_deletion_artifact(self, result):
        """
        Create:
        - deletion.patch: git diff format
        - safety_note.md: regression safety explanation
        """
        pass
    
    def generate_adr_artifact(self, result):
        """
        Create:
        - adr_snippet.md: why this code is load-bearing
        - docstring_addition.py: enhanced docstring
        """
        pass
    
    def generate_documentation(self, result):
        """
        Create:
        - module_docs.md: comprehensive documentation
        """
        pass
```

**Artifact Prompt Templates:**

**Deletion Prompt:**
```
Generate a safe deletion patch for this module that was classified as safe to delete.

Module: {module_path}
Evidence: {evidence}

Provide:
1. A git diff format patch for deletion
2. A safety note explaining why this deletion is safe
3. Any regression testing recommendations

Format as JSON:
{
    "patch": "...",
    "safety_note": "...",
    "test_recommendations": ["..."]
}
```

---

### Phase 5: Results Management (1-2 hours)

#### 5.1 Results Schema

```json
{
    "generated_at": "2026-09-26T18:00:00Z",
    "demo_repo": "demo_repo/",
    "modules_analyzed": 5,
    "results": [
        {
            "module_name": "legacy_feature.calculate_legacy_metrics",
            "module_path": "demo_repo/src/legacy_feature.py",
            "verdict": "Safe to Delete",
            "confidence": "High",
            "evidence": [
                "No direct references found in codebase",
                "Not imported in any file",
                "No string-based references in config files"
            ],
            "reasoning": "Comprehensive scan shows no usage...",
            "artifact_path": "artifacts/deletions/legacy_feature_deletion.patch",
            "evidence_path": "results/evidence/legacy_feature/",
            "timestamp": "2026-09-26T18:05:00Z"
        }
    ]
}
```

---

### Phase 6: Web Dashboard (3-4 hours)

#### 6.1 Dashboard Design (Minimal but Clear)

**Features:**
- Single-page table view of all results
- Expandable rows for evidence details
- Download links for generated artifacts
- Color-coded verdicts (red=delete, yellow=document, green=normal)
- No authentication, no routing complexity

**Tech Stack:**
- Plain HTML5 + CSS3
- Vanilla JavaScript (no framework needed)
- Simple Python HTTP server for local serving

#### 6.2 Dashboard Layout

```html
<!DOCTYPE html>
<html>
<head>
    <title>Necro - Code Archaeology Results</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <h1>🏺 Necro - Code Archaeology Results</h1>
        <p>AI-Powered Legacy Code Analysis</p>
    </header>
    
    <main>
        <div class="summary">
            <div class="stat">
                <span class="label">Modules Analyzed:</span>
                <span class="value" id="total-modules">5</span>
            </div>
            <div class="stat">
                <span class="label">Safe to Delete:</span>
                <span class="value delete" id="delete-count">2</span>
            </div>
            <div class="stat">
                <span class="label">Load-Bearing:</span>
                <span class="value warning" id="warning-count">1</span>
            </div>
            <div class="stat">
                <span class="label">Needs Docs:</span>
                <span class="value info" id="docs-count">1</span>
            </div>
        </div>
        
        <table id="results-table">
            <thead>
                <tr>
                    <th>Module</th>
                    <th>Verdict</th>
                    <th>Confidence</th>
                    <th>Evidence</th>
                    <th>Artifact</th>
                </tr>
            </thead>
            <tbody id="results-body">
                <!-- Populated by JavaScript -->
            </tbody>
        </table>
    </main>
    
    <script src="app.js"></script>
</body>
</html>
```

---

### Phase 7: Integration & Testing (4-5 hours)

#### 7.1 Main Pipeline Script (`scripts/run_pipeline.py`)

```python
#!/usr/bin/env python3
"""
Main execution script for Necro pipeline.
Runs full classification and artifact generation.
"""

def main():
    # 1. Load configuration
    # 2. Initialize Bob wrapper
    # 3. Load demo repo and suspect modules
    # 4. Run classification pipeline
    # 5. Generate artifacts
    # 6. Save results.json
    # 7. Generate evidence summary
    # 8. Print summary report
    pass

if __name__ == "__main__":
    main()
```

#### 7.2 Testing Strategy

**Unit Tests (if time permits):**
- Bob wrapper response parsing
- Artifact generation formatting
- Evidence logging file creation

**Integration Tests (priority):**
- End-to-end pipeline for each of 5 modules
- Verify all verdicts are reasonable
- Confirm artifacts are generated correctly
- Check evidence is captured

**Manual Testing Checklist:**
- [ ] All 5 modules classified with different verdicts
- [ ] At least 2 artifact types generated
- [ ] Dashboard displays all results correctly
- [ ] Evidence folder contains session logs
- [ ] Artifacts are downloadable and valid

---

## Critical Path Items

### Must-Have for Demo
1. ✅ Demo repo with 5 distinct seeded cases
2. ✅ Bob integration working for classification
3. ✅ At least 2 artifact types generated (deletion + docs)
4. ✅ Dashboard showing all results
5. ✅ Evidence logs saved for submission

### Nice-to-Have (if time)
- Prettier dashboard styling
- More sophisticated artifact formatting
- Additional test cases
- Better error handling and logging

### Explicitly Out of Scope
- Real GitHub OAuth/PR automation
- Custom call-graph algorithms
- Multi-repo support
- User authentication
- CI/CD integration

---

## Risk Mitigation Strategies

### Risk 1: Bob API Interface Unknown
**Mitigation:** Build flexible wrapper with multiple backend options (API, CLI, mock)

### Risk 2: Prompt Engineering Takes Too Long
**Mitigation:** Test prompts early with simple cases; lock down templates by end of Phase 2

### Risk 3: Demo Cases Too Obvious/Subtle
**Mitigation:** Test seeded repo against simple grep/search first; adjust complexity

### Risk 4: Time Pressure for Polish
**Mitigation:** Prioritize functionality over aesthetics; ugly-but-working beats pretty-but-broken

---

## Submission Deliverables Checklist

### Code & Artifacts
- [ ] Complete source code in GitHub repo
- [ ] Demo repo with 5 seeded modules (before state)
- [ ] Generated artifacts (diffs, docs, ADRs) as files
- [ ] `results.json` with all classification results

### Evidence & Documentation
- [ ] Screenshots of Bob session summaries (one per module)
- [ ] Evidence folder with session logs
- [ ] README with setup and run instructions
- [ ] Architecture diagram (Mermaid or image)

### Demo Materials
- [ ] Working dashboard (live or recorded)
- [ ] Demo video (2-3 minutes)
- [ ] Presentation slides covering:
  - Problem statement
  - Solution overview
  - Bob 2.0's role (emphasized)
  - Business value (dev time saved, risk avoided)
  - Live demo walkthrough
  - Roadmap (future features)

### Business Value Write-up
- [ ] Short document connecting each verdict to:
  - Developer time saved
  - Risk avoided
  - Concrete business impact

---

## Timeline Breakdown (48 Hours)

### Friday Evening (4 hours)
- [x] PRD analysis and planning
- [ ] Project structure setup
- [ ] Demo repo seeding
- [ ] Bob wrapper skeleton
- [ ] Smoke test: classify one module end-to-end

### Saturday (12 hours)
**Morning (6 hours):**
- [ ] Complete Bob integration
- [ ] Build classification pipeline
- [ ] Test all 5 modules classification

**Afternoon (6 hours):**
- [ ] Implement artifact generation
- [ ] Build dashboard frontend
- [ ] Integration testing

### Sunday (8 hours)
**Morning (4 hours):**
- [ ] Polish artifacts and dashboard
- [ ] Generate all evidence documentation
- [ ] Create screenshots and logs

**Afternoon (4 hours):**
- [ ] Record demo video
- [ ] Build presentation slides
- [ ] Final testing and submission prep
- [ ] Submit with buffer before deadline

---

## Success Metrics

### Technical Depth (Bob 2.0 Usage)
- ✅ Every verdict backed by Bob session with cited evidence
- ✅ Multiple prompt types (classification + artifact generation)
- ✅ Full-repo context utilized in reasoning

### Presentation Quality
- ✅ Clean, functional dashboard
- ✅ Clear demo flow (problem → verdict → artifact)
- ✅ Professional slides and video

### Business Value
- ✅ Compelling dev-time/risk narrative
- ✅ Real-world pain point addressed
- ✅ Quantifiable impact story

### Originality
- ✅ "Code archaeology" framing (not another RAG bot)
- ✅ Novel use of Bob for legacy code analysis
- ✅ Practical, immediately useful tool

---

## Next Steps

1. **Immediate:** Set up project structure and Python environment
2. **Critical:** Seed demo repository with all 5 test cases
3. **Priority:** Build and test Bob wrapper with one module
4. **Then:** Follow phase-by-phase implementation plan

---

## Notes & Decisions Log

- **2026-09-26:** Python backend chosen over Node.js for faster prototyping
- **2026-09-26:** Bob 2.0 access confirmed available
- **2026-09-26:** Starting build immediately (not waiting for Friday kickoff)
- **2026-09-26:** Flexible Bob wrapper design to handle API variations

---

## Questions for Clarification

1. Bob 2.0 API specifics: REST API, CLI tool, or IDE integration?
2. Session logging format: JSON, screenshots, or both?
3. Artifact format preferences: Markdown, patches, or mixed?

---

*This plan is a living document. Update as implementation progresses and new information becomes available.*