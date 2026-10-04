"""
Nana, Press the Green Button
A tiny WhatsApp helper for grandparents.
Uses Gemma 4 (open-weight) via the Gemini API; Nana opens the app on her phone over home WiFi.
Run with: streamlit run app.py --server.address 0.0.0.0
"""

import os
import requests
import streamlit as st

# Gemma 4 (Google's open-weight model), served free through the Gemini API.
MODEL = "gemma-4-26b-a4b-it"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Grounding notes so even a small model gives correct, simple steps.
WHATSAPP_NOTES = """
VIDEO CALL: Open the person's chat. Tap the video camera icon at the top right. Wait for them to pick up. Tap the red button to end.
VOICE CALL: Open the chat. Tap the phone icon at the top right.
SEND A PHOTO: Open the chat. Tap the paperclip (Android) or the + (iPhone) next to the typing box. Tap Gallery or Photos. Tap the photo. Tap the green send arrow.
TAKE AND SEND A NEW PHOTO: Open the chat. Tap the camera icon in the typing box. Tap the big white circle to click. Tap send.
VOICE MESSAGE: Open the chat. Press and HOLD the microphone button, speak, then let go. It sends by itself.
FORWARD A MESSAGE: Press and hold the message. Tap the arrow pointing right. Pick the person. Tap send.
SEE PHOTOS SOMEONE SENT: Open the chat and tap the photo. To save it, it is usually saved to Gallery automatically.
STATUS: Tap the Updates tab at the bottom. Tap a person's circle to see their status.
GROUP CHAT: Groups appear in Chats like a person. Open it and type normally; everyone in the group sees it.
BLOCK SPAM: Open the chat. Tap the name at the top. Scroll down and tap Block.
FONT TOO SMALL: In WhatsApp, Settings > Chats > Font size > Large.
SAFETY: Never share an OTP or bank details on WhatsApp, even if the message says it is from family or a bank.
"""

SYSTEM_PROMPT = f"""You are a patient, warm helper teaching Indian grandparents how to use WhatsApp on their phone.
Rules:
- Answer in {{lang}}.
- Give at most 5 numbered steps. One short action per step.
- Describe buttons by shape and colour (green arrow, red button, small camera).
- No jargon. Never say "UI", "icon menu", "settings pane".
- If the question is about sharing an OTP, password or money, warn them kindly first.
- End with one short encouraging line.
Use ONLY these facts:
{WHATSAPP_NOTES}
If the answer is not in the facts, say: "Please ask your grandchild to show you this one."
Think briefly. Then write ONLY the final answer for the grandparent between <answer> and </answer>.
"""

QUICK_QUESTIONS = {
    "📹 Video call": "How do I make a video call?",
    "🖼️ Send a photo": "How do I send a photo from my gallery?",
    "🎤 Voice message": "How do I send a voice message?",
    "➡️ Forward message": "How do I forward a message?",
    "🔠 Bigger letters": "The letters are too small, how do I make them bigger?",
    "🚫 Block spam": "Someone unknown is messaging me, how do I block them?",
}


