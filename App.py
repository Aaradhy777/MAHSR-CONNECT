import streamlit as st
import urllib.parse
import random
import os
from groq import Groq

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="MAHSR Connect | Mumbai–Ahmedabad Bullet Train",
    page_icon="🚄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM HIGH-CONTRAST CSS ---
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #001f3f 0%, #004080 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        border-bottom: 4px solid #FF851B;
    }
    .manual-box {
        background-color: #f0f4f8;
        border-left: 5px solid #004080;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        color: #111111;
    }
    .ticket-card {
        background: #ffffff;
        border: 2px solid #001f3f;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        color: #111111;
    }
    .wayfinding-box {
        background-color: #e6fffa;
        border-left: 5px solid #008080;
        padding: 15px;
        border-radius: 8px;
        margin-top: 15px;
        color: #111111;
    }
    </style>
""", unsafe_allow_html=True)

# --- QUAD-LANGUAGE DICTIONARY (EN / HI / MR / GU) ---
LANG = {
    "English": {
        "title": "MAHSR Connect — High-Speed Rail Portal",
        "subtitle": "Mumbai (BKC) ↔ Ahmedabad (Sabarmati) | 508 km Corridor",
        "manual_title": "📘 Quick Start User Manual (How to Book)",
        "manual_steps": [
            "**Step 1 (Verify):** Enter your Full Name and 10-digit Mobile Number to unlock booking.",
            "**Step 2 (Train):** Choose your departure, destination, travel date, and preferred bullet train.",
            "**Step 3 (Seat):** Pick your coach class (Standard 3x2 or Business 2x2) and click an available seat.",
            "**Step 4 (Board):** Download/scan your Digital QR E-Boarding Pass and follow the live terminal guide."
        ],
        "step1_header": "Step 1: Passenger Verification",
        "name_label": "Full Name *",
        "phone_label": "10-Digit Mobile Number *",
        "start_btn": "Proceed to Train Selection ➔",
        "err_missing": "⚠️ Please enter both your Full Name and a valid 10-digit Mobile Number to continue.",
        "step2_header": "Step 2: Select Route & Bullet Train",
        "from_label": "From Station",
        "to_label": "To Station",
        "date_label": "Journey Date",
        "select_train": "Select Train",
        "next_seat_btn": "Proceed to Seat Selection ➔",
        "back_btn": "⬅ Back",
        "step3_header": "Step 3: Interactive Coach Seat Matrix",
        "class_label": "Select Coach Class",
        "std_class": "Standard Class (3x2 Layout) - ₹3,000",
        "bus_class": "Business Class (2x2 Layout) - ₹5,500",
        "selected_seat": "Selected Seat:",
        "confirm_btn": "Confirm Booking & Generate QR Pass ✅",
        "err_seat": "⚠️ Please click on a seat from the grid before confirming.",
        "step4_header": "Step 4: Digital E-Boarding Pass & Terminal Wayfinding",
        "pnr": "PNR Number",
        "passenger": "Passenger",
        "mobile": "Mobile",
        "route": "Route",
        "seat": "Coach & Seat",
        "wayfinding_title": "🧭 Live Terminal Wayfinding Guide",
        "wayfinding_text": "Enter via **Gate 3 (Express Biometric Lane)** ➔ Take Escalator B down to **Concourse Level -1** ➔ Scan QR at **Turnstile 04** ➔ Proceed to **Platform 2 (Coach C1)**.",
        "new_booking": "Book Another Ticket 🔄",
        "ai_title": "🤖 MAHSR AI Travel Assistant",
        "ai_welcome": "Hello! I am your live Gemini AI assistant. Ask me anything about train timings, fares, or your trip.",
        "ai_placeholder": "Ask a question about your trip..."
    },
    "हिंदी (Hindi)": {
        "title": "MAHSR कनेक्ट — हाई-स्पीड रेल पोर्टल",
        "subtitle": "मुंबई (BKC) ↔ अहमदाबाद (साबरमती) | 508 किमी कॉरिडोर",
        "manual_title": "📘 त्वरित उपयोगकर्ता पुस्तिका (बुकिंग कैसे करें)",
        "manual_steps": [
            "**चरण 1 (सत्यापन):** बुकिंग शुरू करने के लिए अपना पूरा नाम और 10-अंकीय मोबाइल नंबर दर्ज करें।",
            "**चरण 2 (ट्रेन):** अपना प्रस्थान, गंतव्य, यात्रा तिथि और पसंदीदा बुलेट ट्रेन चुनें।",
            "**चरण 3 (सीट):** कोच श्रेणी (स्टैंडर्ड या बिज़नेस) चुनें और उपलब्ध सीट पर क्लिक करें।",
            "**चरण 4 (बोर्डिंग):** अपना डिजिटल QR ई-बोर्डिंग पास प्राप्त करें और टर्मिनल गाइड का पालन करें।"
        ],
        "step1_header": "चरण 1: यात्री सत्यापन",
        "name_label": "पूरा नाम *",
        "phone_label": "10-अंकीय मोबाइल नंबर *",
        "start_btn": "ट्रेन चयन पर आगे बढ़ें ➔",
        "err_missing": "⚠️ आगे बढ़ने के लिए कृपया अपना पूरा नाम और 10-अंकीय मोबाइल नंबर दोनों दर्ज करें।",
        "step2_header": "चरण 2: मार्ग और बुलेट ट्रेन चुनें",
        "from_label": "प्रस्थान स्टेशन",
        "to_label": "गंतव्य स्टेशन",
        "date_label": "यात्रा की तिथि",
        "select_train": "ट्रेन चुनें",
        "next_seat_btn": "सीट चयन पर आगे बढ़ें ➔",
        "back_btn": "⬅ पीछे",
        "step3_header": "चरण 3: इंटरैक्टिव कोच सीट मैट्रिक्स",
        "class_label": "कोच श्रेणी चुनें",
        "std_class": "स्टैंडर्ड क्लास (3x2 लेआउट) - ₹3,000",
        "bus_class": "बिज़नेस क्लास (2x2 लेआउट) - ₹5,500",
        "selected_seat": "चयनित सीट:",
        "confirm_btn": "बुकिंग कन्फर्म करें और QR पास बनाएं ✅",
        "err_seat": "⚠️ कृपया पुष्टि करने से पहले ग्रिड से एक सीट चुनें।",
        "step4_header": "चरण 4: डिजिटल ई-बोर्डिंग पास और टर्मिनल मार्गदर्शिका",
        "pnr": "PNR नंबर",
        "passenger": "यात्री",
        "mobile": "मोबाइल",
        "route": "मार्ग",
        "seat": "कोच और सीट",
        "wayfinding_title": "🧭 लाइव टर्मिनल वेफ़ाइंडिंग गाइड",
        "wayfinding_text": "**गेट 3 (एक्सप्रेस लेन)** से प्रवेश करें ➔ एस्केलेटर B से **कॉनकोर्स लेवल -1** पर जाएं ➔ **टर्नस्टाइल 04** पर QR स्कैन करें ➔ **प्लेटफ़ॉर्म 2 (कोच C1)** पर जाएं।",
        "new_booking": "दूसरा टिकट बुक करें 🔄",
        "ai_title": "🤖 MAHSR AI यात्रा सहायक",
        "ai_welcome": "नमस्ते! मैं आपका लाइव जेमिनी AI सहायक हूँ। ट्रेन के समय, किराए या यात्रा के बारे में कुछ भी पूछें।",
        "ai_placeholder": "अपनी यात्रा के बारे में पूछें..."
    },
    "मराठी (Marathi)": {
        "title": "MAHSR कनेक्ट — हाय-स्पीड रेल पोर्टल",
        "subtitle": "मुंबई (BKC) ↔ अहमदाबाद (साबरमती) | 508 किमी कॉरिडॉर",
        "manual_title": "📘 जलद वापरकर्ता पुस्तिका (तिकीट कसे बुक करावे)",
        "manual_steps": [
            "**पायरी 1 (पडताळणी):** बुकिंग सुरू करण्यासाठी तुमचे पूर्ण नाव आणि 10-अंकी मोबाईल नंबर टाका.",
            "**पायरी 2 (ट्रेन):** तुमचे प्रस्थान, गंतव्यस्थान, प्रवासाची तारीख आणि पसंतीची बुलेट ट्रेन निवडा.",
            "**पायरी 3 (सीट):** कोच प्रकार (स्टँडर्ड किंवा बिझनेस) निवडा आणि उपलब्ध सीटवर क्लिक करा.",
            "**पायरी 4 (बोर्डिंग):** तुमचा डिजिटल QR ई-बोर्डिंग पास मिळवा आणि टर्मिनल मार्गदर्शकाचे पालन करा."
        ],
        "step1_header": "पायरी 1: प्रवासी पडताळणी",
        "name_label": "पूर्ण नाव *",
        "phone_label": "10-अंकी मोबाईल नंबर *",
        "start_btn": "ट्रेन निवडीकडे पुढे जा ➔",
        "err_missing": "⚠️ पुढे जाण्यासाठी कृपया तुमचे पूर्ण नाव आणि 10-अंकी मोबाईल नंबर दोन्ही टाका.",
        "step2_header": "पायरी 2: मार्ग आणि बुलेट ट्रेन निवडा",
        "from_label": "प्रस्थान स्थानक",
        "to_label": "गंतव्य स्थानक",
        "date_label": "प्रवासाची तारीख",
        "select_train": "ट्रेन निवडा",
        "next_seat_btn": "सीट निवडीकडे पुढे जा ➔",
        "back_btn": "⬅ मागे",
        "step3_header": "पायरी 3: इंटरॅक्टिव्ह कोच सीट मॅट्रिक्स",
        "class_label": "कोच प्रकार निवडा",
        "std_class": "स्टँडर्ड क्लास (3x2 लेआउट) - ₹3,000",
        "bus_class": "बिझनेस क्लास (2x2 लेआउट) - ₹5,500",
        "selected_seat": "निवडलेली सीट:",
        "confirm_btn": "बुकिंग निश्चित करा आणि QR पास तयार करा ✅",
        "err_seat": "⚠️ कृपया निश्चित करण्यापूर्वी ग्रीडमधून एक सीट निवडा.",
        "step4_header": "पायरी 4: डिजिटल ई-बोर्डिंग पास आणि टर्मिनल मार्गदर्शक",
        "pnr": "PNR क्रमांक",
        "passenger": "प्रवासी",
        "mobile": "मोबाईल",
        "route": "मार्ग",
        "seat": "कोच आणि सीट",
        "wayfinding_title": "🧭 लाइव्ह टर्मिनल वेफाइंडिंग गाईड",
        "wayfinding_text": "**गेट 3 (एक्स्प्रेस लेन)** मधून प्रवेश करा ➔ एस्कलेटर B ने **कॉनकोर्स लेव्हल -1** वर जा ➔ **टर्नस्टाइल 04** वर QR स्कॅन करा ➔ **प्लॅटफॉर्म 2 (कोच C1)** वर जा.",
        "new_booking": "दुसरे तिकीट बुक करें 🔄",
        "ai_title": "🤖 MAHSR AI प्रवास सहाय्यक",
        "ai_welcome": "नमस्कार! मी तुमचा लाइव्ह जेमिनी AI सहाय्यक आहे. ट्रेनच्या वेळा, भाडे किंवा प्रवासाविषयी काहीही विचार.",
        "ai_placeholder": "तुमच्या प्रवासाबद्दल प्रश्न विचार..."
    },
    "ગુજરાતી (Gujarati)": {
        "title": "MAHSR કનેક્ટ — હાઈ-સ્પીડ રેલ પોર્ટલ",
        "subtitle": "મુંબઈ (BKC) ↔ અમદાવાદ (સાબરમતી) | 508 કિમી કોરિડોર",
        "manual_title": "📘 ક્વિક સ્ટાર્ટ યુઝર મેન્યુઅલ (ટિકિટ કેવી રીતે બુક કરવી)",
        "manual_steps": [
            "**પગલું 1 (ચકાસણી):** બુકિંગ શરૂ કરવા માટે તમારું પૂરું નામ અને 10-અંકનો મોબાઇલ નંબર દાખલ કરો.",
            "**પગલું 2 (ટ્રેન):** તમારું પ્રસ્થાન, ગંતવ્ય, મુસાફરીની તારીખ અને પસંદગીની બુલેટ ટ્રેન પસંદ કરો.",
            "**પગલું 3 (સીટ):** કોચ ક્લાસ (સ્ટાન્ડર્ડ અથવા બિઝનેસ) પસંદ કરો અને ઉપલબ્ધ સીટ પર ક્લિક કરો.",
            "**પગલું 4 (બોર્ડિંગ):** તમારો ડિજિટલ QR ઈ-બોર્ડિંગ પાસ મેળવો અને ટર્મિનલ ગાઈડને અનુસરો."
        ],
        "step1_header": "પગલું 1: મુસાફરની ચકાસણી",
        "name_label": "પૂરું નામ *",
        "phone_label": "10-અંકનો મોબાઇલ નંબર *",
        "start_btn": "ટ્રેન પસંદગી પર આગળ વધો ➔",
        "err_missing": "⚠️ આગળ વધવા માટે કૃપા કરીને તમારું પૂરું નામ અને 10-અંકનો મોબાઇલ નંબર બંને દાખલ કરો.",
        "step2_header": "પગલું 2: રૂટ અને બુલેટ ટ્રેન પસંદ કરો",
        "from_label": "પ્રસ્થાન સ્ટેશન",
        "to_label": "ગંતવ્ય સ્ટેશન",
        "date_label": "મુસાફરીની તારીખ",
        "select_train": "ટ્રેન પસંદ કરો",
        "next_seat_btn": "સીટ પસંદગી પર આગળ વધો ➔",
        "back_btn": "⬅ પાછળ",
        "step3_header": "પગલું 3: ઇન્ટરેક્ટિવ કોચ સીટ મેટ્રિક્સ",
        "class_label": "કોચ ક્લાસ પસંદ કરો",
        "std_class": "સ્ટાન્ડર્ડ ક્લાસ (3x2 લેઆઉટ) - ₹3,000",
        "bus_class": "બિઝનેસ ક્લાસ (2x2 લેઆઉટ) - ₹5,500",
        "selected_seat": "પસંદ કરેલ સીટ:",
        "confirm_btn": "બુકિંગ કન્ફર્મ કરો અને QR પાસ બનાવો ✅",
        "err_seat": "⚠️ કૃપા કરીને કન્ફર્મ કરતા પહેલા ગ્રીડમાંથી એક સીટ પસંદ કરો.",
        "step4_header": "પગલું 4: ડિજિટલ ઈ-બોર્ડિંગ પાસ અને ટર્મિનલ માર્ગદર્શિકા",
        "pnr": "PNR નંબર",
        "passenger": "મુસાફર",
        "mobile": "મોબાઇલ",
        "route": "રૂટ",
        "seat": "કોચ અને સીટ",
        "wayfinding_title": "🧭 લાઇવ ટર્મિનલ વેફાઇન્ડિંગ ગાઈડ",
        "wayfinding_text": "**ગેટ 3 (એક્સપ્રેસ લેન)** થી પ્રવેશ કરો ➔ એસ્કેલેટર B દ્વારા **કોનકોર્સ લેવલ -1** પર જાઓ ➔ **ટર્નસ્ટાઇલ 04** પર QR સ્કેન કરો ➔ **પ્લેટફોર્મ 2 (કોચ C1)** પર જાઓ.",
        "new_booking": "બીજી ટિકિટ બુક કરો 🔄",
        "ai_title": "🤖 MAHSR AI ટ્રાવેલ આસિસ્ટન્ટ",
        "ai_welcome": "નમસ્તે! હું તમારો લાઇવ જેમિની AI આસિસ્ટન્ટ છું. ટ્રેનના સમય, ભાડા અથવા તમારી સફર વિશે કંઈપણ પૂછો.",
        "ai_placeholder": "તમારી મુસાફરી વિશે પૂછો..."
    }
}

# --- INITIALIZE SESSION STATE ---
if "step" not in st.session_state:
    st.session_state.step = 1
if "passenger_name" not in st.session_state:
    st.session_state.passenger_name = ""
if "passenger_phone" not in st.session_state:
    st.session_state.passenger_phone = ""
if "selected_seat" not in st.session_state:
    st.session_state.selected_seat = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "pnr" not in st.session_state:
    st.session_state.pnr = f"MAHSR-{random.randint(1000, 9999)}"

# --- TOP LANGUAGE BAR ---
col_spacer, col_lang = st.columns([3, 1])
with col_lang:
    selected_lang = st.selectbox(
        "🌐 Language / भाषा / भाषा / ભાષા",
        list(LANG.keys()),
        index=0
    )

T = LANG[selected_lang]

# --- SIDEBAR: LIVE GROQ AI ASSISTANT ---
with st.sidebar:
    st.markdown(f"### {T['ai_title']}")
    st.info(T["ai_welcome"])

    # Load Groq API key safely from Streamlit Secrets or environment
    api_key = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", ""))

    if st.session_state.passenger_name:
        st.caption(f"👤 Active User: **{st.session_state.passenger_name}** ({st.session_state.passenger_phone})")

    for sender, msg in st.session_state.chat_history:
        with st.chat_message(sender):
            st.markdown(msg)

    user_q = st.chat_input(T["ai_placeholder"])
    if user_q:
        st.session_state.chat_history.append(("user", user_q))
        with st.chat_message("user"):
            st.markdown(user_q)

        if not api_key:
            reply = "⚠️ Please add `GROQ_API_KEY` in Streamlit Secrets to activate live AI."
        else:
            try:
                client = Groq(api_key=api_key)
                
                system_context = (
                    f"You are the official MAHSR Connect AI Travel Assistant for the Mumbai–Ahmedabad High-Speed Rail (Bullet Train). "
                    f"Reply strictly in {selected_lang}. Keep answers helpful, concise (2-3 sentences), and accurate. "
                    f"Key facts: 508 km route, 12 stations (Mumbai BKC, Thane, Virar, Boisar, Vapi, Bilimora, Surat, Bharuch, Vadodara, Anand, Ahmedabad, Sabarmati), "
                    f"max speed 320 km/h (~2h 07m travel time), Standard Class ₹3,000, Business Class ₹5,500, baggage limit 20kg check-in + 7kg cabin. "
                    f"Current passenger: {st.session_state.passenger_name or 'Guest'}, "
                    f"Route: {st.session_state.get('from_stn', 'Not selected')} to {st.session_state.get('to_stn', 'Not selected')}, "
                    f"Seat: {st.session_state.selected_seat or 'Not selected'}."
                )

                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_context},
                        {"role": "user", "content": user_q}
                    ],
                    model="openai/gpt-oss-120b",
                )
                reply = chat_completion.choices[0].message.content
            except Exception as e:
                reply = f"⚠️ AI connection error: {e}"

        st.session_state.chat_history.append(("assistant", reply))
        with st.chat_message("assistant"):
            st.markdown(reply)

# --- MAIN HEADER ---
st.markdown(f"""
    <div class="main-header">
        <h1>🚄 {T['title']}</h1>
        <p style="font-size: 1.1rem; margin: 0;">{T['subtitle']}</p>
    </div>
