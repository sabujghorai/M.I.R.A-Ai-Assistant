import datetime
import platform


def get_current_time() -> dict:
    """Return the current local time."""

    now = datetime.datetime.now()

    return {
        "success": True,
        "message": now.strftime(
            "The current time is %I:%M %p."
        )
    }


def get_current_date() -> dict:
    """Return today's date."""

    now = datetime.datetime.now()

    return {
        "success": True,
        "message": now.strftime(
            "Today is %A, %B %d, %Y."
        )
    }


def get_computer_info() -> dict:
    """Return basic Mac information."""

    return {
        "success": True,
        "message": (
            f"System: {platform.system()}, "
            f"macOS version: {platform.mac_ver()[0]}, "
            f"Architecture: {platform.machine()}"
        )
    }
