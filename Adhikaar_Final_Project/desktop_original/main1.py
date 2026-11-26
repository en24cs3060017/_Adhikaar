"""ADHIKAAR desktop prototype.
This keeps the original 1506463.jpg home screen and adds a rule-based chat flow.
It is not connected to AI and is not a legal-advice service. Review legal content
with a qualified person before using this project outside a classroom demo.
Keep 1506463.jpg beside this file. Pillow (PIL) is required for the background.
"""
import os
import tkinter as tk
import webbrowser
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

# ---------- theme (change colours / fonts here only) ----------
BG = "#17100d"
PANEL = "#241A14"
CARD = "#30251B"
GOLD = "#F3D69A"
BROWN = "#5A4228"
BROWN_HOVER = "#795A36"
DANGER = "#B03A2E"
MUTED = "#CDBFA8"
FONT = "Segoe UI"
W, H = 1040, 585

app = tk.Tk()
app.title("Adhikaar")
app.geometry(f"{W}x{H}")
app.resizable(False, False)

style = ttk.Style(app)
try:
    style.theme_use("clam")
except tk.TclError:
    pass
style.configure("Vertical.TScrollbar", background=BROWN, troughcolor=BG, bordercolor=BG,
                arrowcolor=GOLD, lightcolor=BROWN, darkcolor=BROWN)
style.map("Vertical.TScrollbar", background=[("active", BROWN_HOVER)])
style.configure("TCombobox", fieldbackground=CARD, background=BROWN, foreground="white",
                arrowcolor=GOLD, bordercolor=GOLD, lightcolor=CARD, darkcolor=CARD)
style.map("TCombobox", fieldbackground=[("readonly", CARD)], foreground=[("readonly", "white")],
          selectbackground=[("readonly", CARD)], selectforeground=[("readonly", "white")])
app.option_add("*TCombobox*Listbox.background", CARD)
app.option_add("*TCombobox*Listbox.foreground", "white")
app.option_add("*TCombobox*Listbox.selectBackground", BROWN)
app.option_add("*TCombobox*Listbox.selectForeground", "white")

language = tk.StringVar(value="English")
labels = {}
buttons = {}
home = tk.Canvas(app, width=W, height=H, highlightthickness=0)
home.pack(fill="both", expand=True)


def rounded_rect(canvas, x1, y1, x2, y2, r=14, **kw):
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
           x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return canvas.create_polygon(pts, smooth=True, **kw)


def build_background(path, w, h):
    """Resize the photo and darken the left side and bottom so text stays readable,
    while the statue on the right is left untouched."""
    base = Image.open(path).convert("RGB").resize((w, h), Image.Resampling.LANCZOS)
    dark = Image.new("RGB", (w, h), (20, 13, 9))
    side = Image.new("L", (w, 1))
    side.putdata([int(215 * max(0.0, 1 - x / 560) ** 0.8) for x in range(w)])
    base = Image.composite(dark, base, side.resize((w, h)))
    bottom = Image.new("L", (1, h))
    bottom.putdata([int(190 * min(1.0, max(0.0, (y - (h - 110)) / 110))) for y in range(h)])
    return Image.composite(dark, base, bottom.resize((w, h)))


try:
    image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "1506463.jpg")
    photo = ImageTk.PhotoImage(build_background(image_path, W, H))
    home.create_image(0, 0, image=photo, anchor="nw")
except (OSError, AttributeError):
    photo = None
    home.configure(bg=PANEL)
    messagebox.showwarning(
        "Adhikaar",
        "1506463.jpg was not found beside main.py. The app will open with a plain background."
    )


def add_text(key, x, y, english, hindi, color, font, anchor="w"):
    item = home.create_text(x, y, text=english, fill=color, font=font, anchor=anchor)
    labels[key] = (item, english, hindi)
    return item


def change_language(_event=None):
    hindi = language.get() == "Hindi"
    app.title("अधिकार" if hindi else "Adhikaar")
    for item, english, hindi_text in labels.values():
        home.itemconfigure(item, text=hindi_text if hindi else english)
    for title, sub, en, hi, sub_en, sub_hi in buttons.values():
        home.itemconfigure(title, text=hi if hindi else en)
        home.itemconfigure(sub, text=sub_hi if hindi else sub_en)


add_text("name", 50, 105, "ADHIKAAR", "अधिकार", GOLD, (FONT, 40, "bold"))
add_text("tagline", 54, 160, "Know your rights. Know what to do.",
         "अपने अधिकार जानें। जानें कि क्या करना है।", "white", (FONT, 12))
