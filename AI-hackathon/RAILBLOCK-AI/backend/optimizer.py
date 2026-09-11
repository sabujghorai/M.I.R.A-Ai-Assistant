from backend.conflict import check_conflict


def minutes_to_time(minutes):
    """Convert minutes into HH:MM format."""

    hour = minutes // 60
    minute = minutes % 60

    return f"{hour:02d}:{minute:02d}"


def time_to_minutes(time_string):
    """Convert HH:MM into minutes."""

    hour, minute = map(int, time_string.split(":"))

    return hour * 60 + minute


def blocks_overlap(start1, end1, start2, end2):
    """Check whether two time blocks overlap."""

    start1 = time_to_minutes(start1)
    end1 = time_to_minutes(end1)

    start2 = time_to_minutes(start2)
    end2 = time_to_minutes(end2)

    return start1 < end2 and start2 < end1


def find_best_block(duration_hours, train_times, existing_schedule=None):
    """
    Find the first available maintenance block
    between 08:00 and 18:00 across the working week.
    """

    if existing_schedule is None:
        existing_schedule = []

    duration = duration_hours * 60

    start_time = 8 * 60
    end_time = 18 * 60

    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday"
    ]

    # Check each day
    for day in days:

        start = start_time

        while start + duration <= end_time:

            block_end = start + duration

            block_start = minutes_to_time(start)
            block_end_time = minutes_to_time(block_end)

            # -------------------------------------
            # Check train conflicts
            # -------------------------------------

            conflicts = check_conflict(
                block_start,
                block_end_time,
                train_times
            )

            if conflicts:
                start += 30
                continue

            # -------------------------------------
            # Check existing weekly blocks
            # -------------------------------------

            schedule_conflict = False

            for existing in existing_schedule:

                if existing["day"] != day:
                    continue

                existing_start, existing_end = existing["block_time"].split(" - ")

                if blocks_overlap(
                    block_start,
                    block_end_time,
                    existing_start,
                    existing_end
                ):
                    schedule_conflict = True
                    break

            if schedule_conflict:
                start += 30
                continue

            # -------------------------------------
            # Suitable block found
            # -------------------------------------

            return {
                "day": day,
                "start": block_start,
                "end": block_end_time,
                "conflicts": []
            }

            start += 30

    return None