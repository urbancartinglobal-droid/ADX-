"""ADX next-level assistant features.

This module provides lightweight building blocks for wake-word handling,
modes, task planning, safety confirmations, and Command Center status.
These features are intentionally dependency-light so ADX can run even when
optional vision/phone integrations are not configured.
"""

from datetime import datetime
from livekit.agents import function_tool

MODES = ("Normal", "Coding", "Study", "Work", "Gaming", "Developer")
_current_mode = "Normal"
_pending_confirmation = None
_status = "Idle"


@function_tool
async def set_adx_mode(mode: str) -> str:
    """Switch ADX between Normal, Coding, Study, Work, Gaming, and Developer modes."""
    global _current_mode
    requested = mode.strip().title()
    if requested not in MODES:
        return f"Unknown mode. Available modes: {', '.join(MODES)}"
    _current_mode = requested
    return f"ADX mode changed to {requested}."


@function_tool
async def get_adx_status() -> str:
    """Return the current ADX Command Center status."""
    return f"Mode: {_current_mode} | Status: {_status} | Time: {datetime.now():%I:%M:%S %p}"


@function_tool
async def request_action_confirmation(action: str) -> str:
    """Ask for confirmation before a sensitive/destructive action."""
    global _pending_confirmation
    _pending_confirmation = action.strip()
    return f"Confirmation required before: {_pending_confirmation}. Reply 'confirm' to continue or 'cancel' to stop."


@function_tool
async def resolve_action_confirmation(answer: str) -> str:
    """Resolve a pending sensitive-action confirmation."""
    global _pending_confirmation
    if not _pending_confirmation:
        return "There is no pending action requiring confirmation."
    action = _pending_confirmation
    _pending_confirmation = None
    normalized = answer.strip().lower()
    if normalized in {"confirm", "confirmed", "yes", "haan", "ha"}:
        return f"Confirmed: {action}"
    return f"Cancelled: {action}"


@function_tool
async def detect_wake_word(text: str) -> str:
    """Detect whether a transcript contains the ADX wake phrase."""
    normalized = text.lower().replace("-", " ")
    phrases = ("hey adx", "hi adx", "adx")
    return "Wake word detected." if any(p in normalized for p in phrases) else "Wake word not detected."


@function_tool
async def plan_task(task: str) -> str:
    """Turn a natural-language task into a safe, high-level execution plan."""
    text = task.strip()
    if not text:
        return "Please provide a task."
    return (
        f"Task: {text}\n"
        "Plan: 1) Understand intent 2) Gather required information 3) Execute available tools "
        "4) Verify result 5) Report completion. Sensitive/destructive steps require confirmation."
    )


@function_tool
async def set_adx_status(status: str) -> str:
    """Update the status shown by the ADX Command Center."""
    global _status
    _status = status.strip() or "Idle"
    return f"ADX status: {_status}"


def get_mode() -> str:
    """Internal helper for integrations such as the GUI."""
    return _current_mode