home.create_line(54, 190, 340, 190, fill=GOLD, width=2)
add_text("language", 55, 222, "Choose your language", "अपनी भाषा चुनें", "white", (FONT, 12))
add_text("situation", 55, 295, "How much detail do you need?", "कितनी जानकारी चाहिए?",
         "white", (FONT, 14, "bold"))
add_text("helplines", 55, 518, "112 Police  ·  15100 Legal aid  ·  1930 Cyber fraud",
         "112 पुलिस  ·  15100 कानूनी सहायता  ·  1930 साइबर ठगी", GOLD, (FONT, 10, "bold"))
add_text("disclaimer", 45, 560, "General educational information only — not legal advice",
         "यह केवल सामान्य शैक्षिक जानकारी है — कानूनी सलाह नहीं", MUTED, (FONT, 9))
WORDS = {
    "traffic": ("traffic", "challan", "vehicle", "driving", "चालान", "यातायात", "गाड़ी", "वाहन"),
    "police": ("police", "officer", "station", "thana", "थाना", "पुलिस", "अधिकारी"),
    "arrest": ("arrest", "detained", "detention", "custody", "गिरफ्तार", "गिरफ्तारी", "हिरासत"),
    "cyber": ("cyber", "online", "hack", "blackmail", "photo", "fraud", "scam", "account",
              "साइबर", "ऑनलाइन", "हैक", "ब्लैकमेल", "तस्वीर", "फोटो", "धोखा", "खाता"),
}
TOPICS = {
    "traffic": ("Traffic / vehicle", "यातायात / वाहन"),
    "police": ("Police interaction", "पुलिस से बातचीत"),
    "arrest": ("Detention / arrest", "हिरासत / गिरफ्तारी"),
    "cyber": ("Cyber / online issue", "साइबर / ऑनलाइन समस्या"),
}
SOURCES = [
    ("MP State Legal Services Authority — free legal aid 15100", "https://madhyapradesh.nalsa.gov.in/contact-us/"),
    ("MP District Legal Services Authority directory", "https://madhyapradesh.nalsa.gov.in/directory/"),
    ("MP Police — emergency services and helplines", "https://dial112.mppolice.gov.in/about.php"),
    ("National Cyber Crime Reporting Portal — 1930 and online reports", "https://www.cybercrime.gov.in/"),
    ("India Code — Bharatiya Nyaya Sanhita, 2023", "https://www.indiacode.nic.in/indiacode/handle/123456789/20062?col=123456789%2F1362&view_type=search"),
    ("India Code — Bharatiya Nagarik Suraksha Sanhita, 2023", "https://www.indiacode.nic.in/indiacode/handle/123456789/20099?view_type=browse"),
    ("Supreme Court of India — D.K. Basu judgment", "https://api.sci.gov.in/supremecourt/2017/22086/22086_2017_Judgement_20-Mar-2018.pdf"),
    ("Supreme Court of India — Arnesh Kumar judgment", "https://api.sci.gov.in/supremecourt/2021/27955/27955_2021_5_1505_36261_Judgement_11-Jul-2022.pdf"),
    ("National Cyber Crime Portal — complaint FAQ", "https://www.cybercrime.gov.in/Webform/FAQ.aspx"),
    ("National Cyber Crime Portal — social-media abuse reporting", "https://cybercrime.gov.in/Webform/report_abuse_social_media.aspx"),
    ("I4C — cyber safety handbook for women and children", "https://cybercrime.gov.in/UploadMedia/TSWSW-HandbookforTacklingCyberCrimes.pdf"),
    ("I4C — Cyber Security Awareness booklet for citizens", "https://cybercrime.gov.in/pdf/Cyber%20Security%20Awareness%20Booklet%20for%20Citizens.pdf"),
    ("Reserve Bank of India — reporting unauthorised transactions", "https://www.rbi.org.in/commonman/English/scripts/Notification.aspx?Id=2623"),
    ("India Code — Indian Penal Code, 1860", "https://www.indiacode.nic.in/bitstream/123456789/11091/1/the_indian_penal_code%2C_1860.pdf"),
    ("National Cyber Crime Reporting Portal — citizen complaint manual", "https://cybercrime.gov.in/UploadMedia/MHA-CitizenManualReportOtherCyberCrime-v10.pdf"),
]
LAST_CHECKED = "15 Oct 2026"
CYBER_TYPES = {
    "images": ("Photo threats / blackmail", "तस्वीरों की धमकी / ब्लैकमेल"),
    "account": ("Hacked account", "हैक किया गया खाता"),
    "money": ("Online money fraud", "ऑनलाइन पैसों की धोखाधड़ी"),
}
CYBER_WORDS = {
    "images": ("photo", "picture", "image", "blackmail", "private image", "intimate", "leak", "publish", "तस्वीर", "फोटो", "ब्लैकमेल", "लीक", "वायरल"),
    "account": ("hacked", "hack", "account", "password", "login", "locked out", "खाता", "हैक", "पासवर्ड", "लॉगिन"),
    "money": ("money", "payment", "upi", "bank", "transaction", "scam", "fraud", "पैसे", "भुगतान", "बैंक", "लेन-देन", "धोखाधड़ी", "ठगी"),
}
WORDS_DEEP = ("history", "case law", "judgment", "explain", "explanation", "detailed", "research", "study",
              "ipc", "bns", "section", "act", "धारा", "आईपीसी", "बीएनएस", "समझाएं", "समझाइए",
              "विस्तार", "इतिहास", "फैसले", "अध्ययन", "पूरी जानकारी")
