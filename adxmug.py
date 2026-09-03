"""ADXmug business-intelligence module.

Independent implementation inspired by the requested workflow: Corporate,
Macro and Global intelligence streams, source filtering, impact mapping and
concise decision-ready briefs. No paid Gigamug subscription is required.
"""

import asyncio
import logging
import os
import subprocess
import sys
import webbrowser
from typing import Dict, List

from livekit.agents import function_tool

from jarvis_search import search_internet

logger = logging.getLogger(__name__)

ADX_MUG_WEB_URL = "https://urbancartinglobal-droid.github.io/ADX-/adxmug/"

SOURCE_HINTS = {
    "corporate": "India listed companies earnings capex orders capacity expansion acquisitions filings annual reports presentations conference calls",
    "macro": "India RBI government ministries SEBI policy notifications budget PLI procurement regulation infrastructure industry impact",
    "global": "Federal Reserve White House US Treasury ECB China Japan OPEC commodity copper gold oil India business impact",
}


def _clean_text(text: str) -> str:
    return " ".join((text or "").split())


def _impact_score(text: str) -> int:
    """Lightweight prioritisation score; it is not a market prediction."""
    positive = (
        "order", "orders", "capex", "capacity", "tariff", "policy", "approval",
        "contract", "investment", "expansion", "production", "export", "demand",
        "pli", "procurement", "acquisition", "rate cut", "subsidy",
    )
    negative = (
        "shutdown", "penalty", "ban", "downgrade", "default", "fraud",
        "weak demand", "cut production", "loss", "investigation",
    )
    lowered = text.lower()
    score = 50
    score += min(35, sum(lowered.count(word) for word in positive) * 3)
    score -= min(30, sum(lowered.count(word) for word in negative) * 5)
    return max(0, min(100, score))


async def _search_unit(unit: str, topic: str) -> str:
    query = f"{topic} {SOURCE_HINTS[unit]} latest"
    try:
        return await search_internet(query)
    except Exception as exc:
        logger.warning("ADXmug search failed for %s: %s", unit, exc)
        return f"Search unavailable for {unit}: {exc}"


@function_tool
async def adxmug_intelligence(topic: str = "India industry opportunities") -> str:
    """Scan Corporate, Macro and Global intelligence streams."""
    topic = _clean_text(topic) or "India industry opportunities"
    corporate, macro, global = await asyncio.gather(
        _search_unit("corporate", topic),
        _search_unit("macro", topic),
        _search_unit("global", topic),
    )
    raw: Dict[str, str] = {
        "Corporate Intelligence": corporate,
        "Macro Intelligence": macro,
        "Global Intelligence": global,
    }
    ranked: List[tuple] = []
    for name, text in raw.items():
        clean = _clean_text(text)
        ranked.append((_impact_score(clean), name, clean))
    ranked.sort(reverse=True)

    lines = [
        "ADXmug — Intelligence Brief",
        f"Query: {topic}",
        "",
        "THREE INTELLIGENCE UNITS",
        "1) Corporate Intelligence — companies, capex, orders, earnings and business changes.",
        "2) Macro Intelligence — RBI, ministries, regulation, policy and domestic demand.",
        "3) Global Intelligence — major economies, trade, commodities and global spillovers.",
        "",
        "PRIORITISED SIGNALS",
    ]
    for score, name, text in ranked:
        excerpt = text[:900] if text else "No usable search result."
        lines.append(f"[{name}] Signal priority: {score}/100")
        lines.append(excerpt)
        lines.append("")
    lines.extend([
        "DECISION FILTER",
        "• Prefer developments with a credible path from trigger → business impact → earnings.",
        "• Separate confirmed facts from interpretation; do not invent numbers or catalysts.",
        "• For Indian equity analysis, restrict company discussion to NSE/BSE-listed names when possible.",
        "• Research/education only: no buy/sell/hold recommendation or price target.",
        "",
        "NEXT STEP",
        "Use the strongest signal for the full 7DIO.EL sectoral story: hidden trigger, value chain, earnings translation, timeline and Bull/Base/Bear cases.",
    ])
    return "\n".join(lines)


@function_tool
async def adxmug_find_industry_opportunity() -> str:
    """Find an emerging, potentially underappreciated Indian industry opportunity."""
    return await adxmug_intelligence("Which Indian industry currently has an underappreciated opportunity?")


@function_tool
async def get_adxmug_status() -> str:
    """Return ADXmug module status and intelligence units."""
    return "ADXmug: ACTIVE | Units: Corporate, Macro, Global | Mode: research and signal discovery"


@function_tool
def open_adxmug() -> str:
    """Open the live ADXmug dashboard from the ADX AI assistant."""
    try:
        opened = webbrowser.open(ADX_MUG_WEB_URL, new=2)
        if opened:
            return "ADXmug live Command Center खोल दिया गया है।"

        # Browser launch can fail on some desktop environments; keep the
        # existing local ADXmug mode as a safe fallback.
        dashboard = os.path.join(os.path.dirname(__file__), "jarvis_ui.py")
        env = os.environ.copy()
        env["ADX_MUG_MODE"] = "1"
        subprocess.Popen([sys.executable, dashboard], env=env)
        return "Live ADXmug browser नहीं खुला, इसलिए local ADXmug Command Center खोल दिया गया है।"
    except Exception as exc:
        return f"ADXmug खोलने में समस्या हुई: {exc}"
