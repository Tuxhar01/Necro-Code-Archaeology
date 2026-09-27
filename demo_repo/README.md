# Demo Repository for Necro Testing

This is a carefully seeded test repository containing 5 distinct code patterns for testing Necro's classification capabilities.

## Test Cases

### Case 1: Genuinely Dead Function #1
**Location:** `src/legacy_feature.py::calculate_legacy_metrics()`
**Pattern:** No references anywhere in codebase
**Expected Verdict:** Safe to Delete

### Case 2: Genuinely Dead Function #2
**Location:** `src/utils.py::format_old_date()`
**Pattern:** Leftover from removed feature (different from Case 1)
**Expected Verdict:** Safe to Delete

### Case 3: Fake-Dead / Secretly Load-Bearing
**Location:** `src/analytics.py::track_user_event()`
**Pattern:** Called via string-based dispatch in `router.py` and referenced in `config/routes.json`
**Challenge:** Static analysis misses this because it's dynamically loaded
**Expected Verdict:** Secretly Load-Bearing

### Case 4: Undocumented but Clearly Used
**Location:** `src/utils.py::validate_input()`
**Pattern:** No docstring, no comments, but directly called in `main.py`
**Expected Verdict:** Undocumented but Valuable

### Case 5: Control Case (Normal)
**Location:** `src/main.py::process_request()`
**Pattern:** Well-documented, clearly used, normal function
**Expected Verdict:** Normal / No Action

## File Structure

```
demo_repo/
├── README.md
├── src/
│   ├── main.py              # Control case + uses validate_input
│   ├── utils.py             # Contains Case 2 (dead) and Case 4 (undocumented)
│   ├── legacy_feature.py    # Case 1 (dead)
│   ├── analytics.py         # Case 3 (fake-dead)
│   └── router.py            # String-based dispatcher (makes analytics load-bearing)
└── config/
    └── routes.json          # Config-based references to analytics
```

## Key Patterns to Test

1. **Direct references** - Easy to detect (Case 5)
2. **No references** - Should be safe to delete (Cases 1, 2)
3. **String-based dispatch** - Hard to detect, requires reasoning (Case 3)
4. **Config-driven usage** - Indirect reference pattern (Case 3)
5. **Missing documentation** - Used but undocumented (Case 4)

## Running the Demo Code

```bash
# Test the normal flow
python src/main.py

# Test the router (which uses analytics via string dispatch)
python -c "from src.router import route_request; print(route_request('analytics', {'event': 'test', 'user_id': 123}))"
```

## Expected Necro Analysis Results

| Module | Verdict | Confidence | Key Evidence |
|--------|---------|------------|--------------|
| `legacy_feature.calculate_legacy_metrics` | Safe to Delete | High | No references found |
| `utils.format_old_date` | Safe to Delete | High | No references found |
| `analytics.track_user_event` | Secretly Load-Bearing | High | String dispatch in router.py:13, config reference in routes.json |
| `utils.validate_input` | Undocumented but Valuable | High | Called in main.py:15, no docstring |
| `main.process_request` | Normal | High | Well-documented, clearly used |

---

*This repository is designed to test Necro's ability to distinguish between genuinely dead code, secretly load-bearing code, and undocumented-but-valuable code.*