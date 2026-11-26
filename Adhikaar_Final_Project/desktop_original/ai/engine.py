# -*- coding: utf-8 -*-
"""AI engine: sends the chat to the Claude API. Never raises - returns (text, ok)."""
import json
import urllib.request

import config
from ai.prompts import system_prompt


class Engine:
    def __init__(self):
        self.last_error = ""

    @property
    def enabled(self):
        """True when an API key is available."""
        return bool(config.API_KEY)

    def reply(self, message, context, history):
        try:
            return self._ask(message, context, history), True
        except Exception as exc:                 # no internet, bad key, rate limit ...
            self.last_error = str(exc)
            return "", False

    def _ask(self, message, context, history):
        body = json.dumps({
            "model": config.MODEL,
            "max_tokens": config.MAX_TOKENS,
            "system": system_prompt(context),
            "messages": list(history[-8:]) + [{"role": "user", "content": message}],
        }).encode("utf-8")
        req = urllib.request.Request(
            config.API_URL, data=body,
            headers={"content-type": "application/json",
                     "x-api-key": config.API_KEY,
                     "anthropic-version": "2023-06-01"})
        with urllib.request.urlopen(req, timeout=config.TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text").strip()
        if not text:
            raise RuntimeError("empty AI reply")
        return text
