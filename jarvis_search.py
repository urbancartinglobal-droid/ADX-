# jarvis_search.py
import os
import requests
import asyncio
import logging
from dotenv import load_dotenv
from livekit.agents import function_tool
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] %(message)s"
)

load_dotenv()

# Keep credentials out of source code. Put them in environment variables.
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY", "")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID", "")


@function_tool
async def search_internet(query: str) -> str:
    """Perform a Google Custom Search and return the top 3 results."""
    if not GOOGLE_SEARCH_API_KEY or not SEARCH_ENGINE_ID:
        logging.error("Google Search API credentials not found in environment.")
        return "Google Search API credentials not found in environment."

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_SEARCH_API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "q": query,
    }

    try:
        response = await asyncio.to_thread(
            requests.get, url, params=params, timeout=10
        )
        response.raise_for_status()
        data = response.json()

        if "items" not in data:
            logging.warning("No results found for query: %s", query)
            return f"No results found for: {query}"

        results = []
        for item in data["items"][:3]:
            title = item.get("title", "No title")
            snippet = item.get("snippet", "")
            link = item.get("link", "")
            results.append(f"{title}\n{snippet}\n{link}")

        return "\n\n".join(results)

    except Exception as e:
        logging.error("Error performing search: %s", e)
        return f"Error performing search: {e}"


# Compatibility names used by the rest of the project.
google_search = search_internet


@function_tool
async def get_formatted_datetime() -> str:
    """Return the current date and time in a human-readable format."""
    now = datetime.now()
    return now.strftime("%A, %B %d, %Y - %I:%M %p")


get_current_datetime = get_formatted_datetime
