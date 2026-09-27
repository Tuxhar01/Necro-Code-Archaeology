"""
CASE 3: Fake-Dead / Secretly Load-Bearing
Analytics module that appears unused but is called via string-based dispatch.
Static analysis will miss this because it's loaded dynamically.
"""


def track_user_event(event_type, user_id):
    """
    Track user events for analytics.
    Called via string-based dispatch - static analysis misses it.
    """
    print(f"[ANALYTICS] Event: {event_type} for user {user_id}")
    # In a real system, this would log to a database or analytics service
    return {"event": event_type, "user": user_id, "tracked": True}


def log_system_metric(metric_name, value):
    """
    Log system performance metrics.
    Also called via dynamic dispatch.
    """
    print(f"[METRICS] {metric_name}: {value}")
    return {"metric": metric_name, "value": value}


def record_error(error_type, details):
    """
    Record application errors for monitoring.
    Part of the error tracking system.
    """
    print(f"[ERROR] {error_type}: {details}")
    return {"error": error_type, "details": details, "recorded": True}

# Made with Bob
