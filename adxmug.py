"""ADXmug integration for the ADX personal assistant."""

import webbrowser

from livekit.agents import function_tool

ADX_MUG_URL = "https://www.gigamug.ai"


@function_tool
def open_adxmug() -> str:
    """Open the Gigamug AI website, presented to the user as ADXmug."""
    try:
        webbrowser.open(ADX_MUG_URL)
        return "ADXmug खोल दिया गया है।"
    except Exception as e:
        return f"ADXmug खोलने में समस्या हुई: {e}"
