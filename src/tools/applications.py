import subprocess


def open_application(application_name: str) -> dict:
    """
    Open a macOS application.

    Example:
        open_application("Google Chrome")
    """

    try:
        result = subprocess.run(
            ["open", "-a", application_name],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return {
                "success": True,
                "message": (
                    f"{application_name} "
                    "opened successfully."
                )
            }

        error_message = (
            result.stderr.strip()
            or f"Could not open {application_name}."
        )

        return {
            "success": False,
            "message": error_message
        }

    except Exception as error:
        return {
            "success": False,
            "message": str(error)
        }


def close_application(application_name: str) -> dict:
    """
    Close a macOS application.
    """

    try:
        script = f'''
        tell application "{application_name}"
            quit
        end tell
        '''

        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return {
                "success": True,
                "message": (
                    f"{application_name} "
                    "closed successfully."
                )
            }

        error_message = (
            result.stderr.strip()
            or f"Could not close {application_name}."
        )

        return {
            "success": False,
            "message": error_message
        }

    except Exception as error:
        return {
            "success": False,
            "message": str(error)
        }