def ask_model(question: str, lang: str) -> str:
    """Ask Gemma 4 via the Gemini API and return the answer text."""
    body = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT.replace("{lang}", lang)}]},
        "contents": [{"role": "user", "parts": [{"text": question}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 4096},
    }
    r = requests.post(API_URL, headers={"x-goog-api-key": API_KEY}, json=body, timeout=60)
    r.raise_for_status()
    data = r.json()
    try:
        parts = data["candidates"][0]["content"]["parts"]
    except (KeyError, IndexError):
        return f"Sorry, no answer came back. (Details: {str(data)[:300]})"

    full = "".join(p.get("text", "") for p in parts)
    # Preferred: the text inside the last <answer>...</answer>
    if "<answer>" in full:
        ans = full.rsplit("<answer>", 1)[1].split("</answer>", 1)[0].strip()
        if ans:
            return ans
    # Fallback: non-thinking parts only
    ans = "".join(p.get("text", "") for p in parts if not p.get("thought")).strip()
    if ans:
        return ans
    return "Sorry, I could not answer that. Please tap the button again."


# ---------- UI ----------
st.set_page_config(page_title="Nana, Press the Green Button", page_icon="🟢",
                   layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;700&family=Nunito:wght@400;600;700&display=swap');

#MainMenu, header, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] {visibility: hidden; height: 0;}
.stApp {background: #F4EFE6;}
.block-container {padding-top: 1.2rem; max-width: 640px;}
html, body, [class*="css"], .stMarkdown, p, label, input {font-family: 'Nunito', sans-serif !important;}

.hero {
  background: linear-gradient(135deg, #075E54 0%, #128C7E 100%);
  border-radius: 28px; padding: 26px 24px 22px; color: #fff; text-align: center;
  box-shadow: 0 10px 30px rgba(7,94,84,.25); margin-bottom: 18px;
}
.hero .dot {width: 64px; height: 64px; border-radius: 50%; background: #25D366; margin: 0 auto 10px;
  box-shadow: 0 0 0 8px rgba(37,211,102,.25); display:flex; align-items:center; justify-content:center; font-size: 30px;}
.hero h1 {font-family: 'Baloo 2', cursive; font-size: 2.1rem; line-height: 1.1; margin: 0; color: #fff;}
.hero p {font-size: 1.1rem; opacity: .9; margin: 6px 0 0;}

.label {font-family: 'Baloo 2', cursive; font-size: 1.45rem; color: #075E54; margin: 14px 0 6px;}

/* language buttons */
div[class*="st-key-lang_"] button {min-height: 64px !important; font-size: 1.2rem;}
div[class*="st-key-lang_"] button p {font-size: 1.2rem !important;}
div[data-testid="stButton"] button[kind="primary"] {
  background: #25D366 !important; border-color: #25D366 !important; color: #fff !important; box-shadow: 0 4px 0 #1DA851 !important;}
div[data-testid="stButton"] button[kind="primary"] p {color: #fff !important;}

/* big task buttons */
div[data-testid="stButton"] button {
  width: 100%; min-height: 88px; border-radius: 22px; border: 2px solid #E2DACB;
  background: #fff !important; color: #1F2C34 !important; font-size: 1.3rem; font-weight: 700;
  box-shadow: 0 4px 0 #E2DACB; transition: transform .08s, box-shadow .08s, border-color .15s;
}
div[data-testid="stButton"] button:hover {border-color: #25D366; color: #075E54;}
div[data-testid="stButton"] button:active {transform: translateY(3px); box-shadow: 0 1px 0 #E2DACB;}
div[data-testid="stButton"] button p {font-size: 1.3rem !important; font-weight: 700; color: inherit; white-space: normal !important; overflow: visible !important; text-overflow: clip !important; line-height: 1.7 !important; padding-top: 4px; margin: 0;}
div[data-testid="stButton"] button, div[data-testid="stButton"] button > div {overflow: visible !important;}
div[data-testid="stHorizontalBlock"] {gap: 12px; flex-wrap: nowrap !important; flex-direction: row !important;}
div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"],
div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {flex: 1 1 0 !important; min-width: 0 !important; width: auto !important;}
@media (max-width: 640px) {
  div[data-testid="stButton"] button {min-height: 80px; font-size: 1.1rem; padding: 6px;}
  div[data-testid="stButton"] button p {font-size: 1.1rem !important;}
  .hero h1 {font-size: 1.7rem;}
}

/* text box */
div[data-testid="stTextInput"] input {font-size: 1.2rem; border-radius: 18px; padding: 16px;
  background: #fff; border: 2px solid #E2DACB; color: #1F2C34;}

/* chat bubbles */
.q-bubble {background: #D9FDD3; border-radius: 20px 20px 4px 20px; padding: 14px 18px; margin: 18px 0 10px auto;
  max-width: 85%; font-size: 1.2rem; color: #1F2C34; box-shadow: 0 2px 4px rgba(0,0,0,.06); width: fit-content;}
.a-card {background: #fff; border-radius: 20px 20px 20px 4px; padding: 18px 22px; font-size: 1.3rem; line-height: 1.7;
  color: #1F2C34; box-shadow: 0 6px 18px rgba(0,0,0,.08); border-left: 6px solid #25D366;}
.a-card ol, .a-card ul {padding-left: 1.3rem; margin: 0;}
.a-card li {margin-bottom: 8px;}
.safe {background: #FFF4D6; border-radius: 16px; padding: 12px 16px; font-size: 1.05rem; color: #6B4E00; margin-top: 22px;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="dot">📞</div>
  <h1>Nana, Press the Green Button</h1>
  <p>Your WhatsApp helper. Tap a button, follow the steps.</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="label">Choose your language</div>', unsafe_allow_html=True)
if "lang" not in st.session_state:
    st.session_state.lang = "English"
if "question" not in st.session_state:
    st.session_state.question = None

LANGS = {"English": "English", "Hindi": "हिंदी", "Marathi": "मराठी"}
lang_cols = st.columns(3)
for col, (code, shown) in zip(lang_cols, LANGS.items()):
    if col.button(shown, key=f"lang_{code}", use_container_width=True,
                  type="primary" if st.session_state.lang == code else "secondary"):
        st.session_state.lang = code
        st.rerun()
lang = st.session_state.lang

st.markdown('<div class="label">What do you want to do?</div>', unsafe_allow_html=True)
cols = st.columns(2)
for i, (label, q) in enumerate(QUICK_QUESTIONS.items()):
    if cols[i % 2].button(label, key=f"q_{i}", use_container_width=True):
        st.session_state.question = q

st.markdown('<div class="label">Or ask in your own words</div>', unsafe_allow_html=True)
typed = st.text_input("Question", placeholder="e.g. how do I call Malisha on video?", label_visibility="collapsed")
if typed and typed != st.session_state.get("last_typed"):
    st.session_state.question = typed
    st.session_state.last_typed = typed
question = st.session_state.question

if not API_KEY:
    st.error("Missing GEMINI_API_KEY. Ask your grandchild to set it up.")
elif question:
    st.markdown(f'<div class="q-bubble">{question}</div>', unsafe_allow_html=True)
    try:
        with st.spinner("Finding the steps..."):
            answer = ask_model(question, lang)
        import markdown as md
        st.markdown(f'<div class="a-card">{md.markdown(answer)}</div>', unsafe_allow_html=True)
    except requests.exceptions.HTTPError as e:
        st.error(f"The helper could not answer right now. ({e.response.status_code}: {e.response.text[:300]})")
    except requests.exceptions.RequestException as e:
        st.error(f"The helper could not answer right now. Please try again. ({e})")

st.markdown('<div class="safe">🔒 Never share an OTP or bank details on WhatsApp, even if the message says it is from family.</div>',
            unsafe_allow_html=True)
