# 🤖 ADX – Advanced Real-Time AI Personal Assistant (Python)

ADX is a real-time AI personal assistant built in Python, capable of answering live queries, controlling Windows OS, executing keyboard commands, opening files, storing memory, and performing system automation.

This project is designed for automation, speed, extensibility, and real-world usage.

---

## 🚀 Core Features

✅ **Real-Time AI Interaction**
- Instant AI-powered responses
- Text & optional voice-based commands
- Async execution for low latency

✅ **Windows System Control**
- Open / close applications
- Shutdown, restart, sleep system
- Control volume, brightness, and system settings

✅ **Keyboard & Mouse Automation**
- Execute keyboard shortcuts
- Auto typing & command execution
- Mouse movement & command execution

✅ **File & Folder Management**
- Open files instantly
- Search directories
- Create, delete, rename files/folders

✅ **Persistent Memory System**
- Store user preferences
- Remember past commands
- Context-aware responses
- Memory saved locally (JSON / DB)

✅ **Live Internet & Update Tasks**
- Fetch real-time data
- Perform searches
- Check updates dynamically

✅ **ADXmug Business Intelligence**
- Independent ADXmug module; no Gigamug subscription required
- Corporate Intelligence: Indian companies, capex, orders, capacity and earnings signals
- Macro Intelligence: RBI, ministries, policy, regulation, PLI and procurement signals
- Global Intelligence: rates, trade, commodities and global business spillovers
- Signal prioritisation and impact filtering
- Industry-opportunity discovery connected to the 7DIO.EL sectoral framework
- Research/education only: no buy/sell/hold calls or price targets
- Integrated dark Command Center view inside the existing ADX GUI

✅ **Modular & Scalable Architecture**
- Skill-based system
- Easy to extend with new commands
- Clean and maintainable codebase

---

## 🧠 Example ADXmug Commands

Ask ADX:

> "ADX, अभी कौन-सी industry में opportunity है?"

> "ADXmug से India के semiconductor sector को scan करो।"

> "ADX, Corporate + Macro + Global signals देखकर 7DIO.EL analysis करो।"

For industry/sector research, ADX uses fresh configured web-search results when available and clearly separates evidence from interpretation.

---

## 🖥️ ADXmug Command Center

The existing `jarvis_ui.py` contains an integrated ADXmug mode inspired by the supplied visual reference: three intelligence cards, source/filter/impact/compliance metrics, a live activity feed, and a sector-opportunity prompt. Saying **"ADXmug खोलो"** launches this mode separately from the normal ADX interface.

The visual design is an independent ADX implementation and does not require or reproduce a paid third-party service.

---

## 🧠 Use Cases

- Personal desktop assistant
- Productivity automation
- AI system controller
- Smart command executor
- Business-intelligence research
- Sector and industry signal discovery
- Learning & experimentation with AI agents

---

## 🛠️ Tech Stack

- **Python 3.10+**
- AsyncIO
- AI APIs (Gemini / others)
- Windows Automation APIs
- Keyboard & Mouse Control Libraries
- Environment-based Configuration
- Pygame desktop UI

---

## 📂 Project Structure

ADX is organized as a modular Python desktop assistant. Key ADXmug files include:

- `adxmug.py` — Corporate/Macro/Global intelligence tools and industry scanning
- `jarvis_ui.py` — ADX + integrated ADXmug Command Center UI
- `jarvis_prompt.py` — ADXmug commands and 7DIO.EL behavior rules
- `brain.py` — ADXmug tools registered with the assistant
