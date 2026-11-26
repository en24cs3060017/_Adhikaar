"""Topic labels and official reference links adapted from the original project."""

WORDS = {
    "traffic": ("traffic", "challan", "vehicle", "driving", "document", "paper", "license", "licence", "registration", "insurance", "checkpoint", "चालान", "यातायात", "गाड़ी", "वाहन", "दस्तावेज", "कागज़", "कागज", "बीमा", "लाइसेंस"),
    "police": ("police", "officer", "station", "thana", "complaint", "fir", "थाना", "पुलिस", "अधिकारी", "शिकायत", "एफआईआर"),
    "arrest": ("arrest", "detained", "detention", "custody", "गिरफ्तार", "गिरफ्तारी", "हिरासत"),
    "cyber": ("cyber", "online", "hack", "blackmail", "photo", "picture", "image", "threat", "leak", "fraud", "scam", "account", "access", "profile", "upi", "bank", "money", "payment", "साइबर", "ऑनलाइन", "हैक", "ब्लैकमेल", "तस्वीर", "फोटो", "धमकी", "लीक", "धोखा", "खाता", "बैंक", "भुगतान", "ठगी"),
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
    ("Ministry of Road Transport and Highways — eChallan portal", "https://echallan.parivahan.gov.in/"),
    ("Ministry of Road Transport and Highways — mParivahan", "https://mparivahan.parivahan.gov.in/"),
]
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