""", unsafe_allow_html=True)

# --- STARTING USER MANUAL ---
with st.expander(T["manual_title"], expanded=(st.session_state.step == 1)):
    st.markdown('<div class="manual-box">', unsafe_allow_html=True)
    for step_text in T["manual_steps"]:
        st.markdown(f"- {step_text}")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# STEP 1: MANDATORY NAME & PHONE NUMBER GATE
# ==========================================
if st.session_state.step == 1:
    st.subheader(T["step1_header"])
    
    col1, col2 = st.columns(2)
    with col1:
        name_input = st.text_input(T["name_label"], value=st.session_state.passenger_name, placeholder="e.g., Aarav Patel")
    with col2:
        phone_input = st.text_input(T["phone_label"], value=st.session_state.passenger_phone, max_chars=10, placeholder="e.g., 9876543210")

    if st.button(T["start_btn"], type="primary"):
        clean_name = name_input.strip()
        clean_phone = phone_input.strip()
        
        if len(clean_name) > 0 and clean_phone.isdigit() and len(clean_phone) == 10:
            st.session_state.passenger_name = clean_name
            st.session_state.passenger_phone = clean_phone
            st.session_state.step = 2
            st.rerun()
        else:
            st.error(T["err_missing"])

# ==========================================
# STEP 2: ROUTE & TRAIN SELECTION
# ==========================================
elif st.session_state.step == 2:
    st.subheader(T["step2_header"])
    st.success(f"👤 {st.session_state.passenger_name} | 📞 +91-{st.session_state.passenger_phone}")

    stations = [
        "Mumbai (BKC)", "Thane", "Virar", "Boisar", "Vapi",
        "Bilimora", "Surat", "Bharuch", "Vadodara", "Anand",
        "Ahmedabad", "Sabarmati"
    ]

    c1, c2, c3 = st.columns(3)
    with c1:
        from_stn = st.selectbox(T["from_label"], stations, index=0)
    with c2:
        to_stn = st.selectbox(T["to_label"], stations, index=10)
    with c3:
        travel_date = st.date_input(T["date_label"])

    trains = [
        "12901 MAHSR Tejas Bullet (06:00 AM - 08:07 AM)",
        "12903 Sabarmati Express Bullet (10:30 AM - 12:37 PM)",
        "12905 Western Lightning Bullet (05:15 PM - 07:22 PM)"
    ]
    chosen_train = st.radio(T["select_train"], trains)

    b1, b2 = st.columns([1, 4])
    with b1:
        if st.button(T["back_btn"]):
            st.session_state.step = 1
            st.rerun()
    with b2:
        if st.button(T["next_seat_btn"], type="primary"):
            if from_stn == to_stn:
                st.warning("⚠️ Departure and destination stations cannot be the same.")
            else:
                st.session_state.from_stn = from_stn
                st.session_state.to_stn = to_stn
                st.session_state.travel_date = str(travel_date)
                st.session_state.chosen_train = chosen_train
                st.session_state.step = 3
                st.rerun()

# ==========================================
# STEP 3: INTERACTIVE COACH SEAT MATRIX
# ==========================================
elif st.session_state.step == 3:
    st.subheader(T["step3_header"])
    
    coach_class = st.radio(T["class_label"], [T["std_class"], T["bus_class"]], horizontal=True)
    is_business = "Business" in coach_class or "बिज़नेस" in coach_class or "बिझनेस" in coach_class or "બિઝનેસ" in coach_class
    coach_code = "B1" if is_business else "C1"

    st.markdown("---")
    rows = ["1", "2", "3", "4"]
    cols = ["A", "B", "C", "D"] if is_business else ["A", "B", "C", "D", "E"]
    booked_seats = {"1B", "2C", "3A", "4D"}

    for r in rows:
        grid_cols = st.columns(len(cols) + 1)
        for idx, c in enumerate(cols):
            col_pos = idx + 1 if (is_business and idx >= 2) or (not is_business and idx >= 3) else idx
            seat_id = f"{r}{c}"
            with grid_cols[col_pos]:
                if seat_id in booked_seats:
                    st.button(f"🚫 {seat_id}", key=f"btn_{seat_id}", disabled=True, use_container_width=True)
                else:
                    btn_type = "primary" if st.session_state.selected_seat == seat_id else "secondary"
                    if st.button(f"💺 {seat_id}", key=f"btn_{seat_id}", type=btn_type, use_container_width=True):
                        st.session_state.selected_seat = seat_id
                        st.rerun()

    st.markdown("---")
    if st.session_state.selected_seat:
        st.info(f"✅ {T['selected_seat']} **{coach_code}-{st.session_state.selected_seat}**")

    c_back, c_next = st.columns([1, 4])
    with c_back:
        if st.button(T["back_btn"]):
            st.session_state.step = 2
            st.rerun()
    with c_next:
        if st.button(T["confirm_btn"], type="primary"):
            if st.session_state.selected_seat:
                st.session_state.coach_code = coach_code
                st.session_state.step = 4
                st.rerun()
            else:
                st.error(T["err_seat"])

# ==========================================
# STEP 4: QR E-BOARDING PASS & WAYFINDING
# ==========================================
elif st.session_state.step == 4:
    st.subheader(T["step4_header"])

    qr_payload = (
        f"PNR:{st.session_state.pnr}|Name:{st.session_state.passenger_name}|"
        f"Phone:{st.session_state.passenger_phone}|From:{st.session_state.from_stn}|"
        f"To:{st.session_state.to_stn}|Seat:{st.session_state.coach_code}-{st.session_state.selected_seat}"
    )
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={urllib.parse.quote(qr_payload)}"

    col_ticket, col_qr = st.columns([2, 1])
    with col_ticket:
        st.markdown(f"""
            <div class="ticket-card">
                <h2 style="color:#001f3f; margin-top:0;">🚄 MAHSR E-BOARDING PASS</h2>
                <p><strong>{T['pnr']}:</strong> {st.session_state.pnr}</p>
                <p><strong>{T['passenger']}:</strong> {st.session_state.passenger_name}</p>
                <p><strong>{T['mobile']}:</strong> +91-{st.session_state.passenger_phone}</p>
                <p><strong>{T['route']}:</strong> {st.session_state.from_stn} ➔ {st.session_state.to_stn}</p>
                <p><strong>Train:</strong> {st.session_state.chosen_train} ({st.session_state.travel_date})</p>
                <p><strong>{T['seat']}:</strong> {st.session_state.coach_code} - {st.session_state.selected_seat}</p>
            </div>
        """, unsafe_allow_html=True)

    with col_qr:
        st.image(qr_url, caption="Scan at Station Turnstile", width=210)

    st.markdown(f"""
        <div class="wayfinding-box">
            <h4>{T['wayfinding_title']}</h4>
            <p>{T['wayfinding_text']}</p>
        </div>
    """, unsafe_allow_html=True)

    st.write("")
    if st.button(T["new_booking"]):
        st.session_state.step = 1
        st.session_state.selected_seat = None
        st.session_state.pnr = f"MAHSR-{random.randint(1000, 9999)}"
        st.rerun()
