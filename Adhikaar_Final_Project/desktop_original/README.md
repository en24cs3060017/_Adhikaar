# ADHIKAAR - MP Legal Rights Emergency Information System

Windows desktop app (Python + Tkinter) for Madhya Pradesh. English and Hindi.
Home screen with 3 answer styles (Urgent / Summarised / Detailed) -> guided chat -> AI follow-up chat.

## Setup
1. Install Python 3.10+ (tick "Add Python to PATH").
2. `pip install -r requirements.txt`
3. Copy your photo `1506463.jpg` into the `assets` folder.
4. (For AI) get an API key and either run `setx ANTHROPIC_API_KEY "your-key"` (then reopen the terminal)
   or save the key alone in a file `api_key.txt` in this folder.
5. `python main.py`

Without a key the app still works exactly like the original guided demo (AI is simply off).

## Project structure
```
main.py            starts the app
config.py          colours, fonts, window size, AI settings
data/knowledge.py  keywords, topics, official sources (from the original prototype)
ui/theme.py        ttk styling
ui/home.py         front page (unchanged design)
ui/chat.py         guided chat flow + AI hooks (ask_ai, ask_ai_instead)
ai/prompts.py      system prompt (scope, safety rules, helplines, source titles)
ai/engine.py       Claude API call; returns (text, ok), never crashes the UI
docs/CHAT_FLOWS.md every chat state defined
```

## Disclaimer
General educational information only - not legal advice. Have the legal content reviewed by a
qualified person before using it outside a classroom demo.