def start_chat(mode):
    is_hindi = language.get() == "Hindi"
    mode_key = {"Urgent": "urgent", "Summarised": "summary", "Detailed": "detail"}[mode]
    mode_names = {"urgent": ("Urgent", "तत्काल"), "summary": ("Summarised", "संक्षिप्त"),
                  "detail": ("Detailed", "विस्तृत")}
    home.pack_forget()
    chat = tk.Frame(app, bg=BG)
    chat.pack(fill="both", expand=True)
    header = tk.Frame(chat, bg=PANEL)
    header.pack(fill="x")
    def go_home():
        app.unbind_all("<MouseWheel>")
        app.unbind_all("<Button-4>")
        app.unbind_all("<Button-5>")
        chat.destroy()
        home.pack(fill="both", expand=True)
        change_language()
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
             "pending_deep": False, "result_shown": False}
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
    def topic_buttons():
        choices = []
        for key, names in TOPICS.items():
            choices.append((names[1 if is_hindi else 0], lambda topic=key: choose_topic(topic)))
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
        if state["mode"] == "urgent" and is_deep(message):
            show_mode_switch()
        else:
            bubble(say("I have kept your message in this chat. This demo does not generate new legal answers yet. You can choose Summarised or Detailed above if you want a fuller format.",
                        "आपका संदेश इसी चैट में रखा गया है। यह नमूना अभी नए कानूनी उत्तर नहीं बनाता। विस्तृत रूप चाहिए तो ऊपर संक्षिप्त या विस्तृत विकल्प चुनें।"))
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
    prompts = {
        "urgent": ("Briefly tell me the problem.", "संक्षेप में समस्या बताएं।"),
        "summary": ("Summarise what happened in a short paragraph.", "घटना को एक छोटे पैराग्राफ में बताएं।"),
        "detail": ("Describe what happened step by step.", "घटना को क्रम से बताएं।"),
    }
    bubble(say(*prompts[mode_key]))
    entry.focus_set()
menu = ttk.Combobox(app, textvariable=language, values=["English", "Hindi"],
                    state="readonly", width=18, font=(FONT, 10))
home.create_window(55, 252, window=menu, anchor="w")
menu.bind("<<ComboboxSelected>>", change_language)


def make_button(mode, english, hindi, sub_en, sub_hi, y):
    x1, x2, h = 55, 355, 46
    tag = "btn_" + mode
    shape = rounded_rect(home, x1, y - h // 2, x2, y + h // 2, 14,
                         fill=CARD, outline=GOLD, width=1, tags=(tag,))
    title = home.create_text(x1 + 20, y - 8, anchor="w", text=english, fill=GOLD,
                             font=(FONT, 13, "bold"), tags=(tag,))
    sub = home.create_text(x1 + 20, y + 11, anchor="w", text=sub_en, fill=MUTED,
                           font=(FONT, 9), tags=(tag,))

    def on_enter(_e):
        home.itemconfigure(shape, fill=BROWN)
        home.configure(cursor="hand2")

    def on_leave(_e):
        home.itemconfigure(shape, fill=CARD)
        home.configure(cursor="")

    home.tag_bind(tag, "<Enter>", on_enter)
    home.tag_bind(tag, "<Leave>", on_leave)
    home.tag_bind(tag, "<Button-1>", lambda _e, m=english: (on_leave(None), start_chat(m)))
    buttons[mode] = (title, sub, english, hindi, sub_en, sub_hi)


make_button("Urgent", "Urgent", "तत्काल", "Quick steps for right now", "अभी के लिए तुरंत कदम", 352)
make_button("Summarised", "Summarised", "संक्षिप्त", "Short, clear overview", "छोटी और स्पष्ट जानकारी", 407)
make_button("Detailed", "Detailed", "विस्तृत", "Full explanation with sources", "स्रोतों के साथ पूरी जानकारी", 462)
change_language()
app.mainloop()

