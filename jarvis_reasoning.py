from dotenv import load_dotenv

from langchain.agents import AgentExecutor, create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import hub
from livekit.agents import function_tool

from jarvis_search import google_search, get_current_datetime
from jarvis_get_whether import get_weather
from Jarvis_window_CTRL import list_folder_items, run_application_or_media
from Jarvis_file_opner import Play_file
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

load_dotenv()


@function_tool(
    name="thinking_capability",
    description=(
        "Use this tool whenever the user asks to generate or write something new. "
        "If the user does not specify where to write, use the available Windows "
        "application/file tools. This tool can also handle search, weather, "
        "file access, mouse/keyboard control, and system utilities."
    ),
)
async def thinking_capability(query: str) -> dict:
    """LangChain-powered reasoning and action tool."""
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    prompt = hub.pull("hwchase17/react")

    tools = [
        google_search,
        get_current_datetime,
        get_weather,
        run_application_or_media,
        list_folder_items,
        Play_file,
        move_cursor_tool,
        mouse_click_tool,
        scroll_cursor_tool,
        type_text_tool,
        press_key_tool,
        press_hotkey_tool,
        control_volume_tool,
        swipe_gesture_tool,
    ]

    agent = create_react_agent(
        llm=model,
        tools=tools,
        prompt=prompt,
    )

    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
    )

    try:
        return await executor.ainvoke({"input": query})
    except Exception as e:
        return {"error": f"Agent execution failed: {e}"}
