import streamlit as st
import pandas as pd
import google.generativeai as genai

# ==========================================
# ตั้งค่าหน้าเว็บ
# ==========================================
st.set_page_config(page_title="Champa AI Assistant", page_icon="🏢")

# 🟢 เพิ่มฟอนต์ Noto Sans Lao และ Noto Sans Thai ให้ตัวหนังสือสวยงาม
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Lao:wght@300;400;500;700&family=Noto+Sans+Thai:wght@300;400;500;700&display=swap');
        
        * {
            font-family: 'Noto Sans Lao', 'Noto Sans Thai', sans-serif !important;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. ฐานข้อมูลภาษา (รวมหน้าล็อกอินและหน้าแชท)
# ==========================================
lang_options = {
    "ລາວ (Lao)": {
        "login_title": "🛡️ ເຂົ້າສູ່ລະບົບ Champa AI",
        "login_sub": "ລະບົບຜູ້ຊ່ວຍອັດສະລິຍະສຳລັບພະນັກງານ **ຈຳປາປະກັນໄພ (Champa Insurance)**",
        "pwd_prompt": "ກະລຸນາໃສ່ລະຫັດຜ່ານຂອງບໍລິສັດ:",
        "login_btn": "ເຂົ້າສູ່ລະບົບ",
        "login_err": "ລະຫັດຜ່ານບໍ່ຖືກຕ້ອງ ກະລຸນາລອງໃໝ່",
        "title": "🐘 ລະບົບຖາມ-ຕອບ ພາຍໃນຈຳປາປະກັນໄພ",
        "subtitle": "ພິມຄຳຖາມກ່ຽວກັບແຜນທຸລະກິດປີ 2026, ໂຄງສ້າງອົງກອນ, ຫຼື ນະໂຍບາຍໄດ້ເລີຍ",
        "input": "ພິມຄຳຖາມຂອງທ່ານທີ່ນີ້...",
        "ai_instruction": "You must answer the question in Lao language (ພາສາລາວ) naturally and professionally."
    },
    "ภาษาไทย (Thai)": {
        "login_title": "🛡️ เข้าสู่ระบบ Champa AI",
        "login_sub": "ระบบผู้ช่วยอัจฉริยะสำหรับพนักงาน **จำปาประกันภัย (Champa Insurance)**",
        "pwd_prompt": "กรุณาใส่รหัสผ่านของบริษัท:",
        "login_btn": "เข้าสู่ระบบ",
        "login_err": "รหัสผ่านไม่ถูกต้อง โปรดลองอีกครั้ง",
        "title": "🐘 ระบบถาม-ตอบ ภายในจำปาประกันภัย",
        "subtitle": "พิมพ์คำถามเกี่ยวกับแผนธุรกิจปี 2026, โครงสร้างองค์กร, หรือนโยบายการรับประกันภัยได้เลยครับ",
        "input": "พิมพ์คำถามของคุณที่นี่...",
        "ai_instruction": "You must answer the question in Thai language naturally and professionally."
    },
    "English": {
        "login_title": "🛡️ Login to Champa AI",
        "login_sub": "Smart AI Assistant for **Champa Insurance** employees",
        "pwd_prompt": "Please enter the company password:",
        "login_btn": "Login",
        "login_err": "Incorrect password. Please try again.",
        "title": "🐘 Champa Insurance Q&A System",
        "subtitle": "Ask questions about the 2026 business plan, organizational structure, or policies.",
        "input": "Type your question here...",
        "ai_instruction": "You must answer the question in English naturally and professionally."
    },
    "Tiếng Việt (Vietnamese)": {
        "login_title": "🛡️ Đăng nhập Champa AI",
        "login_sub": "Trợ lý AI thông minh dành cho nhân viên **Champa Insurance**",
        "pwd_prompt": "Vui lòng nhập mật khẩu công ty:",
        "login_btn": "Đăng nhập",
        "login_err": "Sai mật khẩu. Vui lòng thử lại.",
        "title": "🐘 Hệ thống Hỏi đáp Champa Insurance",
        "subtitle": "Nhập câu hỏi về kế hoạch kinh doanh 2026, cơ cấu tổ chức hoặc chính sách.",
        "input": "Nhập câu hỏi của bạn tại đây...",
        "ai_instruction": "You must answer the question in Vietnamese (Tiếng Việt) naturally and professionally."
    }
}

# ==========================================
# 2. ระบบรักษาความปลอดภัย & เลือกภาษาหน้าแรก
# ==========================================
COMPANY_PASSWORD = "Champa@2026"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "selected_lang" not in st.session_state:
    st.session_state.selected_lang = "ລາວ (Lao)"

if not st.session_state.authenticated:
    try:
        st.image("logo.jpg", width=250)
    except:
        pass
        
    # 🟢 ย้ายเมนูเลือกภาษามาไว้หน้าล็อกอิน
    st.session_state.selected_lang = st.selectbox(
        "🌐 Language / ພາສາ / Ngôn ngữ", 
        list(lang_options.keys()), 
        index=list(lang_options.keys()).index(st.session_state.selected_lang)
    )
    
    ui_text = lang_options[st.session_state.selected_lang]
    
    st.title(ui_text["login_title"])
    st.markdown(ui_text["login_sub"])
    pwd = st.text_input(ui_text["pwd_prompt"], type="password")
    
    if st.button(ui_text["login_btn"]):
        if pwd == COMPANY_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error(ui_text["login_err"])
    st.stop() 

# ==========================================
# 3. โหลดข้อมูลจำปาประกันภัย (หน้าแชทหลัก)
# ==========================================
ui_text = lang_options[st.session_state.selected_lang]

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
