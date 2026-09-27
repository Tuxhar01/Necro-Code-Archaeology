# 🏺 Necro — AI-Powered Code Archaeologist

> **Find dead code. Detect hidden dependencies. Preserve what matters.**

Necro is a code-archaeology tool for understanding legacy codebases before someone deletes the wrong thing.

It analyzes suspicious or forgotten functions and classifies them into actionable categories:

- 🗑️ **Safe to Delete**
- ⚠️ **Secretly Load-Bearing**
- 📚 **Undocumented but Valuable**
- ✓ **Normal — No Action**

The project demonstrates how **IBM Bob 2.0's repository-level reasoning** can be applied to a practical software-engineering problem: determining whether seemingly unused legacy code is actually safe to remove.

---

## 🚀 Live Demo

**Dashboard:**  
https://necro-code-archaeology.onrender.com

**Source Code:**  
https://github.com/Tuxhar01/Necro-Code-Archaeology

The live application provides two analysis modes:

### ✓ Bob 2.0 Verified Demo

A controlled five-module repository whose classifications and evidence were produced through the project's Bob 2.0 analysis workflow.

### ⚠ Static Repository Inspection

Upload your own repository as a ZIP and inspect it using Necro's local static-analysis pipeline.

> **Important:** Uploaded repositories are currently analyzed using static inspection. They are **not analyzed by IBM Bob 2.0** and are explicitly labeled as such in the dashboard.

---

# 🎯 The Problem

Legacy codebases accumulate functions and modules that nobody wants to touch.

They may be:

- undocumented
- poorly tested
- written years ago
- disconnected from the current architecture
- apparently unused
- referenced only through configuration or dynamic dispatch

This creates two opposing risks.

### 1. Fear-driven technical debt

Teams keep obsolete code because nobody can confidently prove that it is safe to remove.

### 2. Accidental breakage

A developer sees apparently unused code, deletes it, and discovers later that production depended on it through an indirect execution path.

Traditional text search can miss patterns such as:

- configuration-driven handlers
- string-based dispatch
- dynamic imports
- reflection
- runtime references

Necro is designed around this problem.

---

# 💡 The Idea

Instead of asking:

> "Can I find an import for this function?"

Necro asks:

> **"What role does this code actually play in the repository?"**

For each suspicious module, Necro combines repository evidence and reasoning to produce:

1. a classification
2. supporting evidence
3. reasoning
4. confidence
5. an actionable artifact when available

The result is not simply a list of unused functions.

It is an **evidence-backed code archaeology report**.

---

# 🔍 Classification Model

| Verdict | Meaning |
|---|---|
| 🗑️ **Safe to Delete** | No meaningful references were found in the analyzed repository |
| ⚠️ **Secretly Load-Bearing** | The code appears unused directly but is connected through indirect/dynamic usage |
| 📚 **Undocumented but Valuable** | The code is actively used but lacks adequate documentation |
| ✓ **Normal — No Action** | The code is used and sufficiently documented |

The dashboard exposes the evidence behind each classification rather than presenting only a label.

---

# 🧠 IBM Bob 2.0

The original Necro demonstration uses **IBM Bob 2.0's repository-level reasoning workflow** to investigate the relationship between apparently isolated code and the rest of the repository.

This is particularly important for the **Secretly Load-Bearing** case.

For example, the demo contains a function that does not have obvious direct imports but is referenced through a routing/dispatch mechanism.

A simple search can make it look dead.

Repository-level reasoning can reveal the larger execution path.

---

# 🏺 The Verified Demo

Necro includes a deliberately constructed five-module repository designed to test different forms of legacy-code ambiguity.

| Case | Expected Verdict | Purpose |
|---|---|---|
| `calculate_legacy_metrics` | Safe to Delete | Genuinely unused code |
| `format_old_date` | Safe to Delete | Another dead legacy function |
| `track_user_event` | Secretly Load-Bearing | Indirect/string-based dispatch |
| `validate_input` | Undocumented but Valuable | Used but poorly documented |
| `process_request` | Normal — No Action | Control case |

### Demo summary

