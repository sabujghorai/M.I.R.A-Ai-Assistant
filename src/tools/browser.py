import urllib.parse
import webbrowser


def open_url(url: str) -> dict:
    """
    Open a URL in the default browser.
    """

    try:
        if not url.startswith(
            ("http://", "https://")
        ):
            url = "https://" + url

        opened = webbrowser.open(url)

        if opened:
            return {
                "success": True,
                "message": f"Opened {url}"
            }

        return {
            "success": False,
            "message": f"Could not open {url}"
        }

    except Exception as error:
        return {
            "success": False,
            "message": str(error)
        }


def google_search(query: str) -> dict:
    """
    Search Google.
    """

    try:
        encoded_query = urllib.parse.quote_plus(
            query
        )

        url = (
            "https://www.google.com/search?q="
            + encoded_query
        )

        opened = webbrowser.open(url)

        if opened:
            return {
                "success": True,
                "message": (
                    f"Searched Google for {query}"
                )
            }

        return {
            "success": False,
            "message": "Could not open Google."
        }

    except Exception as error:
        return {
            "success": False,
            "message": str(error)
        }


def youtube_search(query: str) -> dict:
    """
    Search YouTube.
    """

    try:
        encoded_query = urllib.parse.quote_plus(
            query
        )

        url = (
            "https://www.youtube.com/results"
            "?search_query="
            + encoded_query
        )

        opened = webbrowser.open(url)

        if opened:
            return {
                "success": True,
                "message": (
                    f"Searched YouTube for {query}"
                )
            }

        return {
            "success": False,
            "message": "Could not open YouTube."
        }

    except Exception as error:
        return {
            "success": False,
            "message": str(error)
        }
