import streamlit as st
import pandas as pd
import google.generativeai as genai

# ==========================================
# ตั้งค่าหน้าเว็บ
# ==========================================
st.set_page_config(page_title="Champa AI Assistant", page_icon="🏢")

# ==========================================
# 1. ระบบรักษาความปลอดภัย
# ==========================================
COMPANY_PASSWORD = "Champa@2026"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    try:
        st.image("logo.jpg", width=250)
    except:
        pass # ป้องกัน Error กรณีคลาวด์หาไฟล์ภาพไม่เจอ
        
    st.title("🛡️ เข้าสู่ระบบ Champa AI")
    st.markdown("ระบบผู้ช่วยอัจฉริยะสำหรับพนักงาน **จำปาประกันภัย (Champa Insurance)**")
    pwd = st.text_input("กรุณาใส่รหัสผ่านของบริษัท:", type="password")
    
    if st.button("เข้าสู่ระบบ"):
        if pwd == COMPANY_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("รหัสผ่านไม่ถูกต้อง โปรดลองอีกครั้ง")
    st.stop() 

# ==========================================
# 2. ระบบเลือกภาษา (Lao, English, Vietnamese, Thai)
# ==========================================
lang_options = {
    "ລາວ (Lao)": {
        "title": "🐘 ລະບົບຖາມ-ຕອບ ພາຍໃນຈຳປາປະກັນໄພ",
        "subtitle": "ພິມຄຳຖາມກ່ຽວກັບແຜນທຸລະກິດປີ 2026, ໂຄງສ້າງອົງກອນ, ຫຼື ນະໂຍບາຍໄດ້ເລີຍ",
        "input": "ພິມຄຳຖາມຂອງທ່ານທີ່ນີ້...",
        "ai_instruction": "You must answer the question in Lao language (ພາສາລາວ) naturally and professionally."
    },
    "English": {
        "title": "🐘 Champa Insurance Q&A System",
        "subtitle": "Ask questions about the 2026 business plan, organizational structure, or policies.",
        "input": "Type your question here...",
        "ai_instruction": "You must answer the question in English naturally and professionally."
    },
    "Tiếng Việt (Vietnamese)": {
        "title": "🐘 Hệ thống Hỏi đáp Champa Insurance",
        "subtitle": "Nhập câu hỏi về kế hoạch kinh doanh 2026, cơ cấu tổ chức hoặc chính sách.",
        "input": "Nhập câu hỏi của bạn tại đây...",
        "ai_instruction": "You must answer the question in Vietnamese (Tiếng Việt) naturally and professionally."
    },
    "ภาษาไทย (Thai)": {
        "title": "🐘 ระบบถาม-ตอบ ภายในจำปาประกันภัย",
        "subtitle": "พิมพ์คำถามเกี่ยวกับแผนธุรกิจปี 2026, โครงสร้างองค์กร, หรือนโยบายการรับประกันภัยได้เลยครับ",
        "input": "พิมพ์คำถามของคุณที่นี่...",
        "ai_instruction": "You must answer the question in Thai language naturally and professionally."
    }
}

# สร้างเมนูด้านซ้ายสำหรับเปลี่ยนภาษา
with st.sidebar:
    st.subheader("🌐 Select Language")
    selected_lang = st.selectbox("เลือกภาษา / ເລືອກພາສາ / Chọn ngôn ngữ", list(lang_options.keys()))

ui_text = lang_options[selected_lang]

# ==========================================
# 3. โหลดข้อมูลจำปาประกันภัย
# ==========================================
try:
    st.image("logo.jpg", width=200)
except:
    pass

st.title(ui_text["title"])
st.markdown(ui_text["subtitle"])

API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)

LOCAL_EXCEL_FILE = "champa_data.xlsx" 

@st.cache_data(ttl=300) 
def load_company_data():
    try:
        df = pd.read_excel(LOCAL_EXCEL_FILE)
        return df.to_string(index=False)
    except Exception as e:
        return f"Error: {e}"

company_knowledge = load_company_data()

# ==========================================
# 4. ระบบแชท 
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input(ui_text["input"])

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    prompt = f"""
    คุณคือผู้ช่วย AI อัจฉริยะของบริษัท จำปาประกันภัย (Champa Insurance) สปป.ลาว
    จงตอบคำถามพนักงานโดยอ้างอิงจากข้อมูลของบริษัทด้านล่างนี้เท่านั้น 
    
    **คำสั่งสำคัญ (CRITICAL INSTRUCTION):** 
    {ui_text["ai_instruction"]}

    ข้อมูลภายในบริษัท:
    {company_knowledge}

    คำถามของพนักงาน: {user_input}
    """

    try:
        model = genai.GenerativeModel('gemini-3.6-flash')
        response = model.generate_content(prompt)
        bot_reply = response.text
    except Exception as e:
        bot_reply = f"System Error: {e}"

    with st.chat_message("assistant"):
        st.markdown(bot_reply)
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