```text
Modules Analyzed: 5

Safe to Delete:             2
Secretly Load-Bearing:      1
Undocumented but Valuable:  1
Normal — No Action:         1

The control case is intentional: Necro should not simply label everything as suspicious.


---

🕵️ Example: The Fake-Dead Function

One of the most important demo cases is:

def track_user_event(event_type, user_id):
    print(f"Event: {event_type} for user {user_id}")

At first glance, the function appears unused.

Necro's evidence shows that it is connected through the repository's dispatch mechanism.

The dashboard exposes evidence such as:

Verdict:
Secretly Load-Bearing

Confidence:
High

Evidence:
• router.py maps a handler to analytics.track_user_event
• routes.json references the same handler
• runtime dispatch uses dynamic loading

This is the core problem Necro is designed to surface.


---

🛠️ Actionable Artifacts

For the verified Bob 2.0 demo, Necro can produce artifacts associated with the analysis, including:

deletion patches

architecture decision records

documentation artifacts


These are surfaced directly from the dashboard so the user can inspect the evidence and proposed action.

The project deliberately separates analysis from action:

Code
  ↓
Analysis
  ↓
Evidence
  ↓
Verdict
  ↓
Artifact


---

📊 Interactive Dashboard

The dashboard provides:

repository upload

verified demo mode

analysis summary

verdict filtering

module search

evidence inspection

source-code context

reasoning

artifact downloads

static-analysis disclosure for uploaded repositories


The interface separates two sources of analysis:

✓ Bob 2.0 Verified Demo

The controlled demonstration backed by the project's Bob 2.0 workflow.

⚠ Static Inspection

User-uploaded repositories analyzed using Necro's local static-analysis engine.

This distinction is intentionally visible so the application does not imply that arbitrary uploaded repositories were analyzed by Bob.


---

📦 Analyze Your Own Repository

Necro supports a repository-upload MVP.

Upload a repository as a .zip file and the application performs static inspection without executing the uploaded code.

The upload pipeline includes protections against:

ZIP path traversal

absolute paths

unsafe archive entries

excessive file counts

excessive uncompressed size

oversized uploads


Uploaded repositories are never imported, executed, or evaluated.


---

🔬 Static Inspection Mode

The upload pipeline currently performs conservative static analysis.

For Python repositories, Necro uses AST-based inspection.

For other supported languages, it can use static/regex-based reference detection where applicable.

The inspector looks for signals including:

function definitions

class definitions

direct references

calls

docstrings

configuration references

quoted string references

dynamic-dispatch patterns


Important limitation

Static analysis cannot guarantee that a function is unused.

Runtime-only behavior, reflection, external consumers, generated code, and other dynamic mechanisms may not be visible to the inspector.

For that reason, uploaded-repository confidence is intentionally capped at Medium.


---

🏗️ Architecture

flowchart TD
    A[Repository] --> B{Analysis Mode}

    B -->|Verified Demo| C[IBM Bob 2.0 Workflow]
    B -->|Uploaded ZIP| D[Static Repository Inspector]

    C --> E[Classification]
    D --> E

    E --> F{Verdict}

    F -->|Safe to Delete| G[Deletion Artifact]
    F -->|Secretly Load-Bearing| H[ADR / Documentation]
    F -->|Undocumented| I[Documentation Artifact]
    F -->|Normal| J[No Action]

    G --> K[Dashboard]
    H --> K
    I --> K
    J --> K

    K --> L[Evidence]
    K --> M[Artifacts]


---

🧩 How It Works

1. Ingest

For the verified demo, the repository is prepared as a controlled analysis target.

For uploaded repositories, Necro safely extracts the ZIP into a temporary workspace.

2. Analyze

Bob 2.0 mode

The demonstration workflow uses Bob 2.0's repository-level reasoning to investigate code relationships.

Static mode

Uploaded repositories are analyzed without executing their code.

3. Classify

Necro assigns one of four verdicts based on the available evidence.

4. Capture Evidence

Relevant references, configuration relationships, source context, and reasoning are surfaced in the dashboard.

5. Generate Artifacts

Where supported by the verified analysis workflow, Necro generates actionable artifacts such as deletion patches, documentation, and ADRs.

6. Present

The dashboard turns the analysis into an explorable investigation rather than a raw JSON report.


---

🧰 Technology Stack

Layer	Technology	Purpose

AI reasoning	IBM Bob 2.0	Repository-level reasoning for the verified demo
Backend	Python	Analysis pipeline and HTTP server
Static analysis	Python AST + static heuristics	Uploaded repository inspection
Storage	JSON / filesystem	Results, evidence, artifacts
Frontend	HTML / CSS / JavaScript	Interactive dashboard
Deployment	Render	Public demo deployment
Source control	GitHub	Project repository



---

📁 Project Structure

Necro-Code-Archaeology/
│
├── dashboard/
│   ├── index.html
│   ├── styles.css
│   └── app.js
│
├── demo_repo/
│   ├── src/
│   │   ├── main.py
│   │   ├── utils.py
│   │   ├── router.py
│   │   ├── legacy_feature.py
│   │   └── analytics.py
│   └── config/
│       └── routes.json
│
├── necro/
│   ├── bob_wrapper.py
│   ├── classifier.py
│   ├── artifact_generator.py
│   ├── evidence_logger.py
│   ├── repo_inspector.py
│   ├── upload_handler.py
│   └── config.py
│
├── prompts/
│   ├── classify_module.txt
│   ├── generate_deletion.txt
│   ├── generate_docs.txt
│   └── generate_adr.txt
│
├── results/
│   ├── results.json
│   └── evidence/
│
├── artifacts/
│   ├── deletions/
│   ├── documentation/
│   └── adrs/
│
├── scripts/
│   ├── run_pipeline.py
│   ├── seed_demo_repo.py
│   └── serve_dashboard.py
│
├── test_upload_api.py
├── test_upload_simple.py
├── test_upload_comprehensive.py
│
├── QUICKSTART.md
├── ARCHITECTURE.md
├── IMPLEMENTATION_PLAN.md
├── requirements.txt
└── README.md


---

⚡ Quick Start

Clone

git clone https://github.com/Tuxhar01/Necro-Code-Archaeology.git
cd Necro-Code-Archaeology

Create an environment

Windows

python -m venv venv
venv\Scripts\activate

macOS / Linux

python3 -m venv venv
source venv/bin/activate

Install dependencies

pip install -r requirements.txt

Start the dashboard

python scripts/serve_dashboard.py

Open:

http://localhost:8000

Explore the verified demo

Choose:

Explore Verified Demo

Analyze your own repository

Choose:

Analyze Your Repository

and upload a .zip repository.

For the complete Bob 2.0 analysis workflow, see:

QUICKSTART.md

ARCHITECTURE.md

IMPLEMENTATION_PLAN.md



---

🧪 Testing

The repository includes tests for the repository-upload MVP.

The test suite covers areas including:

demo regression

successful ZIP upload

invalid ZIP rejection

ZIP path traversal protection

oversized upload handling

temporary extraction cleanup

unrelated POST rejection

demo switching


Run the comprehensive upload test suite with:

python test_upload_comprehensive.py

The uploaded-repository analyzer is deliberately conservative and does not execute repository code during analysis.


---

🔐 Security Model

Uploaded repositories are treated as untrusted input.

Necro:

does not execute uploaded source code

does not import uploaded modules

does not evaluate uploaded expressions

does not install uploaded dependencies

validates archive paths

limits upload size

limits extracted size

limits file count

cleans temporary extraction directories


Static inspection is performed against extracted source/configuration files only.


---

📌 Current Limitations

Necro is currently a hackathon MVP.

Uploaded repositories

Uploaded repositories use static inspection rather than live Bob 2.0 reasoning.

Dynamic behavior

Static analysis may miss:

reflection

runtime-generated references

external consumers

generated code

behavior dependent on external systems


Analysis scope

The repository-upload MVP limits the number of analyzed candidates to keep analysis bounded.

GitHub automation

Necro currently does not automatically create GitHub pull requests.

Generated patches and artifacts are available for inspection/download instead.


---

🗺️ Roadmap

Current MVP

[x] IBM Bob 2.0 analysis workflow

[x] Evidence-backed classifications

[x] Five-case demonstration repository

[x] Artifact generation

[x] Interactive dashboard

[x] Repository ZIP upload

[x] Static repository inspection

[x] Upload security controls

[x] Demo/live deployment


Future

[ ] Direct GitHub repository integration

[ ] GitHub PR creation

[ ] CI/CD integration

[ ] Multi-repository analysis

[ ] Historical analysis and code-debt tracking

[ ] Custom classification rules

[ ] Team collaboration

[ ] Live Bob 2.0 analysis for connected repositories



---

🏆 Why Necro?

Legacy code isn't necessarily dead code.

A function with no obvious import can still be part of:

Configuration
      ↓
String Dispatch
      ↓
Dynamic Loading
      ↓
Runtime Behavior

Necro's goal is to make those relationships visible before somebody reaches for git rm.

> Don't delete what you don't understand. Unearth it first.




---

🤝 Contributing

Contributions are welcome.

1. Fork the repository.


2. Create a feature branch.


3. Make your changes.


4. Add or update tests.


5. Submit a pull request.




---

📄 License

MIT License.

See LICENSE for details.


---

🙏 Acknowledgments

IBM Bob 2.0 — for the repository-level reasoning workflow demonstrated by Necro

IBM Bob 2.0 Hackathon — for the opportunity to build and explore this concept

Every developer who has inherited a codebase containing a function nobody remembers writing



---

<div align="center">

## 🏺 Necro — Code Archaeology

**Find dead code. Detect hidden dependencies. Preserve what matters.**

Built with **IBM Bob 2.0** for the **IBM Bob 2.0 Hackathon 2026**.

[Live Demo](https://necro-code-archaeology.onrender.com) · [GitHub](https://github.com/Tuxhar01/Necro-Code-Archaeology)

</div>