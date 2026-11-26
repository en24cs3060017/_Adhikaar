from __future__ import annotations

import base64
import re
from pathlib import Path
from datetime import datetime, timezone

import streamlit as st

from data.knowledge import CYBER_TYPES, SOURCES, TOPICS, WORDS, CYBER_WORDS
from database import create_account, save_feedback, verify_account
from ai_engine import available as ai_available, ask as ask_ai
from legal_search import LOGO_URL, available as legal_api_available, query_for as legal_query_for, search as search_legal_api


st.set_page_config(page_title="ADHIKAAR | Legal Rights Guide", page_icon="⚖️", layout="wide")

st.markdown("""
<style>
.stApp { background: radial-gradient(ellipse at 50% -12%, #44311d 0%, #17100d 47%); }
.block-container { max-width: 1000px; padding-top: 3rem; padding-bottom: 3rem; }
.hero-kicker { color: #e6bd72; font-size: .75rem; letter-spacing: .2em; font-weight: 700; }
.hero-shell { min-height: 360px; display: flex; align-items: center; padding: 2.5rem; border: 1px solid #5a4228; border-radius: 20px; background-color: #17100d; background-size: auto 145%; background-position: right 38%; background-repeat: no-repeat; box-shadow: 0 18px 55px rgba(0,0,0,.28); }
.hero-copy { max-width: 560px; }
.hero-title { color: #f3d69a; font-size: clamp(2.8rem, 7vw, 4.4rem); font-weight: 750; letter-spacing: .12em; line-height: 1.1; }
.hero-tagline { color: #fff8eb; font-size: 1.1rem; margin-top: .8rem; }
.mode-card { min-height: 132px; margin: .8rem 0 .6rem; padding: 1.1rem; background: linear-gradient(145deg,#30251b,#241a14); border: 1px solid #705631; border-radius: 14px; }
.mode-card h3 { color: #f3d69a; margin: .35rem 0; }
.mode-card p { color: #cdbfa8; margin: 0; }
.card-number { color: #b08a50; font-size: .7rem; letter-spacing: .15em; }
.rule { height: 1px; background: linear-gradient(90deg, #e6bd72, #503c28, transparent); margin: 1.5rem 0; }
h1 { color: #f2d89f !important; letter-spacing: .12em; }
div[data-testid="stAlert"] { border-radius: 12px; }
div[data-testid="stForm"] { border-color: #503c28; border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

GOLD = "#e6bd72"
APP_DIR = Path(__file__).resolve().parent
HERO_PATH = APP_DIR / "assets" / "lady_justice.jpg"
HERO_IMAGE = base64.b64encode(HERO_PATH.read_bytes()).decode("ascii") if HERO_PATH.exists() else ""


def tr(en: str, hi: str, language: str) -> str:
    return hi if language == "हिन्दी" else en


def input_caution(text: str, language: str, selected_topic: str | None = None,
                  selected_scenario: str | None = None, require_scope: bool = False) -> str | None:
    if not text.strip():
        return None
    patterns = (
        (r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", "email address"),
        (r"\b[6-9]\d{9}\b", "phone number"),
        (r"\b\d{4}[ -]?\d{4}[ -]?\d{4}\b", "12-digit identity number"),
        (r"\b(?:password|passcode|otp|one.?time password|pin|cvv|card number|bank account|account number)\b|पासवर्ड|ओटीपी|पिन", "private account information"),
        (r"\b(?:my address is|house number|flat number|street address)\b|मेरा पता|घर का पता", "home address"),
    )
    for pattern, _kind in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return tr("Please remove personal or secret information and submit a general description instead. Do not include phone numbers, email addresses, ID numbers, home addresses, passwords, OTPs, bank details, or private images.", "कृपया निजी या गोपनीय जानकारी हटाकर सामान्य विवरण लिखें। फोन नंबर, ईमेल, पहचान संख्या, घर का पता, पासवर्ड, OTP, बैंक विवरण या निजी तस्वीरें न लिखें।", language)
    if re.search(r"\b(?:hack someone|steal|hurt|kill|hide evidence|destroy evidence|bribe|evade police)\b", text, flags=re.IGNORECASE):
        return tr("This guide can help with lawful rights information and safety steps. Rephrase your question around getting help, reporting an issue, or understanding official procedures.", "यह मार्गदर्शिका वैध अधिकारों और सुरक्षा के कदमों की जानकारी देती है। मदद लेने, समस्या रिपोर्ट करने या आधिकारिक प्रक्रिया समझने के बारे में प्रश्न दोबारा लिखें।", language)
    if selected_topic:
        normalized = text.casefold()
        scores = {topic: sum(1 for word in words if word.casefold() in normalized) for topic, words in WORDS.items()}
        strongest = max(scores.values(), default=0)
        if require_scope and not strongest:
            return tr("Please describe the selected legal topic using a few relevant words, such as traffic/checkpoint, police/station, arrest/custody, or cyber/account.", "कृपया चुने गए कानूनी विषय का कुछ संबंधित शब्दों में वर्णन करें, जैसे यातायात/जाँच, पुलिस/थाना, गिरफ्तारी/हिरासत या साइबर/खाता।", language)
        if strongest and scores.get(selected_topic, 0) < strongest:
            return tr("Your description seems to match a different topic than the one selected. Change the topic above and try again, or remove the optional description. The guide will not guess which topic is right.", "आपका विवरण चुने गए विषय से अलग विषय से जुड़ा लगता है। ऊपर विषय बदलें या वैकल्पिक विवरण हटाएँ। यह मार्गदर्शिका सही विषय का अनुमान नहीं लगाएगी।", language)
    if require_scope and selected_scenario and selected_scenario in SCENARIO_KEYWORDS:
        if not any(word.casefold() in text.casefold() for word in SCENARIO_KEYWORDS[selected_scenario]):
            return tr("Your description does not match the situation selected. Choose the closest situation or reword your description so it clearly matches.", "आपका विवरण चुनी गई स्थिति से मेल नहीं खाता। सबसे निकट स्थिति चुनें या विवरण को स्पष्ट रूप से उससे संबंधित करके लिखें।", language)
    return None


def description_caution(text: str, language: str, topic: str, scenario: str | None) -> str | None:
    cleaned = text.strip()
    if not cleaned:
        return tr("Describe the issue before continuing. A few general sentences help the guide check that your topic and situation match.", "आगे बढ़ने से पहले समस्या का वर्णन करें। कुछ सामान्य वाक्य लिखें ताकि मार्गदर्शिका विषय और स्थिति का मेल जाँच सके।", language)
    if len(cleaned) < 15:
        return tr("Please add a little more detail (at least 15 characters) so the guide can check the topic. Keep it general and leave out private details.", "विषय जाँचने के लिए थोड़ा और विवरण जोड़ें (कम से कम 15 अक्षर)। सामान्य जानकारी लिखें और निजी विवरण न दें।", language)
    words = re.findall(r"[A-Za-z\u0900-\u097F]+", cleaned.casefold())
    if len(words) < 3 or len(set(words)) < 3:
        return tr("Please enter a short, meaningful description instead of a single word or repeated text.", "एक शब्द या दोहराए हुए पाठ के बजाय छोटी, स्पष्ट जानकारी लिखें।", language)
    return input_caution(cleaned, language, topic, scenario, require_scope=True)


def show_auth() -> None:
    language = st.radio("Language / भाषा", ["English", "हिन्दी"], horizontal=True, key="auth_language")
    st.markdown("<div class='hero-kicker'>MADHYA PRADESH · EDUCATIONAL DEMO</div>", unsafe_allow_html=True)
    st.title(tr("ADHIKAAR · Sign in", "अधिकार · साइन इन", language))
    st.write(tr("Sign in or create an account to open the legal-rights guide.", "कानूनी जानकारी खोलने के लिए साइन इन करें या खाता बनाएँ।", language))
    st.caption(tr("The account is stored in MongoDB. Passwords are saved as salted hashes, not readable text. Your legal questions are not part of the account record.", "खाता MongoDB में सहेजा जाता है। पासवर्ड salted hash के रूप में रहते हैं, पढ़े जा सकने वाले पाठ के रूप में नहीं। आपके कानूनी प्रश्न खाते के रिकॉर्ड में नहीं रखे जाते।", language))
    sign_in, register = st.tabs([tr("Sign in", "साइन इन", language), tr("Create account", "खाता बनाएँ", language)])
    with sign_in:
        with st.form("sign_in_form"):
            email = st.text_input(tr("Email", "ईमेल", language), max_chars=254, key="login_email")
            password = st.text_input(tr("Password", "पासवर्ड", language), type="password", max_chars=128, key="login_password")
            submitted = st.form_submit_button(tr("Sign in", "साइन इन", language), type="primary", use_container_width=True)
        if submitted:
            if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email.strip()):
                st.warning(tr("Enter a valid email address.", "मान्य ईमेल पता लिखें।", language))
            elif not password:
                st.warning(tr("Enter your password.", "अपना पासवर्ड लिखें।", language))
            else:
                ok, result = verify_account(email, password)
                if ok:
                    st.session_state["authenticated_user"] = result
                    st.session_state["language"] = language
                    st.session_state.setdefault("page", "home")
                    st.rerun()
                else:
                    st.error(result)
    with register:
        with st.form("create_account_form"):
            new_email = st.text_input(tr("Email", "ईमेल", language), max_chars=254, key="register_email")
            new_password = st.text_input(tr("Create password", "पासवर्ड बनाएँ", language), type="password", max_chars=128, key="register_password")
            confirm_password = st.text_input(tr("Confirm password", "पासवर्ड की पुष्टि करें", language), type="password", max_chars=128, key="register_confirm")
            created = st.form_submit_button(tr("Create account", "खाता बनाएँ", language), type="primary", use_container_width=True)
        if created:
            if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", new_email.strip()):
                st.warning(tr("Enter a valid email address.", "मान्य ईमेल पता लिखें।", language))
            elif len(new_password) < 10:
                st.warning(tr("Use a password with at least 10 characters.", "कम से कम 10 अक्षरों का पासवर्ड रखें।", language))
            elif not re.search(r"[A-Za-z]", new_password) or not re.search(r"\d", new_password):
                st.warning(tr("Include at least one letter and one number in your password.", "पासवर्ड में कम से कम एक अक्षर और एक अंक रखें।", language))
            elif new_password != confirm_password:
                st.warning(tr("The passwords do not match. Please re-enter them.", "पासवर्ड मेल नहीं खाते। फिर से लिखें।", language))
            else:
                ok, message = create_account(new_email, new_password)
                (st.success if ok else st.error)(message)
    st.markdown("---")
    st.caption(tr("Local setup uses MongoDB at mongodb://localhost:27017. If sign-in reports that MongoDB cannot be reached, start the MongoDB Server service on your laptop.", "स्थानीय सेटअप mongodb://localhost:27017 पर MongoDB उपयोग करता है। MongoDB से संपर्क न होने का संदेश आए तो अपने लैपटॉप पर MongoDB Server सेवा शुरू करें।", language))


def detect_cyber_type(text: str) -> str | None:
    normalized = text.casefold()
    for kind, words in CYBER_WORDS.items():
        if any(word.casefold() in normalized for word in words):
            return kind
    return None


def title(topic: str, language: str) -> str:
    return TOPICS[topic][1 if language == "हिन्दी" else 0]


def source_links(indices: tuple[int, ...] | None = None) -> None:
    selected = enumerate(SOURCES) if indices is None else ((i, SOURCES[i]) for i in indices)
    for _, (label, url) in selected:
        st.markdown(f"- [{label}]({url})")


def cyber_result(kind: str, language: str) -> None:
    en = language != "हिन्दी"
    if kind == "images":
        guidance = tr(
            "Do not send more images, passwords, or OTPs. Keep the original messages, account name, content link, and dates; do not copy or forward intimate images. Report the account through the platform and the National Cyber Crime Reporting Portal. Its anonymous option is limited to certain women/child sexual-content reports. Call 112 if you are in immediate danger; 1930 is for online financial fraud.",
            "और तस्वीरें, पासवर्ड या OTP न भेजें। मूल संदेश, खाते का नाम, सामग्री का लिंक और तारीख सुरक्षित रखें; निजी तस्वीरों की कॉपी या फॉरवर्ड न करें। प्लेटफ़ॉर्म और राष्ट्रीय साइबर अपराध रिपोर्टिंग पोर्टल पर रिपोर्ट करें। इसका गुमनाम विकल्प कुछ महिला/बाल यौन-सामग्री रिपोर्ट तक सीमित है। तत्काल खतरे में 112 पर कॉल करें; 1930 ऑनलाइन वित्तीय धोखाधड़ी के लिए है।", language)
        statement = tr(
            "I am reporting a threat to share private images online. The account/platform is [details]. The threat was made on [date/time] and said [brief factual words]. The link or account involved is [details]. I have preserved relevant messages and dates. Please tell me the official next steps. I have not attached or forwarded private images in this statement.",
            "मैं निजी तस्वीरें ऑनलाइन साझा करने की धमकी की रिपोर्ट कर रहा/रही हूँ। खाता/प्लेटफ़ॉर्म [विवरण] है। धमकी [तारीख/समय] को दी गई और उसमें [संक्षिप्त तथ्य] कहा गया। संबंधित लिंक या खाता [विवरण] है। मैंने संबंधित संदेश और तारीख सुरक्षित रखी हैं। कृपया आधिकारिक अगले कदम बताएं। इस बयान के साथ मैंने निजी तस्वीरें संलग्न या आगे नहीं भेजी हैं।", language)
        refs = (2, 8, 9, 10, 14)
    elif kind == "account":
        guidance = tr(
            "Use the service’s official account-recovery page; do not use recovery links sent by strangers. If you can still sign in, set a new, unique password and turn on two-step verification. Change reused passwords elsewhere and tell contacts through another trusted method if the account is sending messages. Report the incident through the National Cyber Crime Reporting Portal. Call 112 for immediate danger.",
            "सेवा के आधिकारिक खाता-वापसी पेज का उपयोग करें; अनजान लोगों के भेजे लिंक न खोलें। यदि लॉगिन कर सकते हैं, नया और अलग पासवर्ड रखें तथा दो-चरण सत्यापन चालू करें। दूसरे खातों में यही पासवर्ड हो तो उन्हें भी बदलें। यदि खाते से आपके नाम पर संदेश जा रहे हों, तो दूसरे भरोसेमंद माध्यम से संपर्कों को बताएं। राष्ट्रीय साइबर अपराध रिपोर्टिंग पोर्टल पर रिपोर्ट करें। तत्काल खतरे में 112 पर कॉल करें।", language)
        statement = tr(
            "I am reporting unauthorised access to my online account. The service/account name is [details]. I noticed the issue on [date/time]. The changes or activity I noticed were [facts]. I have tried [official recovery steps, if any]. Please record my report and tell me the next official steps.",
            "मैं अपने ऑनलाइन खाते में अनधिकृत प्रवेश की रिपोर्ट कर रहा/रही हूँ। सेवा/खाते का नाम [विवरण] है। मुझे समस्या [तारीख/समय] को पता चली। मैंने [तथ्य] बदलाव/गतिविधि देखी। मैंने [आधिकारिक रिकवरी के कदम, यदि उठाए] आज़माए हैं। कृपया रिपोर्ट दर्ज कर अगले आधिकारिक कदम बताएं।", language)
        refs = (8, 11)
    else:
        guidance = tr(
            "Contact your bank/payment provider immediately using the official app or website and ask how to secure the affected account or payment method. Call 1930 and report the incident at the National Cyber Crime Reporting Portal. Keep the transaction reference, date, amount, messages, and complaint acknowledgement. Never share an OTP, PIN, or full password here. Call 112 if there is immediate danger.",
            "बैंक/भुगतान सेवा प्रदाता से तुरंत उसके आधिकारिक ऐप या वेबसाइट पर दिए संपर्क से बात करें और प्रभावित खाते/भुगतान माध्यम को सुरक्षित करने का तरीका पूछें। 1930 पर कॉल करें और राष्ट्रीय साइबर अपराध रिपोर्टिंग पोर्टल पर रिपोर्ट करें। लेन-देन/रेफरेंस आईडी, तारीख, राशि, संदेश और शिकायत की पावती रखें। यहाँ OTP, PIN या पूरा पासवर्ड कभी न दें। तत्काल खतरे में 112 पर कॉल करें।", language)
        statement = tr(
            "I am reporting an online financial fraud. I noticed it on [date/time]. The bank/payment app is [name]. The transaction/reference ID is [ID], the amount is [amount], and the transaction date is [date]. I contacted [bank/provider] on [date/time] using its official contact channel. Please record this report and tell me the next official steps.",
            "मैं ऑनलाइन वित्तीय धोखाधड़ी की रिपोर्ट कर रहा/रही हूँ। मुझे यह [तारीख/समय] को पता चली। बैंक/भुगतान ऐप [नाम] है। लेन-देन/रेफरेंस आईडी [आईडी], राशि [राशि] और तारीख [तारीख] है। मैंने [बैंक/सेवा प्रदाता] से [तारीख/समय] को उसके आधिकारिक माध्यम से संपर्क किया। कृपया रिपोर्ट दर्ज कर अगले आधिकारिक कदम बताएं।", language)
        refs = (8, 12)
    st.subheader(tr("Cyber safety steps", "साइबर सुरक्षा के कदम", language))
    st.info(guidance)
    st.subheader(tr("Copy-ready report statement", "कॉपी करने योग्य रिपोर्ट बयान", language))
    st.caption(tr("Fill in only accurate details. Do not attach private images.", "केवल सही जानकारी भरें। निजी तस्वीरें संलग्न न करें।", language))
    st.code(statement, language=None)
    st.markdown("**Official sources**")
    source_links(refs)


def scenario_result(scenario: str | None, language: str) -> None:
    notes = {
        "vehicle_documents": (
            "An official may check vehicle records. Whether a document is required, or whether a fine or other action applies, depends on the document, facts, state rules, and current law. This demo cannot decide that.",
            "Calmly ask what issue is being recorded. Show genuine documents you have, including official digital records where available, and request an official challan or receipt for formal action. Check the MoRTH services below. Do not pay unofficially.",
            "अधिकारी वाहन के रिकॉर्ड जाँच सकते हैं। कोई दस्तावेज़ आवश्यक है या जुर्माना/अन्य कार्रवाई लागू होती है, यह दस्तावेज़, तथ्यों, राज्य के नियम और वर्तमान कानून पर निर्भर करता है। यह नमूना इसका निर्णय नहीं कर सकता।",
            "शांत रहकर पूछें कि कौन-सी समस्या दर्ज की जा रही है। उपलब्ध वास्तविक दस्तावेज़ दिखाएँ; औपचारिक कार्रवाई पर आधिकारिक चालान या रसीद माँगें। नीचे MoRTH सेवाएँ देखें। अनौपचारिक भुगतान न करें।",
        ),
        "challan": (
            "A traffic challan or notice may depend on the recorded facts and applicable rules. This demo does not determine a violation, penalty, or deadline.",
            "Check the notice using the official MoRTH eChallan portal. Use only an official government site or app; do not follow payment links from unexpected messages. Keep the notice and payment receipt, and use the portal's official help or grievance route if details look wrong.",
            "यातायात चालान या नोटिस दर्ज तथ्यों और लागू नियमों पर निर्भर हो सकता है। यह नमूना उल्लंघन, जुर्माना या समय-सीमा तय नहीं करता।",
            "आधिकारिक MoRTH eChallan पोर्टल पर नोटिस जाँचें। केवल सरकारी वेबसाइट या ऐप का उपयोग करें; अनजान संदेशों के भुगतान लिंक न खोलें। नोटिस और भुगतान रसीद रखें। विवरण गलत लगे तो पोर्टल का आधिकारिक सहायता या शिकायत माध्यम उपयोग करें।",
        ),
        "vehicle_stop": (
            "The reason for a traffic stop and any next step depend on the circumstances and current rules. This demo cannot predict what an officer will do in a specific case.",
            "Stay calm, ask what issue is being checked, and provide accurate documents or information through official channels. Do not obstruct an official process or offer an unofficial payment. Record basic facts afterwards and seek legal-aid help if you need case-specific advice.",
            "यातायात जाँच का कारण और अगला कदम परिस्थिति तथा वर्तमान नियमों पर निर्भर करता है। यह नमूना किसी खास मामले में अधिकारी की कार्रवाई का अनुमान नहीं लगा सकता।",
            "शांत रहें, पूछें कि किस बात की जाँच हो रही है और आधिकारिक माध्यम से सही दस्तावेज़ या जानकारी दें। आधिकारिक प्रक्रिया में बाधा न डालें और अनौपचारिक भुगतान न करें। बाद में मूल तथ्य लिखें और मामले-विशेष सलाह के लिए कानूनी सहायता लें।",
        ),
        "police_question": (
            "Police interactions depend on the situation. This demo does not decide whether a request or action is lawful in a particular case.",
            "Stay calm and ask, respectfully, what the interaction concerns. Do not obstruct the process. Write down basic facts afterwards and contact a qualified lawyer or legal-aid service for advice about your situation.",
            "पुलिस से बातचीत परिस्थिति पर निर्भर करती है। यह नमूना किसी खास मामले में अनुरोध या कार्रवाई की वैधता तय नहीं करता।",
            "शांत रहें और सम्मानपूर्वक पूछें कि बातचीत किस विषय में है। प्रक्रिया में बाधा न डालें। बाद में मूल तथ्य लिखें और अपनी स्थिति पर सलाह के लिए योग्य वकील या कानूनी सहायता सेवा से संपर्क करें।",
        ),
        "police_complaint": (
            "How a complaint is recorded and handled depends on its facts and the relevant authority. This demo cannot confirm an outcome or timeline.",
            "Keep a factual copy of what you submitted and any acknowledgement or reference number. Use the official police or legal-aid channels linked below to ask about next steps.",
            "शिकायत कैसे दर्ज और संभाली जाती है, यह उसके तथ्यों और संबंधित प्राधिकरण पर निर्भर करता है। यह नमूना परिणाम या समय-सीमा की पुष्टि नहीं कर सकता।",
            "जो जमा किया उसकी तथ्यात्मक प्रति और पावती या संदर्भ संख्या रखें। अगले कदम पूछने के लिए नीचे दिए आधिकारिक पुलिस या कानूनी सहायता माध्यमों का उपयोग करें।",
        ),
        "detention": (
            "A detention or arrest is fact-specific. This demo cannot determine the legal basis or what will happen next.",
            "If safe, note where the person was taken and when. Ask for help from a qualified local lawyer or legal-aid service promptly. In immediate danger, call 112. Do not try to interfere with an official process.",
            "हिरासत या गिरफ्तारी तथ्यों पर निर्भर करती है। यह नमूना कानूनी आधार या आगे क्या होगा, इसका निर्णय नहीं कर सकता।",
            "यदि सुरक्षित हो, तो लिखें कि व्यक्ति को कहाँ और कब ले जाया गया। शीघ्र योग्य स्थानीय वकील या कानूनी सहायता सेवा से मदद लें। तत्काल खतरे में 112 पर कॉल करें। आधिकारिक प्रक्रिया में हस्तक्षेप न करें।",
        ),
        "arrest_rights": (
            "Arrest procedures depend on the facts and current law. This demo cannot assess a person's case or identify a charge.",
            "Ask a qualified lawyer or the District Legal Services Authority to explain the procedure for the specific situation. Keep a factual timeline and use the official law and legal-aid links below.",
            "गिरफ्तारी की प्रक्रिया तथ्यों और वर्तमान कानून पर निर्भर करती है। यह नमूना किसी व्यक्ति के मामले का आकलन या आरोप की पहचान नहीं करता।",
            "विशिष्ट स्थिति की प्रक्रिया समझने के लिए योग्य वकील या जिला विधिक सेवा प्राधिकरण से पूछें। घटनाक्रम लिखें और नीचे दिए आधिकारिक कानून तथा कानूनी सहायता लिंक देखें।",
        ),
    }
    if scenario not in notes:
        return
    entry = notes[scenario]
    hindi = language == "हिन्दी"
    st.subheader(tr("About this situation", "इस स्थिति के बारे में", language))
    st.markdown(f"**{tr('What may happen', 'क्या हो सकता है', language)}**  \n{entry[2] if hindi else entry[0]}")
    st.markdown(f"**{tr('Lawful next steps', 'वैध अगले कदम', language)}**  \n{entry[3] if hindi else entry[1]}")
    if scenario in ("vehicle_documents", "challan", "vehicle_stop"):
        source_links((15, 16))


def legal_reference_search(topic: str, scenario: str | None, cyber_type: str | None, language: str) -> None:
    with st.expander(tr("Search legal references (Indian Kanoon API)", "कानूनी संदर्भ खोजें (Indian Kanoon API)", language)):
        st.caption(tr("This search sends only the selected topic and situation terms—not your written description. Search results are references to review, not a decision about which law applies to you.", "इस खोज में केवल चुने गए विषय और स्थिति के शब्द भेजे जाते हैं—आपका लिखा विवरण नहीं। खोज परिणाम आगे पढ़ने के संदर्भ हैं, यह निर्णय नहीं कि कौन-सा कानून आप पर लागू होता है।", language))
        if not legal_api_available():
            st.info(tr("Add your Indian Kanoon API token in the private settings to enable this search. The guide works without it.", "यह खोज चालू करने के लिए निजी सेटिंग में Indian Kanoon API token जोड़ें। इसके बिना भी मार्गदर्शिका चलेगी।", language))
            st.markdown("[Create an API account and token](https://api.indiankanoon.org/)")
            st.code('INDIANKANOON_API_TOKEN = "your token"', language="toml")
        else:
            query = legal_query_for(scenario, cyber_type, topic)
            st.caption(tr("Search terms: ", "खोज शब्द: ", language) + query)
            with st.form("indian_kanoon_search"):
                search_clicked = st.form_submit_button(tr("Search legal documents", "कानूनी दस्तावेज़ खोजें", language), type="primary")
            if search_clicked:
                try:
                    st.session_state["indian_kanoon_results"] = search_legal_api(query)
                    st.session_state.pop("indian_kanoon_error", None)
                except Exception as error:
                    st.session_state["indian_kanoon_error"] = str(error)
            if st.session_state.get("indian_kanoon_error"):
                st.warning(st.session_state["indian_kanoon_error"])
            result_set = st.session_state.get("indian_kanoon_results")
            if result_set and result_set.get("query") == query:
                st.markdown(f'<a href="https://api.indiankanoon.org/" target="_blank" rel="noopener"><img src="{LOGO_URL}" alt="Powered by IKanoon"></a>', unsafe_allow_html=True)
                st.caption(tr("Powered by Indian Kanoon. Read the linked document in context and check its original source.", "Indian Kanoon द्वारा संचालित। जुड़े दस्तावेज़ को संदर्भ सहित पढ़ें और मूल स्रोत जाँचें।", language))
                if not result_set["results"]:
                    st.info(tr("No matching documents were returned. No results does not mean no relevant law exists.", "कोई मेल खाता दस्तावेज़ नहीं मिला। परिणाम न मिलने का अर्थ यह नहीं कि संबंधित कानून मौजूद नहीं है।", language))
                else:
                    for item in result_set["results"]:
                        st.markdown(f"**{item['title']}**")
                        if item["source"]:
                            st.caption(item["source"])
                        if item["headline"]:
                            st.text(item["headline"])
                        st.markdown(f"[Open document on Indian Kanoon]({item['url']})")


STATES_AND_UTS = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa",
    "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala",
    "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland",
    "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal", "Andaman and Nicobar Islands",
    "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Jammu and Kashmir",
    "Ladakh", "Lakshadweep", "Puducherry",
]
MP_DISTRICTS = [
    ("Agar-Malwa", "आगर मालवा"), ("Alirajpur", "अलीराजपुर"), ("Anuppur", "अनूपपुर"),
    ("Ashoknagar", "अशोकनगर"), ("Balaghat", "बालाघाट"), ("Barwani", "बड़वानी"),
    ("Betul", "बैतूल"), ("Bhind", "भिण्ड"), ("Bhopal", "भोपाल"), ("Burhanpur", "बुरहानपुर"),
    ("Chhatarpur", "छतरपुर"), ("Chhindwara", "छिंदवाड़ा"), ("Damoh", "दमोह"),
    ("Datia", "दतिया"), ("Dewas", "देवास"), ("Dhar", "धार"), ("Dindori", "डिंडौरी"),
    ("Guna", "गुना"), ("Gwalior", "ग्वालियर"), ("Harda", "हरदा"), ("Indore", "इंदौर"),
    ("Jabalpur", "जबलपुर"), ("Jhabua", "झाबुआ"), ("Katni", "कटनी"), ("Khandwa", "खंडवा"),
    ("Khargone", "खरगोन"), ("Maihar", "मैहर"), ("Mandla", "मंडला"), ("Mandsaur", "मंदसौर"),
    ("Mauganj", "मऊगंज"), ("Morena", "मुरैना"), ("Narmadapuram", "नर्मदापुरम"),
    ("Narsinghpur", "नरसिंहपुर"), ("Neemuch", "नीमच"), ("Niwari", "निवाड़ी"),
    ("Pandhurna", "पांढुरना"), ("Panna", "पन्ना"), ("Raisen", "रायसेन"),
    ("Rajgarh", "राजगढ़"), ("Ratlam", "रतलाम"), ("Rewa", "रीवा"), ("Sagar", "सागर"),
    ("Satna", "सतना"), ("Sehore", "सीहोर"), ("Seoni", "सिवनी"), ("Shahdol", "शहडोल"),
    ("Shajapur", "शाजापुर"), ("Sheopur", "श्योपुर"), ("Shivpuri", "शिवपुरी"),
    ("Sidhi", "सीधी"), ("Singrouli", "सिंगरौली"), ("Tikamgarh", "टीकमगढ़"),
    ("Ujjain", "उज्जैन"), ("Umaria", "उमरिया"), ("Vidisha", "विदिशा"),
]
MODE_CARDS = [
    ("urgent", "Urgent", "तत्काल", "Quick steps for right now", "अभी के लिए तुरंत कदम", "01"),
    ("summary", "Summarised", "संक्षिप्त", "A short, clear overview", "छोटी और स्पष्ट जानकारी", "02"),
    ("detail", "Detailed", "विस्तृत", "More context with official sources", "आधिकारिक स्रोतों के साथ विस्तार", "03"),
]
SCENARIOS = {
    "traffic": [
        ("vehicle_documents", "Missing or unavailable vehicle documents", "वाहन के कागज़ उपलब्ध न होना"),
        ("challan", "Traffic challan", "यातायात चालान"),
        ("vehicle_stop", "Stopped during a traffic check", "यातायात जाँच में रोका गया"),
        ("other_traffic", "Another traffic issue", "अन्य यातायात समस्या"),
    ],
    "police": [
        ("police_question", "Questions or interaction with police", "पुलिस के प्रश्न या बातचीत"),
        ("police_complaint", "Making or following up a complaint", "शिकायत देना या उसकी स्थिति जानना"),
        ("other_police", "Another police matter", "अन्य पुलिस मामला"),
    ],
    "arrest": [
        ("detention", "Someone is detained or arrested", "किसी को हिरासत में लिया गया है या गिरफ्तार किया गया है"),
        ("arrest_rights", "General information about arrest procedures", "गिरफ्तारी की सामान्य प्रक्रिया की जानकारी"),
        ("other_arrest", "Another detention or arrest matter", "अन्य हिरासत या गिरफ्तारी मामला"),
    ],
    "cyber": [],
}
SCENARIO_KEYWORDS = {
    "vehicle_documents": ("document", "paper", "registration", "certificate", "rc", "licence", "license", "insurance", "puc", "कागज़", "कागज", "दस्तावेज", "रजिस्ट्रेशन", "बीमा"),
    "challan": ("challan", "fine", "ticket", "notice", "e-challan", "चालान", "जुर्माना", "नोटिस"),
    "vehicle_stop": ("stopped", "stop", "checkpoint", "checking", "traffic check", "रोका", "जाँच", "जांच", "चेकिंग"),
    "police_question": ("police", "officer", "station", "thana", "asked", "question", "पुलिस", "अधिकारी", "थाना", "पूछा"),
    "police_complaint": ("complaint", "fir", "report", "complained", "शिकायत", "एफआईआर", "रिपोर्ट"),
    "other_police": ("police", "officer", "station", "thana", "पुलिस", "अधिकारी", "थाना"),
    "detention": ("detained", "arrested", "custody", "taken", "हिरासत", "गिरफ्तार", "थाने ले"),
    "arrest_rights": ("arrest", "procedure", "rights", "custody", "गिरफ्तारी", "अधिकार", "हिरासत"),
    "other_arrest": ("arrest", "detained", "custody", "गिरफ्तार", "हिरासत"),
    "images": ("photo", "image", "picture", "blackmail", "threat", "तस्वीर", "फोटो", "ब्लैकमेल", "धमकी"),
    "account": ("hacked", "hack", "account", "password", "login", "खाता", "हैक", "पासवर्ड", "लॉगिन"),
    "money": ("money", "payment", "upi", "bank", "transaction", "fraud", "scam", "पैसे", "भुगतान", "बैंक", "लेन-देन", "धोखाधड़ी", "ठगी"),
}


def show_home() -> None:
    language = st.radio("Choose your language / अपनी भाषा चुनें", ["English", "हिन्दी"], horizontal=True, key="home_language")
    hindi = language == "हिन्दी"
    st.markdown(f"""
    <section class="hero-shell" style="background-image: linear-gradient(90deg, rgba(23,16,13,.99) 0%, rgba(23,16,13,.94) 48%, rgba(23,16,13,.15) 100%), url('data:image/jpeg;base64,{HERO_IMAGE}')">
      <div class="hero-copy"><div class="hero-kicker">MADHYA PRADESH · EDUCATIONAL DEMO</div>
      <div class="hero-title">{ 'अधिकार' if hindi else 'ADHIKAAR' }</div>
      <div class="hero-tagline">{ 'अपने अधिकार जानें। जानें कि क्या करना है।' if hindi else 'Know your rights. Know what to do.' }</div></div>
    </section>
    """, unsafe_allow_html=True)
    st.markdown("<div class='rule'></div>", unsafe_allow_html=True)
    st.subheader(tr("Start with your location", "अपने स्थान से शुरू करें", language))
    st.warning(tr("Please use Madhya Pradesh for state-specific guidance. This project has not yet reviewed legal guidance for other states.", "राज्य-विशेष जानकारी के लिए कृपया केवल मध्य प्रदेश चुनें। इस परियोजना में अन्य राज्यों की कानूनी जानकारी की अभी समीक्षा नहीं हुई है।", language), icon="⚠️")
    loc1, loc2 = st.columns([1, 1])
    with loc1:
        state = st.selectbox(tr("State or Union Territory", "राज्य या केंद्र शासित प्रदेश", language), STATES_AND_UTS, index=12, key="home_state")
    region = None
    if state == "Madhya Pradesh":
        with loc2:
            districts = [None] + [name for name, _hindi in MP_DISTRICTS]
            district_labels = {name: hindi_name for name, hindi_name in MP_DISTRICTS}
            region = st.selectbox(
                tr("Choose your district", "अपना जिला चुनें", language),
                districts,
                format_func=lambda name: tr("Select a district…", "जिला चुनें…", language) if name is None else (district_labels[name] if hindi else name),
                key="home_region",
            )
            st.caption("[Official Madhya Pradesh district list](https://mpdistricts.nic.in/)")
    if state != "Madhya Pradesh":
        st.info(tr("This classroom version has reviewed guided content for Madhya Pradesh only. For other states, use the national official resources below; this demo will not apply MP guidance to your location.", "इस कक्षा संस्करण में सत्यापित निर्देशित जानकारी अभी केवल मध्य प्रदेश के लिए है। अन्य राज्यों के लिए नीचे दिए राष्ट्रीय आधिकारिक स्रोत देखें; यह नमूना MP की जानकारी को आपके राज्य पर लागू नहीं करेगा।", language))
        if st.button(tr("Continue to national resources", "राष्ट्रीय स्रोत देखें", language), type="primary"):
            st.session_state["language"] = language
            st.session_state["state"] = state
            st.session_state["page"] = "national"
            st.rerun()
    elif region is None:
        st.warning(tr("Choose your district before starting the guide.", "मार्गदर्शिका शुरू करने से पहले अपना जिला चुनें।", language), icon="⚠️")
    else:
        st.markdown(f"<div class='hero-kicker'>{tr('HOW MUCH DETAIL DO YOU NEED?', 'आपको कितनी जानकारी चाहिए?', language)}</div>", unsafe_allow_html=True)
        cards = st.columns(3, gap="medium")
        for col, (mode_key, en_title, hi_title, en_sub, hi_sub, number) in zip(cards, MODE_CARDS):
            with col:
                st.markdown(f"<div class='mode-card'><span class='card-number'>{number}</span><h3>{tr(en_title, hi_title, language)}</h3><p>{tr(en_sub, hi_sub, language)}</p></div>", unsafe_allow_html=True)
                if st.button(tr(f"Start {en_title}", f"{hi_title} शुरू करें", language), key=f"start_{mode_key}", type="primary", use_container_width=True):
                    st.session_state["mode"] = mode_key
                    st.session_state["language"] = language
                    st.session_state["state"] = state
                    st.session_state["region"] = region
                    st.session_state["page"] = "guide"
                    st.rerun()
    st.markdown("<div class='rule'></div>", unsafe_allow_html=True)
    st.markdown(f"**{tr('Emergency information', 'आपातकालीन जानकारी', language)}**  \n112 Police · 15100 Free legal aid · 1930 Cyber financial fraud")
    st.caption(tr("General educational information only — not legal advice. Do not enter names, home addresses, passwords, OTPs, bank details, or private images.", "केवल सामान्य शैक्षिक जानकारी — कानूनी सलाह नहीं। नाम, घर का पता, पासवर्ड, OTP, बैंक विवरण या निजी तस्वीरें न लिखें।", language))
    with st.expander(tr("Official resources for all states", "सभी राज्यों के आधिकारिक स्रोत", language)):
        st.markdown("- [NALSA directory of State Legal Services Authorities](https://nalsa.gov.in/directory/)\n- [India Code — official central laws](https://www.indiacode.nic.in/)\n- [National Cyber Crime Reporting Portal](https://www.cybercrime.gov.in/)")


def show_other_state(language: str) -> None:
    st.title(tr("ADHIKAAR · National resources", "अधिकार · राष्ट्रीय स्रोत", language))
    st.info(tr(f"The selected location is {st.session_state.get('state')}. This classroom version does not yet include reviewed state-specific guidance outside Madhya Pradesh.", f"चुना गया स्थान {st.session_state.get('state')} है। इस कक्षा संस्करण में मध्य प्रदेश के बाहर के राज्यों के लिए सत्यापित राज्य-विशेष जानकारी अभी उपलब्ध नहीं है।", language))
    st.markdown("### " + tr("Official resources", "आधिकारिक स्रोत", language))
    st.markdown("- [NALSA directory — find your State Legal Services Authority](https://nalsa.gov.in/directory/)\n- [India Code — official central laws](https://www.indiacode.nic.in/)\n- [National Cyber Crime Reporting Portal](https://www.cybercrime.gov.in/)")
    st.warning(tr("If someone is in immediate danger in India, call 112. Do not rely on this demo to decide which law or section applies to a case.", "भारत में तत्काल खतरे में 112 पर कॉल करें। किसी मामले पर कौन-सा कानून या धारा लागू होती है, यह तय करने के लिए इस नमूने पर निर्भर न रहें।", language))
    if st.button(tr("← Back to welcome screen", "← स्वागत स्क्रीन पर लौटें", language)):
        st.session_state["page"] = "home"
        st.rerun()


if not st.session_state.get("authenticated_user"):
    show_auth()
    st.stop()

if st.session_state.get("page", "home") == "home":
    show_home()
    st.stop()

language = st.session_state.get("language", "English")
mode = st.session_state.get("mode", "summary")
en = language == "English"
if st.session_state.get("page") == "national":
    show_other_state(language)
    st.stop()

with st.sidebar:
    st.markdown("## ADHIKAAR")
    st.caption(tr("Signed in as", "साइन इन किया है", language) + ": " + st.session_state["authenticated_user"])
    if st.button(tr("Sign out", "साइन आउट", language), use_container_width=True):
        st.session_state.pop("authenticated_user", None)
        st.session_state["page"] = "home"
        st.rerun()
    st.markdown("---")
    chosen_location = st.session_state.get("region") or st.session_state.get("state", "Madhya Pradesh")
    st.caption(tr("Location", "स्थान", language) + ": " + chosen_location)
    mode_options = {"urgent": ("Urgent", "तत्काल"), "summary": ("Summarised", "संक्षिप्त"), "detail": ("Detailed", "विस्तृत")}
    selected_mode = st.radio(tr("Answer style", "उत्तर का प्रकार", language), list(mode_options), index=list(mode_options).index(mode), format_func=lambda key: mode_options[key][1 if not en else 0])
    st.session_state["mode"] = selected_mode
    if st.session_state.get("show_result"):
        st.session_state["last_mode"] = selected_mode
    if st.button(tr("← Welcome screen", "← स्वागत स्क्रीन", language), use_container_width=True):
        st.session_state["page"] = "home"
        st.rerun()
    st.markdown("---")
    st.caption(tr("For emergencies in India, call 112. Keep personal details out of this demo.", "भारत में आपातकाल में 112 पर कॉल करें। निजी जानकारी इस नमूने में न लिखें।", language))

st.markdown(f"<div class='hero-kicker'>{st.session_state.get('state', 'Madhya Pradesh').upper()} · {tr('EDUCATIONAL DEMO', 'शैक्षिक नमूना', language)}</div>", unsafe_allow_html=True)
st.title(tr("ADHIKAAR · Legal rights guide", "अधिकार · कानूनी जानकारी", language))
st.warning(tr("This is general educational information, not legal advice. If anyone is in immediate danger, call 112.", "यह सामान्य शैक्षिक जानकारी है, कानूनी सलाह नहीं। तत्काल खतरे में 112 पर कॉल करें।", language), icon="⚠️")

st.subheader(tr("1 · Choose a topic", "1 · विषय चुनें", language))
topic_labels = {key: title(key, language) for key in TOPICS}
topic_key = st.selectbox(tr("What do you need help with?", "आपको किस विषय में मदद चाहिए?", language), list(topic_labels), format_func=lambda key: topic_labels[key])

scenario_key = None
if topic_key != "cyber":
    st.subheader(tr("2 · Choose the situation", "2 · स्थिति चुनें", language))
    scenario_options = SCENARIOS[topic_key]
    scenario_key, _scenario_en, _scenario_hi = st.selectbox(
        tr("Which situation is closest?", "कौन-सी स्थिति सबसे मिलती है?", language),
        scenario_options,
        format_func=lambda option: option[2 if not en else 1],
        key=f"scenario_{topic_key}",
    )

cyber_type = None
if topic_key == "cyber":
    st.subheader(tr("2 · Choose the cyber issue", "2 · साइबर समस्या चुनें", language))
    cyber_type = st.radio(tr("Which is closest?", "कौन-सा विकल्प सबसे मिलता है?", language), list(CYBER_TYPES), format_func=lambda key: CYBER_TYPES[key][1 if not en else 0], horizontal=True)

step_number = "3" if topic_key != "cyber" else "3"
st.subheader(tr(f"{step_number} · Describe the issue", f"{step_number} · समस्या का विवरण", language))
st.caption(tr("Enter at least 15 characters that match the selected topic and situation. Do not enter personal information. Your description is used for this response only and is not saved to MongoDB.", "चुने गए विषय और स्थिति से मेल खाते कम से कम 15 अक्षर लिखें। निजी जानकारी न लिखें। आपका विवरण केवल इस उत्तर के लिए है और MongoDB में सहेजा नहीं जाता।", language))
description = st.text_area(tr("Keep it general. Leave out names, contact details, passwords, OTPs, bank details, and private images.", "सामान्य जानकारी लिखें। नाम, संपर्क विवरण, पासवर्ड, OTP, बैंक विवरण और निजी तस्वीरें न लिखें।", language), height=110, max_chars=1200, placeholder=tr("For example: I received a traffic challan and want to know where to check it.", "उदाहरण: मुझे यातायात चालान मिला है और मैं उसे कहाँ देखूँ, यह जानना चाहता/चाहती हूँ।", language))

if st.button(tr("Show my guide", "जानकारी दिखाएँ", language), type="primary", use_container_width=True):
    selected_scenario = scenario_key if scenario_key else cyber_type
    caution = description_caution(description, language, topic_key, selected_scenario)
    if caution:
        st.session_state["show_result"] = False
        st.session_state["input_caution"] = caution
    else:
        st.session_state.pop("input_caution", None)
        st.session_state["show_result"] = True
        st.session_state["last_topic"] = topic_key
        st.session_state["last_scenario"] = scenario_key
        st.session_state["last_cyber_type"] = cyber_type
        st.session_state["last_mode"] = mode
        st.session_state["last_language"] = language
        st.session_state["last_description"] = description.strip()
        st.session_state.pop("ai_answer", None)
        st.session_state.pop("ai_error", None)
        st.session_state.pop("indian_kanoon_results", None)
        st.session_state.pop("indian_kanoon_error", None)

if st.session_state.get("input_caution"):
    st.warning(st.session_state["input_caution"], icon="⚠️")

if st.session_state.get("show_result"):
    topic_key = st.session_state.get("last_topic", topic_key)
    scenario_key = st.session_state.get("last_scenario", scenario_key)
    cyber_type = st.session_state.get("last_cyber_type", cyber_type)
    mode = st.session_state.get("last_mode", mode)
    language = st.session_state.get("last_language", language)
    description = st.session_state.get("last_description", description)
    en = language == "English"
    st.markdown("<div class='rule'></div>", unsafe_allow_html=True)
    st.subheader(tr("Your guide", "आपकी जानकारी", language))
    place = st.session_state.get("region") or st.session_state.get("state", "Madhya Pradesh")
    st.caption(tr("Selected location: ", "चुना गया स्थान: ", language) + place + (", Madhya Pradesh" if place != "Madhya Pradesh" else ""))
    if scenario_key:
        scenario_en = next((item[1] for item in SCENARIOS[topic_key] if item[0] == scenario_key), "")
        scenario_hi = next((item[2] for item in SCENARIOS[topic_key] if item[0] == scenario_key), "")
        st.markdown(f"**{tr('Situation', 'स्थिति', language)}:** {tr(scenario_en, scenario_hi, language)}")
    if description:
        st.markdown(f"**{tr('Your description', 'आपका विवरण', language)}**  \n{description}")
    scenario_result(scenario_key, language)
    if mode == "urgent":
        st.error(tr("In immediate danger? Call 112 now.", "तत्काल खतरे में? अभी 112 पर कॉल करें।" , language))
        st.markdown("1. " + tr("Move to a safer place if possible. For cyber concerns, follow the safety steps below.", "संभव हो तो सुरक्षित जगह जाएँ। साइबर समस्या में नीचे दिए सुरक्षा कदम देखें।", language))
        st.markdown("2. " + tr("This demo cannot decide which offence or legal section applies to your facts. Ask a qualified lawyer.", "यह नमूना आपके तथ्यों पर लागू अपराध या धारा तय नहीं कर सकता। योग्य वकील से पूछें।", language))
        st.markdown("3. " + tr("For legal aid call 15100. Cyber financial fraud: 1930. Women’s helpline: 181 or 1090. Child helpline: 1098.", "कानूनी सहायता: 15100। साइबर वित्तीय धोखाधड़ी: 1930। महिला हेल्पलाइन: 181 या 1090। बाल हेल्पलाइन: 1098।", language))
        source_links((0, 1, 2, 3, 4, 5))
    elif mode == "summary":
        st.markdown(f"**{tr('Situation selected', 'चुनी गई स्थिति', language)}:** {title(topic_key, language)}")
        st.markdown(f"**{tr('Legal provisions', 'कानूनी धाराएँ', language)}:** " + tr("This demo does not assign a BNS/IPC section. Ask a lawyer to review the full facts and current law.", "यह नमूना BNS/IPC की धारा तय नहीं करता। पूरे तथ्यों और वर्तमान कानून की समीक्षा वकील से कराएँ।", language))
        st.markdown(f"**{tr('Next step', 'अगला कदम', language)}:** " + tr("Write down what happened and when. Avoid sharing private details here.", "क्या हुआ और कब हुआ, लिख लें। यहाँ निजी जानकारी साझा न करें।", language))
        source_links()
    else:
        st.markdown(f"**{tr('Situation selected', 'चुनी गई स्थिति', language)}:** {title(topic_key, language)}")
        st.markdown(tr("The correct procedure depends on the facts and current law. This demo does not produce case-specific legal conclusions. Keep a factual timeline, read the official sources below, and ask a qualified lawyer how they apply.", "सही प्रक्रिया तथ्यों और वर्तमान कानून पर निर्भर करती है। यह नमूना मामले-विशेष कानूनी निष्कर्ष नहीं देता। घटनाक्रम लिखें, नीचे दिए आधिकारिक स्रोत पढ़ें और अपने मामले पर योग्य वकील से पूछें।", language))
        source_links((4, 5, 6, 7, 0, 1))
    if topic_key == "cyber" and cyber_type:
        cyber_result(cyber_type, language)
    st.markdown("---")
    st.markdown(f"**{tr('Free legal aid', 'निःशुल्क कानूनी सहायता', language)}**  \n{tr('Call 15100 or use the official MP District Legal Services Authority directory.', '15100 पर कॉल करें या आधिकारिक MP जिला विधिक सेवा प्राधिकरण निर्देशिका देखें।', language)}")
    st.markdown(f"[MP District Legal Services Authority directory]({SOURCES[1][1]})")
    st.markdown("---")
    legal_reference_search(topic_key, scenario_key, cyber_type, language)
    st.markdown("---")
    st.subheader(tr("Optional AI follow-up", "वैकल्पिक AI प्रश्न", language))
    if ai_available():
        st.caption(tr("Your follow-up question will be sent to Anthropic to generate an answer. Do not include names, addresses, passwords, OTPs, bank details, or private images. The chat is not saved to MongoDB.", "आपका आगे का प्रश्न उत्तर बनाने के लिए Anthropic को भेजा जाएगा। नाम, पता, पासवर्ड, OTP, बैंक विवरण या निजी तस्वीरें न लिखें। चैट MongoDB में सहेजी नहीं जाती।", language))
        with st.form("ai_follow_up"):
            follow_up = st.text_input(tr("Ask a general follow-up question", "सामान्य अगला प्रश्न पूछें", language), max_chars=1000)
            ask_button = st.form_submit_button(tr("Ask AI", "AI से पूछें", language))
        if ask_button and follow_up.strip():
            caution = description_caution(follow_up, language, topic_key, None)
            if caution:
                st.warning(caution, icon="⚠️")
            else:
                try:
                    st.session_state["ai_answer"] = ask_ai(follow_up.strip(), language=language, mode=mode, topic=title(topic_key, language))
                    st.session_state.pop("ai_error", None)
                except Exception:
                    st.session_state["ai_error"] = tr("The AI service did not respond. Check the API key and internet connection, or use the official links above.", "AI सेवा से उत्तर नहीं मिला। API key और इंटरनेट कनेक्शन जाँचें या ऊपर दिए आधिकारिक लिंक देखें।", language)
        if st.session_state.get("ai_answer"):
            st.markdown(st.session_state["ai_answer"])
        if st.session_state.get("ai_error"):
            st.info(st.session_state["ai_error"])
    else:
        st.caption(tr("To enable this feature, add your Anthropic API key to the private settings described in the README. The guided project works without AI.", "इस सुविधा को चालू करने के लिए README में बताए निजी सेटिंग में Anthropic API key जोड़ें। निर्देशित जानकारी AI के बिना भी चलती है।", language))

st.markdown("<div class='rule'></div>", unsafe_allow_html=True)
with st.expander(tr("About this project and feedback", "इस परियोजना और प्रतिक्रिया के बारे में", language)):
    st.write(tr("ADHIKAAR is a classroom educational demo. It does not provide legal advice, determine offences, or store chat descriptions. Official links are provided so users can check current information.", "ADHIKAAR कक्षा के लिए शैक्षिक नमूना है। यह कानूनी सलाह नहीं देता, अपराध तय नहीं करता और चैट विवरण संग्रहित नहीं करता। वर्तमान जानकारी जाँचने के लिए आधिकारिक लिंक दिए गए हैं।", language))
    st.caption(tr("Feedback is optional and anonymous. Only your rating and selected project-improvement category are saved to MongoDB; no chat text or personal details are collected.", "प्रतिक्रिया वैकल्पिक और गुमनाम है। MongoDB में केवल रेटिंग और चुनी गई सुधार श्रेणी सहेजी जाती है; चैट या निजी जानकारी नहीं।", language))
    with st.form("anonymous_feedback"):
        rating = st.select_slider(tr("How easy was this demo to use?", "इस नमूने का उपयोग कितना आसान था?", language), options=[1, 2, 3, 4, 5], value=4)
        category = st.selectbox(tr("What should be improved?", "किसमें सुधार होना चाहिए?", language), ["Language", "Clarity", "Design", "More topics", "No change"])
        submitted = st.form_submit_button(tr("Send anonymous feedback", "गुमनाम प्रतिक्रिया भेजें", language))
    if submitted:
        saved, message = save_feedback({"rating": rating, "category": category, "language": language, "mode": mode, "topic": topic_key if st.session_state.get("show_result") else None, "created_at": datetime.now(timezone.utc)})
        (st.success if saved else st.info)(message)

st.caption("ADHIKAAR · Educational information only · Official resources are listed above")
