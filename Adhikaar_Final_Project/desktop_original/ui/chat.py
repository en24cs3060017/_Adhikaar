# -*- coding: utf-8 -*-
"""Chat screen: guided flow (topic -> result -> sources) plus AI follow-up chat.
The guided flow is the original prototype code; AI hooks are ask_ai / ask_ai_instead."""
import threading
import tkinter as tk
import webbrowser
from tkinter import ttk

from config import BG, PANEL, CARD, GOLD, BROWN, BROWN_HOVER, DANGER, MUTED, FONT
from data.knowledge import (WORDS, TOPICS, SOURCES, LAST_CHECKED, CYBER_TYPES,
                            CYBER_WORDS, WORDS_DEEP)


def start_chat(app, home_screen, mode, engine):
    """Open the chat screen. `home_screen` is the front page, `engine` the AI engine."""
    is_hindi = home_screen.language.get() == "Hindi"
    mode_key = {"Urgent": "urgent", "Summarised": "summary", "Detailed": "detail"}[mode]
    mode_names = {"urgent": ("Urgent", "तत्काल"), "summary": ("Summarised", "संक्षिप्त"),
                  "detail": ("Detailed", "विस्तृत")}
    home_screen.hide()
    chat = tk.Frame(app, bg=BG)
    chat.pack(fill="both", expand=True)
    header = tk.Frame(chat, bg=PANEL)
    header.pack(fill="x")
    def go_home():
        app.unbind_all("<MouseWheel>")
        app.unbind_all("<Button-4>")
        app.unbind_all("<Button-5>")
        chat.destroy()
        home_screen.show()
    tk.Button(header, text="← वापस" if is_hindi else "← Back", command=go_home,
              bg=PANEL, fg=GOLD, relief="flat").pack(side="left", padx=14, pady=10)
    tk.Label(header, text="ADHIKAAR • सहायता चैट" if is_hindi else "ADHIKAAR • Help Chat",
             bg=PANEL, fg=GOLD, font=(FONT, 15, "bold")).pack(side="left", padx=8)
    tk.Frame(chat, bg=GOLD, height=1).pack(fill="x")
    mode_row = tk.Frame(chat, bg=PANEL)
    mode_row.pack(fill="x", padx=14, pady=(0, 8))
    area = tk.Frame(chat, bg=BG)
    area.pack(fill="both", expand=True, padx=16, pady=6)
    view = tk.Canvas(area, bg=BG, highlightthickness=0)
    scroll = ttk.Scrollbar(area, command=view.yview)
    view.configure(yscrollcommand=scroll.set)
    scroll.pack(side="right", fill="y")
    view.pack(side="left", fill="both", expand=True)
    messages = tk.Frame(view, bg=BG)
    window_id = view.create_window((0, 0), window=messages, anchor="nw")
    messages.bind("<Configure>", lambda _e: view.configure(scrollregion=view.bbox("all")))
    view.bind("<Configure>", lambda e: view.itemconfigure(window_id, width=e.width))
    def mouse_wheel(event):
        if event.delta:
            units = int(-event.delta / 120)
            view.yview_scroll(units if units else (-1 if event.delta > 0 else 1), "units")
        return "break"
    app.bind_all("<MouseWheel>", mouse_wheel)
    app.bind_all("<Button-4>", lambda _event: view.yview_scroll(-1, "units"))
    app.bind_all("<Button-5>", lambda _event: view.yview_scroll(1, "units"))
    entry_area = tk.Frame(chat, bg=PANEL)
    entry_area.pack(fill="x", padx=16, pady=10)
    entry = tk.Text(entry_area, height=2, wrap="word", font=(FONT, 11),
                    bg=CARD, fg="white", insertbackground=GOLD,
                    relief="flat", padx=10, pady=8, highlightthickness=1,
                    highlightbackground=BROWN, highlightcolor=GOLD)
    entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
    state = {"mode": mode_key, "topic": None, "cyber_type": None,
             "description": "", "last_message": "",
             "awaiting_confirm": False, "awaiting_topic": False,
             "awaiting_cyber_type": False, "awaiting_location": False,
             "pending_deep": False, "result_shown": False,
             "ai_free": False, "ai_busy": False, "ai_history": []}
    def say(en, hi):
        return hi if is_hindi else en
    def scroll_bottom():
        view.update_idletasks()
        view.yview_moveto(1)
    def scroll_to_widget(widget):
        """Show a chosen message near the top of the chat window."""
        view.update_idletasks()
        content_height = max(messages.winfo_height(), 1)
        target_y = max(widget.winfo_y() - 6, 0)
        view.yview_moveto(min(target_y / content_height, 1))
    def bubble(text, who="bot"):
        row = tk.Frame(messages, bg=BG)
        row.pack(fill="x", pady=6)
        if who == "user":
            tk.Label(row, text=text, bg=BROWN, fg="white", font=(FONT, 11),
                     justify="left", anchor="w", wraplength=620, padx=14, pady=9
                     ).pack(side="right", padx=(80, 8))
        else:
            holder = tk.Frame(row, bg=CARD)
            holder.pack(side="left", padx=(8, 80))
            tk.Frame(holder, bg=GOLD, width=4).pack(side="left", fill="y")
            tk.Label(holder, text=text, bg=CARD, fg="white", font=(FONT, 11),
                     justify="left", anchor="w", wraplength=720, padx=14, pady=10).pack(side="left")
        scroll_bottom()
        return row
    def banner(text):
        row = tk.Frame(messages, bg=BG)
        row.pack(fill="x", padx=7, pady=(10, 2))
        tk.Label(row, text=text, bg=DANGER, fg="white", font=(FONT, 12, "bold"),
                 anchor="w", padx=14, pady=8).pack(fill="x")
    def linked_source(title, url):
        row = tk.Frame(messages, bg=BG)
        row.pack(fill="x", padx=10, pady=2)
        link = tk.Label(row, text="↗ " + title, bg=BG, fg=GOLD,
                        font=(FONT, 10, "underline"), cursor="hand2", anchor="w")
        link.pack(anchor="w")
        link.bind("<Button-1>", lambda _e, address=url: webbrowser.open(address))
        link.bind("<Enter>", lambda _e, l=link: l.config(fg="white"))
        link.bind("<Leave>", lambda _e, l=link: l.config(fg=GOLD))
    def point(title, body, refs=()):
        row = tk.Frame(messages, bg=BG)
        row.pack(fill="x", pady=(13, 8))
        tk.Label(row, text=title, bg=BG, fg=GOLD,
                 font=(FONT, 12, "bold"), anchor="w").pack(fill="x", padx=7)
        card = tk.Frame(row, bg=PANEL)
        card.pack(fill="x", padx=7, pady=(4, 0))
        tk.Frame(card, bg=GOLD, width=4).pack(side="left", fill="y")
        tk.Label(card, text=body, bg=PANEL, fg="white", font=(FONT, 11),
                 justify="left", anchor="w", wraplength=880, padx=14, pady=11).pack(side="left", fill="x", expand=True)
        for source_index in refs:
            linked_source(*SOURCES[source_index])
    def button_choices(items):
        row = tk.Frame(messages, bg=BG)
        row.pack(fill="x", padx=8, pady=4)
        for text, callback in items:
            btn = tk.Button(row, text=text, command=callback, bg=BROWN, fg="white",
                            activebackground=BROWN_HOVER, activeforeground="white",
                            relief="flat", bd=0, padx=14, pady=7, cursor="hand2",
                            highlightthickness=1, highlightbackground=GOLD,
                            font=(FONT, 10, "bold"))
            btn.pack(side="left", padx=(0, 8))
            btn.bind("<Enter>", lambda _e, b=btn: b.config(bg=BROWN_HOVER))
            btn.bind("<Leave>", lambda _e, b=btn: b.config(bg=BROWN))
        scroll_bottom()
    def add_source_index(indices=None):
        bubble(say("Official sources used (click a title to open it):", "उपयोग किए गए आधिकारिक स्रोत (खोलने के लिए शीर्षक पर क्लिक करें):"))
        for index in (range(len(SOURCES)) if indices is None else indices):
            linked_source(*SOURCES[index])
        bubble(say("Last checked: " + LAST_CHECKED, "अंतिम जाँच: " + LAST_CHECKED))
    def guess_topic(text):
        low = text.lower()
        scores = {key: sum(1 for word in terms if word in low) for key, terms in WORDS.items()}
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else None
    def is_deep(text):
        low = text.lower()
        return any(term in low for term in WORDS_DEEP)
    def guess_cyber_type(text):
        low = text.lower()
        scores = {key: sum(1 for word in words if word in low)
                  for key, words in CYBER_WORDS.items()}
        best = max(scores, key=scores.get)
        return best if scores[best] else None
    def choose_cyber_type(kind):
        state["cyber_type"] = kind
        state["awaiting_cyber_type"] = False
        bubble(say("Cyber topic: ", "साइबर विषय: ") + CYBER_TYPES[kind][1 if is_hindi else 0])
        continue_after_topic()
    def ask_cyber_type():
        state["awaiting_cyber_type"] = True
        bubble(say("Which cyber issue is closest?", "कौन-सी साइबर समस्या सबसे मिलती-जुलती है?"))
        button_choices([
            (CYBER_TYPES[key][1 if is_hindi else 0], lambda selected=key: choose_cyber_type(selected))
            for key in CYBER_TYPES
        ])
    def show_mode_switch():
        state["pending_deep"] = True
        bubble(say("This sounds like you want a fuller explanation. You can change the response style below; this chat will stay here.",
                    "आपका प्रश्न विस्तार से समझाने वाला लगता है। नीचे उत्तर का प्रकार बदल सकते हैं; यह चैट यहीं रहेगी।"))
        def set_mode(new_mode):
            state["mode"] = new_mode
            state["pending_deep"] = False
            state["result_shown"] = False
            mode_label.config(text=("उत्तर: " if is_hindi else "Mode: ") + mode_names[new_mode][1 if is_hindi else 0])
            bubble(say("Changed response style. Your conversation is preserved.", "उत्तर का प्रकार बदला गया। आपकी चैट सुरक्षित है।"))
            show_result()
        button_choices([
            (say("Stay Urgent", "तत्काल में रहें"), lambda: set_mode("urgent")),
            (say("Switch to Summarised", "संक्षिप्त में बदलें"), lambda: set_mode("summary")),
            (say("Switch to Detailed", "विस्तृत में बदलें"), lambda: set_mode("detail")),
        ])
    def cyber_guidance():
        kind = state["cyber_type"] or "images"
        if kind == "images":
            advice = say(
                "• Do not send more images, passwords, or OTPs to the person threatening you.\n• Keep the original messages, account name, profile/content URL, and dates/times. Do not edit or circulate evidence; never copy, forward, or repost intimate images.\n• Report the account/content through the platform and use the National Cyber Crime Reporting Portal. Its anonymous option is limited to certain women/child sexual-content reports; do not assume every report is anonymous.\n• Call 112 if there is immediate danger. 1930 is for online financial fraud.",
                "• धमकी देने वाले को और तस्वीरें, पासवर्ड या OTP न भेजें।\n• मूल संदेश, खाते का नाम, प्रोफ़ाइल/सामग्री का URL और तारीख/समय सुरक्षित रखें। सबूत में बदलाव या प्रसार न करें; निजी तस्वीरों की कॉपी, फ़ॉरवर्ड या दोबारा पोस्ट कभी न करें।\n• प्लेटफ़ॉर्म पर खाते/सामग्री की रिपोर्ट करें और राष्ट्रीय साइबर अपराध रिपोर्टिंग पोर्टल का उपयोग करें। इसका गुमनाम विकल्प कुछ महिला/बाल यौन-सामग्री रिपोर्ट तक सीमित है; हर शिकायत गुमनाम होगी, ऐसा न मानें।\n• तत्काल खतरे में 112 पर कॉल करें। 1930 ऑनलाइन वित्तीय धोखाधड़ी के लिए है।"
            )
            refs = (2, 8, 9, 10, 14)
            statement = say(
                "I am reporting a threat to share private images online. The account/platform is [details]. The threat was made on [date/time] and said [brief factual words]. The link or account involved is [details]. I have preserved relevant messages and dates. Please tell me the official next steps. I have not attached or forwarded private images in this statement.",
                "मैं निजी तस्वीरें ऑनलाइन साझा करने की धमकी की रिपोर्ट कर रहा/रही हूँ। खाता/प्लेटफ़ॉर्म [विवरण] है। धमकी [तारीख/समय] को दी गई और उसमें [संक्षिप्त तथ्य] कहा गया। संबंधित लिंक या खाता [विवरण] है। मैंने संबंधित संदेश और तारीख सुरक्षित रखी हैं। कृपया आधिकारिक अगले कदम बताएं। इस बयान के साथ मैंने निजी तस्वीरें संलग्न या आगे नहीं भेजी हैं।"
            )
        elif kind == "account":
            advice = say(
                "• Use the service’s official account-recovery page; do not use recovery links sent by strangers.\n• If you can still sign in, change to a new, unique password and turn on two-step verification. Change any reused password on other accounts too.\n• Tell your contacts through another trusted method if the account is sending messages they did not come from you.\n• Report the incident through the National Cyber Crime Reporting Portal. Call 112 for immediate danger.",
                "• सेवा के आधिकारिक खाता-वापसी पेज का उपयोग करें; अनजान लोगों के भेजे रिकवरी लिंक न खोलें।\n• यदि अभी लॉगिन कर सकते हैं, नया और अलग पासवर्ड रखें तथा दो-चरण सत्यापन चालू करें। दूसरे खातों में यही पासवर्ड हो तो उन्हें भी बदलें।\n• यदि खाते से आपके नाम पर संदेश जा रहे हों, तो दूसरे भरोसेमंद माध्यम से संपर्कों को बताएं।\n• राष्ट्रीय साइबर अपराध रिपोर्टिंग पोर्टल पर रिपोर्ट करें। तत्काल खतरे में 112 पर कॉल करें।"
            )
            refs = (8, 11)
            statement = say(
                "I am reporting unauthorised access to my online account. The service/account name is [details]. I noticed the issue on [date/time]. The changes or activity I noticed were [facts]. I have tried [official recovery steps, if any]. Please record my report and tell me the next official steps.",
                "मैं अपने ऑनलाइन खाते में अनधिकृत प्रवेश की रिपोर्ट कर रहा/रही हूँ। सेवा/खाते का नाम [विवरण] है। मुझे समस्या [तारीख/समय] को पता चली। मैंने [तथ्य] बदलाव/गतिविधि देखी। मैंने [आधिकारिक रिकवरी के कदम, यदि उठाए] आज़माए हैं। कृपया रिपोर्ट दर्ज कर अगले आधिकारिक कदम बताएं।"
            )
        else:
            advice = say(
                "• Contact your bank/payment provider immediately using the number or support option in its official app or website; ask them how to secure the affected account or payment method.\n• Call 1930 promptly and report the incident at the National Cyber Crime Reporting Portal.\n• Keep the transaction/reference ID, date, amount, messages, and complaint acknowledgement. Never share an OTP, PIN, or full password in this chat.\n• Call 112 if there is immediate danger.",
                "• बैंक/भुगतान सेवा प्रदाता से तुरंत उसके आधिकारिक ऐप या वेबसाइट पर दिए संपर्क से बात करें; प्रभावित खाते/भुगतान माध्यम को सुरक्षित करने का तरीका पूछें।\n• शीघ्र 1930 पर कॉल करें और राष्ट्रीय साइबर अपराध रिपोर्टिंग पोर्टल पर घटना की रिपोर्ट करें।\n• लेन-देन/रेफरेंस आईडी, तारीख, राशि, संदेश और शिकायत की पावती रखें। इस चैट में OTP, PIN या पूरा पासवर्ड न दें।\n• तत्काल खतरे में 112 पर कॉल करें।"
            )
            refs = (8, 12)
            statement = say(
                "I am reporting an online financial fraud. I noticed it on [date/time]. The bank/payment app is [name]. The transaction/reference ID is [ID], the amount is [amount], and the transaction date is [date]. I contacted [bank/provider] on [date/time] using its official contact channel. Please record this report and tell me the next official steps.",
                "मैं ऑनलाइन वित्तीय धोखाधड़ी की रिपोर्ट कर रहा/रही हूँ। मुझे यह [तारीख/समय] को पता चली। बैंक/भुगतान ऐप [नाम] है। लेन-देन/रेफरेंस आईडी [आईडी], राशि [राशि] और तारीख [तारीख] है। मैंने [बैंक/सेवा प्रदाता] से [तारीख/समय] को उसके आधिकारिक माध्यम से संपर्क किया। कृपया रिपोर्ट दर्ज कर अगले आधिकारिक कदम बताएं।"
            )
        point(say("Cyber guidance — " + CYBER_TYPES[kind][0], "साइबर मार्गदर्शन — " + CYBER_TYPES[kind][1]), advice, refs)
        point(say("Copy-ready report statement (fill only true details)", "कॉपी करने योग्य रिपोर्ट बयान (सिर्फ सही जानकारी भरें)"), statement)
        def copy_statement():
            app.clipboard_clear()
            app.clipboard_append(statement)
            bubble(say("Statement copied. Fill in only accurate details.", "बयान कॉपी हुआ। केवल सही जानकारी भरें।"))
        button_choices([(say("Copy statement", "बयान कॉपी करें"), copy_statement)])
    def show_result():
        if state["result_shown"]:
            return
        state["result_shown"] = True
        answer_anchor = tk.Frame(messages, bg=BG, height=1)
        answer_anchor.pack(fill="x")
        topic = state["topic"]
        if topic is None:
            point(say("Your question", "आपका प्रश्न"), state["description"] or state["last_message"])
            point(say("Official law texts", "आधिकारिक कानून का पाठ"),
                  say("This demo does not yet explain or match IPC/BNS sections to your facts. Read the official text and ask a qualified lawyer which law applies. The IPC is the older law; BNS is the newer code, so check which applies to the date and facts of your situation.",
                      "यह नमूना अभी IPC/BNS की धाराओं को आपके तथ्यों से जोड़कर नहीं समझाता। आधिकारिक पाठ पढ़ें और योग्य वकील से पूछें कि कौन-सा कानून लागू होता है। IPC पुराना कानून है; BNS नया कानून है, इसलिए घटना की तारीख और तथ्यों के अनुसार लागू कानून जाँचें।"), (13, 4))
            point(say("Get legal help", "कानूनी सहायता लें"),
                  say("For free legal-aid information, call 15100 or use the official MP DLSA directory.",
                      "निःशुल्क कानूनी सहायता की जानकारी के लिए 15100 पर कॉल करें या आधिकारिक MP DLSA निर्देशिका देखें।"), (0, 1))
            add_source_index((13, 4, 5, 0, 1))
            state["awaiting_location"] = True
            bubble(say("For district legal-aid information, type your district/city, or type Skip. Do not send your home address.",
                        "जिला कानूनी सहायता की जानकारी के लिए जिला/शहर लिखें या Skip लिखें। घर का पता न भेजें।"))
            scroll_to_widget(answer_anchor)
            return
        topic_name = TOPICS[topic][1 if is_hindi else 0]
        if state["mode"] == "urgent":
            banner(say("In immediate danger? Call 112 now.", "तत्काल खतरे में? अभी 112 पर कॉल करें।"))
            point(say("1. Immediate steps", "1. तुरंत उठाए जाने वाले कदम"),
                  say("If anyone is in immediate danger, move to a safer place and call 112. For cyber concerns, see the safety steps below.",
                      "यदि किसी को तत्काल खतरा है, सुरक्षित जगह जाएँ और 112 पर कॉल करें। साइबर समस्या में नीचे दिए सुरक्षा कदम देखें।"), (1,))
            point(say("2. BNS / IPC information", "2. BNS / IPC की जानकारी"),
                  say("This demo cannot determine which offence or section applies to you. Have the facts and current law reviewed by a qualified lawyer; check the official law text below.",
                      "यह नमूना यह तय नहीं कर सकता कि कौन-सा अपराध या धारा आप पर लागू होगी। तथ्यों और वर्तमान कानून की समीक्षा योग्य वकील से कराएँ; आधिकारिक कानून नीचे देखें।"), (4, 5))
            point(say("3. Police actions and safeguards", "3. पुलिस की कार्रवाई और सुरक्षा"),
                  say("This demo does not decide what police may or may not do in your specific situation. The official court judgments below are references for further reading; ask a lawyer about your facts.",
                      "यह नमूना आपकी स्थिति में पुलिस क्या कर सकती है या नहीं, इसका निर्णय नहीं देता। नीचे दिए आधिकारिक अदालती फैसले आगे पढ़ने के संदर्भ हैं; अपने तथ्यों पर वकील से पूछें।"), (6, 7))
            point(say("4. Help and helplines", "4. सहायता और हेल्पलाइन"),
                  say("15100 — Free legal aid · 112 — MP police emergency · 1930 — cyber financial fraud · 181 — MP CM/women helpline · 1090 — women helpline · 1098 — child helpline. For district legal aid, see the DLSA directory.",
                      "15100 — निःशुल्क कानूनी सहायता · 112 — MP पुलिस आपातकाल · 1930 — साइबर वित्तीय धोखाधड़ी · 181 — MP CM/महिला हेल्पलाइन · 1090 — महिला हेल्पलाइन · 1098 — बाल हेल्पलाइन। जिला सहायता के लिए DLSA निर्देशिका देखें।"), (0, 1, 3))
        else:
            if state["description"]:
                point(say("Your description", "आपका विवरण"), state["description"])
            if state["mode"] == "summary":
                bubble(say("Short overview", "संक्षिप्त जानकारी"))
                point(say("Situation identified", "पहचानी गई स्थिति"), topic_name)
                point(say("Legal provisions", "कानूनी धाराएँ"),
                      say("No BNS/IPC section is assigned by this demo. A lawyer should review the full facts and current law.",
                          "यह नमूना कोई BNS/IPC धारा तय नहीं करता। पूरे तथ्यों और वर्तमान कानून की समीक्षा वकील से कराएँ।"), (4, 5))
                point(say("What to do next", "अगला कदम"),
                      say("Write down what happened and when. Avoid sharing names, addresses, passwords, OTPs, or private images here.",
                          "क्या हुआ और कब हुआ, लिख लें। यहाँ नाम, पता, पासवर्ड, OTP या निजी तस्वीरें साझा न करें।"))
            else:
                bubble(say("Detailed information", "विस्तृत जानकारी"))
                point(say("Situation identified", "पहचानी गई स्थिति"), topic_name)
                point(say("Acts and case references", "कानून और मामले के संदर्भ"),
                      say("This demo does not generate case-specific legal conclusions. Read the linked official BNS/BNSS texts and court judgments, then ask a qualified lawyer how they relate to your facts.",
                          "यह नमूना मामले-विशेष कानूनी निष्कर्ष नहीं देता। जुड़े आधिकारिक BNS/BNSS पाठ और अदालती फैसले पढ़ें, फिर अपने तथ्यों पर योग्य वकील से सलाह लें।"), (4, 5, 6, 7))
                point(say("General procedure", "सामान्य प्रक्रिया"),
                      say("The correct procedure depends on the facts and current law. Keep a factual timeline and seek legal aid for advice about your case.",
                          "सही प्रक्रिया तथ्यों और वर्तमान कानून पर निर्भर करती है। घटनाक्रम लिखें और अपने मामले की सलाह के लिए कानूनी सहायता लें।"), (0, 3))
                point(say("Basic precautions", "बुनियादी सावधानियाँ"),
                      say("Do not post private details in this demo. Use the official support links below for help.",
                          "इस नमूने में निजी जानकारी न लिखें। सहायता के लिए नीचे दिए आधिकारिक लिंक खोलें।"))
        if topic == "cyber":
            cyber_guidance()
        bubble(say("Topic detected: " + topic_name + " (keyword-based demo, not AI).",
                    "पहचाना गया विषय: " + topic_name + " (कीवर्ड आधारित नमूना, AI नहीं)।"))
        if topic == "cyber":
            add_source_index((0, 1, 2, 3, 8, 9, 10, 11, 12))
        else:
            add_source_index()
        state["awaiting_location"] = True
        bubble(say("For district legal-aid information, type your district/city, or type Skip. Do not send your home address.",
                    "जिला कानूनी सहायता की जानकारी के लिए जिला/शहर लिखें या Skip लिखें। घर का पता न भेजें।"))
        scroll_to_widget(answer_anchor)
    def handle_location(message):
        state["awaiting_location"] = False
        if message.strip().lower() not in ("skip", "छोड़ें", "छोड़े"):
            bubble(say("For “" + message + "”, use the official MP DLSA directory to find the relevant district office. This demo does not verify a lawyer’s availability.",
                        "“" + message + "” के लिए संबंधित जिला कार्यालय खोजने हेतु आधिकारिक MP DLSA निर्देशिका देखें। यह नमूना किसी वकील की उपलब्धता की पुष्टि नहीं करता।"))
            linked_source(*SOURCES[1])
        if engine.enabled:
            bubble(say("You can now ask a follow-up question. The AI assistant answers in your chosen style.",
                        "अब आप आगे का प्रश्न पूछ सकते हैं। AI सहायक आपके चुने तरीके से उत्तर देगा।"))
    def topic_buttons():
        choices = []
        for key, names in TOPICS.items():
            choices.append((names[1 if is_hindi else 0], lambda topic=key: choose_topic(topic)))
        if engine.enabled:
            choices.append((say("Ask AI instead", "AI से पूछें"), ask_ai_instead))
        button_choices(choices)
    def choose_topic(topic):
        state["topic"] = topic
        state["awaiting_topic"] = False
        bubble(say("Selected topic: ", "चुना गया विषय: ") + TOPICS[topic][1 if is_hindi else 0])
        continue_after_topic()
    def continue_after_topic():
        if state["topic"] == "cyber" and state["cyber_type"] is None:
            guess = guess_cyber_type(state["description"] or state["last_message"])
            if guess:
                state["cyber_type"] = guess
            else:
                ask_cyber_type()
                return
        if state["mode"] == "urgent" and is_deep(state["last_message"]):
            show_mode_switch()
        else:
            show_result()
    def confirm_topic(yes):
        state["awaiting_confirm"] = False
        if yes:
            continue_after_topic()
        else:
            state["topic"] = None
            state["awaiting_topic"] = True
            bubble(say("Please choose the closest topic:", "कृपया सबसे मिलता-जुलता विषय चुनें:"))
            topic_buttons()
    def process_message(message):
        if state["ai_free"]:
            state["last_message"] = message
            ask_ai(message)
            return
        if state["awaiting_location"]:
            handle_location(message)
            return
        if state["awaiting_cyber_type"]:
            subtype = guess_cyber_type(message)
            if subtype:
                choose_cyber_type(subtype)
            else:
                bubble(say("Please click one of the cyber issue buttons above.", "कृपया ऊपर दिए साइबर समस्या बटनों में से एक चुनें।"))
            return
        if state["awaiting_confirm"]:
            low = message.lower().strip()
            if low in ("yes", "y", "हाँ", "हां", "सही"):
                confirm_topic(True)
            elif low in ("no", "n", "नहीं", "गलत"):
                confirm_topic(False)
            else:
                bubble(say("Please use the Yes or Choose another buttons above.", "कृपया ऊपर दिए हाँ या दूसरा विषय चुनें बटन दबाएँ।"))
            return
        if state["awaiting_topic"]:
            found = guess_topic(message)
            if found:
                choose_topic(found)
            else:
                bubble(say("Please click one of the topic buttons above.", "कृपया ऊपर दिए विषय बटनों में से एक चुनें।"))
            return
        if state["pending_deep"]:
            bubble(say("Choose a response style using the buttons above. Your conversation is kept.",
                        "ऊपर दिए बटनों से उत्तर का प्रकार चुनें। आपकी चैट सुरक्षित है।"))
            return
        if state["topic"] is None:
            state["description"] = message
            state["last_message"] = message
            topic = guess_topic(message)
            if state["mode"] == "urgent" and is_deep(message):
                show_mode_switch()
                return
            if topic is None:
                state["awaiting_topic"] = True
                bubble(say("I could not confidently identify the topic. Choose one:",
                            "मैं विषय को भरोसे से नहीं पहचान पाया। एक विकल्प चुनें:"))
                topic_buttons()
                return
            state["topic"] = topic
            state["awaiting_confirm"] = True
            name = TOPICS[topic][1 if is_hindi else 0]
            bubble(say("I think this is about “" + name + "”. Is that right?",
                        "मुझे लगता है यह “" + name + "” से जुड़ा है। क्या यह सही है?"))
            button_choices([
                (say("Yes, continue", "हाँ, जारी रखें"), lambda: confirm_topic(True)),
                (say("Choose another", "दूसरा विषय चुनें"), lambda: confirm_topic(False)),
            ])
            return
        state["last_message"] = message
        if engine.enabled:
            ask_ai(message)
        elif state["mode"] == "urgent" and is_deep(message):
            show_mode_switch()
        else:
            bubble(say("I have kept your message in this chat. This demo does not generate new legal answers yet. You can choose Summarised or Detailed above if you want a fuller format.",
                        "आपका संदेश इसी चैट में रखा गया है। यह नमूना अभी नए कानूनी उत्तर नहीं बनाता। विस्तृत रूप चाहिए तो ऊपर संक्षिप्त या विस्तृत विकल्प चुनें।"))
    def ask_ai_instead():
        state["awaiting_topic"] = False
        state["awaiting_confirm"] = False
        state["ai_free"] = True
        bubble(say("Asking the AI assistant directly.", "AI सहायक से सीधे पूछ रहे हैं।"))
        ask_ai(state["description"] or state["last_message"])
    def ask_ai(message):
        """Send the message to the AI in a background thread; show the answer when ready."""
        if state["ai_busy"]:
            bubble(say("Please wait for the previous answer.", "कृपया पिछले उत्तर का इंतज़ार करें।"))
            return
        state["ai_busy"] = True
        thinking = bubble(say("Thinking…", "सोच रहा हूँ…"))
        topic = state["topic"]
        context = {
            "lang": "hi" if is_hindi else "en",
            "mode": state["mode"],
            "topic": TOPICS[topic][0] if topic else "",
            "cyber_type": CYBER_TYPES[state["cyber_type"]][0] if state["cyber_type"] else "",
            "description": state["description"],
        }
        history = list(state["ai_history"])
        box = {}
        def worker():
            box["out"] = engine.reply(message, context, history)
        worker_thread = threading.Thread(target=worker, daemon=True)
        worker_thread.start()
        def poll():
            if not chat.winfo_exists():          # user went back to the home screen
                return
            if worker_thread.is_alive():
                app.after(120, poll)
                return
            state["ai_busy"] = False
            thinking.destroy()
            answer, ok = box["out"]
            if ok:
                state["ai_history"] = (history + [{"role": "user", "content": message},
                                                  {"role": "assistant", "content": answer}])[-10:]
                scroll_to_widget(bubble(answer))
            else:
                bubble(say("The AI assistant could not be reached right now. Check your internet connection or API key. The guided answers and official sources above still work.",
                            "AI सहायक अभी उपलब्ध नहीं है। इंटरनेट या API कुंजी जाँचें। ऊपर दिए मार्गदर्शन और आधिकारिक स्रोत अभी भी काम करते हैं।"))
        app.after(120, poll)
    def send():
        message = entry.get("1.0", "end-1c").strip()
        if not message:
            return
        entry.delete("1.0", "end")
        bubble(message, "user")
        process_message(message)
    send_button = tk.Button(entry_area, text="भेजें" if is_hindi else "Send", command=send,
                            bg=BROWN, fg="white", font=(FONT, 11, "bold"),
                            relief="flat", padx=20)
    send_button.pack(side="right")
    send_button.config(cursor="hand2", activebackground=BROWN_HOVER, activeforeground="white")
    send_button.bind("<Enter>", lambda _e: send_button.config(bg=BROWN_HOVER))
    send_button.bind("<Leave>", lambda _e: send_button.config(bg=BROWN))
    entry.bind("<Return>", lambda event: (send(), "break"))
    mode_label = tk.Label(mode_row, text="", bg=PANEL, fg="white")
    mode_label.pack(side="left", padx=7)
    mode_label.config(text=("उत्तर: " if is_hindi else "Mode: ") + mode_names[mode_key][1 if is_hindi else 0])
    bubble(say("Please avoid names, addresses, passwords, OTPs, and private images.",
                "कृपया नाम, पता, पासवर्ड, OTP और निजी तस्वीरें न लिखें।"))
    if engine.enabled:
        bubble(say("AI assistant is on. Its answers are general information, not legal advice.",
                    "AI सहायक चालू है। इसके उत्तर सामान्य जानकारी हैं, कानूनी सलाह नहीं।"))
    prompts = {
        "urgent": ("Briefly tell me the problem.", "संक्षेप में समस्या बताएं।"),
        "summary": ("Summarise what happened in a short paragraph.", "घटना को एक छोटे पैराग्राफ में बताएं।"),
        "detail": ("Describe what happened step by step.", "घटना को क्रम से बताएं।"),
    }
    bubble(say(*prompts[mode_key]))
    entry.focus_set()
