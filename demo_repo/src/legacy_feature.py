"""
CASE 1: Genuinely Dead Function #1
Legacy feature module from the old metrics system.
This entire module was replaced by the new analytics system in v2.0.
"""


def calculate_legacy_metrics(data):
    """
    Old metrics calculation - replaced by new system.
    This function computed simple averages for the v1.0 dashboard.
    No longer used anywhere in the codebase.
    """
    if not data or len(data) == 0:
        return 0
    return sum(data) / len(data)


def aggregate_legacy_stats(records):
    """
    Aggregate statistics using old algorithm.
    Part of the deprecated v1.0 reporting system.
    """
    total = 0
    count = 0
    for record in records:
        if "value" in record:
            total += record["value"]
            count += 1
    return {"total": total, "count": count, "average": total / count if count > 0 else 0}

# Made with Bob
