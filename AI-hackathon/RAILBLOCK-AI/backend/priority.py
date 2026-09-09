def calculate_priority(priority):
    """
    Convert maintenance priority into a score.
    """

    priority_scores = {
        "Critical": 100,
        "High": 80,
        "Medium": 60,
        "Low": 30
    }

    return priority_scores.get(priority, 0)