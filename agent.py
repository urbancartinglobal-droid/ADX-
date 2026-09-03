"""ADX application launcher.

Run this file to start the main ADX LiveKit agent and GUI.
"""

import runpy


if __name__ == "__main__":
    runpy.run_module("brain", run_name="__main__")
