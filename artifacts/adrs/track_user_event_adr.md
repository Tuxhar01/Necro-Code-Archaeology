# ADR: track_user_event Must Be Retained

## Status
**ACTIVE - DO NOT DELETE**

## Context
The function `track_user_event` in `demo_repo/src/analytics.py` appears unused when examined with simple static analysis tools. However, it is critically load-bearing through indirect dispatch mechanisms.

## Evidence of Indirect Usage

### 1. String-Based Dispatch in router.py
```python
# router.py line 11
HANDLERS = {
    "user_event": "analytics.track_user_event",
    ...
}
```

### 2. Dynamic Import Mechanism
```python
# router.py line 31
module = importlib.import_module(module_name)
handler = getattr(module, function_name)
```

### 3. Configuration File References
`config/routes.json` contains multiple references:
- Line 3: `"user_action": "analytics.track_user_event"`
- Line 14: `"handler": "analytics.track_user_event"` (login events)
- Line 18: `"handler": "analytics.track_user_event"` (logout events)  
- Line 22: `"handler": "analytics.track_user_event"` (page view events)

## Decision
This function MUST be retained. Deleting it would break:
- All user event tracking (login, logout, page views)
- The dynamic routing system's event dispatch
- Any configuration-driven analytics calls

## Consequences

### Immediate Actions Required:
1. **Add documentation** explaining the indirect usage pattern
2. **Update docstring** with warnings about string-based dispatch
3. **Add tests** that verify the routing system can load this function

### Recommended Refactoring:
- Consider making the dispatch more explicit with direct imports
- Add type hints to make IDE tools aware of usage
- Document the HANDLERS mapping in router.py more clearly

## Enhanced Docstring

```python
def track_user_event(event_type, user_id):
    """
    Track user events for analytics.
    
    **CRITICAL**: This function is called via dynamic dispatch, not direct imports.
    
    Usage Patterns:
    - router.py loads this via importlib based on HANDLERS dict
    - config/routes.json maps multiple event types to this function
    - Called for: user logins, logouts, page views, and custom events
    
    DO NOT DELETE without:
    1. Checking router.py HANDLERS dictionary (line 11)
    2. Reviewing config/routes.json event_handlers section
    3. Verifying no string-based function lookups reference this
    4. Testing the full event routing system
    
    Args:
        event_type: Type of event being tracked (e.g., 'user_login')
        user_id: ID of the user performing the action
        
    Returns:
        dict: Confirmation with event details and tracking status
    """
    print(f"[ANALYTICS] Event: {event_type} for user {user_id}")
    return {"event": event_type, "user": user_id, "tracked": True}
```