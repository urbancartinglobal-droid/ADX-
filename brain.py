from dotenv import load_dotenv

import asyncio
import logging
import os
import subprocess
import sys

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import google, noise_cancellation

from jarvis_prompt import behavior_prompts, Reply_prompts
from jarvis_search import google_search, get_current_datetime
from memory_store import (
    load_memory,
    save_memory,
    get_recent_conversations,
    add_memory_entry,
)
from jarvis_get_whether import get_weather
from Jarvis_window_CTRL import open_file, list_folder_items, run_application_or_media
from ADX_file_opner import Play_file
from adxmug import (
    adxmug_intelligence,
    adxmug_find_industry_opportunity,
    get_adxmug_status,
)
from keyboard_mouse_CTRL import (
    move_cursor_tool,
    mouse_click_tool,
    scroll_cursor_tool,
    type_text_tool,
    press_key_tool,
    swipe_gesture_tool,
    press_hotkey_tool,
    control_volume_tool,
)
from adx_features import (
    set_adx_mode,
    get_adx_status,
    request_action_confirmation,
    resolve_action_confirmation,
    detect_wake_word,
    plan_task,
    set_adx_status,
)

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ENABLE_MEMORY_INTERCEPTOR = True


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=behavior_prompts,
            tools=[
                google_search,
                get_current_datetime,
                get_weather,
                open_file,
                list_folder_items,
                run_application_or_media,
                adxmug_intelligence,
                adxmug_find_industry_opportunity,
                get_adxmug_status,
                load_memory,
                save_memory,
                get_recent_conversations,
                add_memory_entry,
                Play_file,
                move_cursor_tool,
                mouse_click_tool,
                scroll_cursor_tool,
                type_text_tool,
                press_key_tool,
                press_hotkey_tool,
                control_volume_tool,
                swipe_gesture_tool,
                set_adx_mode,
                get_adx_status,
                request_action_confirmation,
                resolve_action_confirmation,
                detect_wake_word,
                plan_task,
                set_adx_status,
            ],
        )


async def entrypoint(ctx: agents.JobContext):
    """Start the LiveKit agent session with retry handling."""
    max_retries = 5
    retry_count = 0
    base_wait_time = 3

    while retry_count < max_retries:
        try:
            print(
                f"\n🚀 Starting ADX agent session "
                f"(attempt {retry_count + 1}/{max_retries})..."
            )

            session = AgentSession(
                llm=google.beta.realtime.RealtimeModel(voice="Charon")
            )

            await session.start(
                room=ctx.room,
                agent=Assistant(),
                room_input_options=RoomInputOptions(
                    noise_cancellation=noise_cancellation.BVC(),
                    video_enabled=True,
                ),
            )

            await ctx.connect()
            print("✅ ADX connected to room, waiting for audio input...")

            instructions = Reply_prompts

            if ENABLE_MEMORY_INTERCEPTOR:
                try:
                    print("🧠 Fetching memory context...")
                    memory_context = await get_recent_conversations(limit=5)
                    if "अभी तक कोई बातचीत याद नहीं है" not in memory_context:
                        instructions = (
                            f"{Reply_prompts}\n\n"
                            f"[RECENT CONTEXT]\n{memory_context}\n[/CONTEXT]"
                        )
                        print("✅ Memory context injected")
                except Exception as e:
                    logger.warning("Memory injection skipped: %s", e)

            print("📡 Sending instructions to LLM...")
            await session.generate_reply(instructions=instructions)
            print("✅ ADX session completed successfully")
            break

        except KeyboardInterrupt:
            print("\n⛔ ADX stopped by user")
            break
        except Exception as e:
            retry_count += 1
            print(
                f"❌ Session error (attempt {retry_count}/{max_retries}): {e}"
            )
            if retry_count < max_retries:
                wait_time = base_wait_time * retry_count
                print(f"⏳ Waiting {wait_time}s before retry...")
                await asyncio.sleep(wait_time)
            else:
                print("❌ Max retries exceeded. Shutting down.")
                raise


if __name__ == "__main__":
    try:
        gui_path = os.path.join(os.path.dirname(__file__), "jarvis_ui.py")
        if os.path.exists(gui_path):
            subprocess.Popen(
                [sys.executable, gui_path],
                stdout=None,
                stderr=None,
                stdin=None,
                close_fds=True,
            )
        else:
            print("jarvis_ui.py not found; GUI will not be started.")
    except Exception as e:
        print("Failed to start GUI subprocess:", e)

    agents.cli.run_app(
        agents.WorkerOptions(entrypoint_fnc=entrypoint)
    )
