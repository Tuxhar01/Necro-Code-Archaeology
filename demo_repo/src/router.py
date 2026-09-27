"""
Dynamic routing system that uses string-based dispatch.
This is what makes analytics.track_user_event secretly load-bearing.
"""

import importlib


# String-based handler mapping - this is the key pattern that static analysis misses
HANDLERS = {
    "user_event": "analytics.track_user_event",
    "system_metric": "analytics.log_system_metric",
    "error": "analytics.record_error",
}


def dispatch_event(event_name, *args, **kwargs):
    """
    Dynamically dispatch events to their handlers.
    This uses string-based lookup, making it invisible to simple static analysis.
    """
    if event_name not in HANDLERS:
        print(f"[ROUTER] Unknown event: {event_name}")
        return None
    
    handler_path = HANDLERS[event_name]
    module_name, function_name = handler_path.rsplit(".", 1)
    
    try:
        # Dynamic import - this is why analytics functions appear unused
        module = importlib.import_module(module_name)
        handler = getattr(module, function_name)
        return handler(*args, **kwargs)
    except (ImportError, AttributeError) as e:
        print(f"[ROUTER] Error loading handler {handler_path}: {e}")
        return None


def route_request(request_type, data):
    """
    Route incoming requests based on type.
    Uses the dispatch system to handle different request types.
    """
    if request_type == "analytics":
        return dispatch_event("user_event", data.get("event"), data.get("user_id"))
    elif request_type == "metrics":
        return dispatch_event("system_metric", data.get("metric"), data.get("value"))
    elif request_type == "error":
        return dispatch_event("error", data.get("type"), data.get("details"))
    else:
        return {"status": "unknown_type"}

# Made with Bob
