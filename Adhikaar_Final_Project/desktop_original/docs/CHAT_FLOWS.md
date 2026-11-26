# ADHIKAAR - all chats defined

State is kept in `state{}` inside `ui/chat.py`. Language (English/Hindi) and mode come from the home screen.

| # | Chat step | Trigger | What ADHIKAAR does | Next |
|---|-----------|---------|--------------------|------|
| 1 | Home | user picks language + Urgent / Summarised / Detailed | opens chat in that mode | 2 |
| 2 | Intro | chat opens | privacy notice (no names, addresses, passwords, OTPs, private images); AI notice if a key exists; asks for the problem (short / paragraph / step by step by mode) | 3 |
| 3 | Describe problem | user types | stores description; guesses topic from keywords | 4 or 5 |
| 4 | Confirm topic | topic guessed | "I think this is about ...?" buttons: Yes, continue / Choose another | 7 or 5 |
| 5 | Choose topic | nothing matched, or "Choose another" | buttons: Traffic / Police / Detention-arrest / Cyber, plus **Ask AI instead** (only when AI is on) | 7 or 12 |
| 6 | Deep-question check | Urgent mode and words like "explain", "judgment", "IPC", "BNS", "section" | offers Stay Urgent / Switch to Summarised / Switch to Detailed; chat is kept | 8 |
| 7 | Cyber sub-type | topic = cyber and type unclear | buttons: Photo threats / Hacked account / Online money fraud | 8 |
| 8 | Result | topic known | **Urgent:** red 112 banner + 4 points (immediate steps, BNS/IPC info, police safeguards, helplines). **Summarised:** overview + provisions + next step. **Detailed:** acts and case references + procedure + precautions. Cyber adds type-specific guidance + copy-ready report statement + Copy button. Then official source links with "last checked" date | 9 |
| 9 | District legal aid | after result | asks district/city or "Skip" (no home address) and links the MP DLSA directory | 10 |
| 10 | **AI follow-up** | any message after step 9 | sends message + topic, cyber type, mode and first description to the AI; answer follows the chosen style; last 10 messages are remembered | 10 |
| 11 | No-key fallback | step 10 with no API key | original message: demo gives no new legal answers; suggests Summarised/Detailed | - |
| 12 | **AI direct chat** | "Ask AI instead" | every message goes straight to the AI | 12 |
| 13 | AI error | no internet / bad key | friendly message; guided answers and sources still work | - |
| 14 | Guards | user types while buttons are pending | gentle reminder to use the buttons above | - |
| 15 | Back | "Back" button | returns to home; running AI answer is dropped safely | 1 |

## AI rules (ai/prompts.py)
- Scope: traffic, police, detention/arrest, cyber crime, free legal aid, helplines; politely refuses the rest.
- Explains general rights in plain words; does NOT name the offence or section for the user's facts, predict outcomes, or invent sections, fees or deadlines.
- 112 first when there is danger; never asks for passwords, OTPs, bank details or private images.
- Replies in the chosen language, plain text, ends with a "general information, not legal advice" line.
