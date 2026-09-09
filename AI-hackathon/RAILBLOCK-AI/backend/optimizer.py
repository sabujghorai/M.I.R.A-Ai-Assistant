from backend.conflict import check_conflict


def minutes_to_time(minutes):
    """Convert minutes into HH:MM format."""

    hour = minutes // 60
    minute = minutes % 60

    return f"{hour:02d}:{minute:02d}"


def find_best_block(duration_hours, train_times):
    """
    Find the first available maintenance block
    between 08:00 and 18:00.
    """

    duration = duration_hours * 60

    start = 8 * 60
    end = 18 * 60

    while start + duration <= end:

        block_end = start + duration

        block_start = minutes_to_time(start)
        block_end_time = minutes_to_time(block_end)

        conflicts = check_conflict(
            block_start,
            block_end_time,
            train_times
        )

        if not conflicts:
            return {
                "start": block_start,
                "end": block_end_time,
                "conflicts": []
            }

        start += 30

    return None