"""Optional Anthropic follow-up, carried over from the desktop project's AI feature."""

import json
import os
import urllib.request

import streamlit as st


def _setting(name: str, default: str = "") -> str:
    try:
        return str(st.secrets.get(name, os.getenv(name, default))).strip()
    except Exception:
        return os.getenv(name, default).strip()


def available() -> bool:
    return bool(_setting("ANTHROPIC_API_KEY"))


def ask(question: str, *, language: str, mode: str, topic: str) -> str:
    api_key = _setting("ANTHROPIC_API_KEY")
    model = _setting("ANTHROPIC_MODEL", "claude-sonnet-5-5")
    if not api_key:
        raise RuntimeError("AI follow-up is not configured.")
    style = {
        "urgent": "Use at most five very short steps. Put Call 112 first if there is danger.",
        "summary": "Use one short paragraph and one useful next step.",
        "detail": "Use short sections for general rights, steps, help, and evidence.",
    }.get(mode, "Use a short, clear answer.")
    system = f"""You are ADHIKAAR, a legal-rights information assistant for ordinary people in Madhya Pradesh, India. You provide general educational information, not legal advice. Stay within traffic and vehicle stops, police, detention and arrest, cybercrime, free legal aid, and helplines. Answer in {language}. {style}
Do not decide which offence or law applies to a person's exact facts, predict what a court or police will do, or invent legal provisions, fees, or deadlines. Say when a qualified lawyer should confirm. Put immediate safety first; mention 112 for danger, 15100 for free legal aid, and 1930 for online financial fraud when relevant. Never ask for passwords, OTPs, bank details, or private images. Do not repeat private details if the user includes them. End with: General information only, not legal advice."""
    payload = json.dumps({
        "model": model,
        "max_tokens": 900,
        "system": system + f"\nSelected topic: {topic}.",
        "messages": [{"role": "user", "content": question}],
    }).encode("utf-8")
    request = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={"content-type": "application/json", "x-api-key": api_key, "anthropic-version": "2023-06-01"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=40) as response:
        result = json.loads(response.read().decode("utf-8"))
    answer = "\n".join(block.get("text", "") for block in result.get("content", []) if block.get("type") == "text").strip()
    if not answer:
        raise RuntimeError("The AI did not return an answer.")
    return answer
