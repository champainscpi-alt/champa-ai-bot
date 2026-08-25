import streamlit as st
import pandas as pd
import google.generativeai as genai

# ==========================================
# ตั้งค่าหน้าเว็บ (เปลี่ยนไอคอนหน้าเว็บเป็นดอกจำปา)
# ==========================================
st.set_page_config(page_title="Champa AI Assistant", page_icon="🌼", layout="centered")

# 🟢 CSS ปรับแต่งความสวยงาม (ฟอนต์ และ การจัดหน้า)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Lao:wght@300;400;500;700&family=Noto+Sans+Thai:wght@300;400;500;700&display=swap');
        
        * {
            font-family: 'Noto Sans Lao', 'Noto Sans Thai', sans-serif !important;
        }
        /* ซ่อนเมนูพื้นฐานของ Streamlit ที่ไม่จำเป็น */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
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
        "title": "ລະບົບຖາມ-ຕອບ ພາຍໃນຈຳປາປະກັນໄພ",
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
        "title": "ระบบถาม-ตอบ ภายในจำปาประกันภัย",
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
        "title": "Champa Insurance Q&A System",
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
        "title": "Hệ thống Hỏi đáp Champa Insurance",
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

# ฟังก์ชันแสดงโลโก้ตรงกลาง
def display_centered_logo(width_ratio=2):
    col1, col2, col3 = st.columns([1, width_ratio, 1])
    with col2:
        try:
            st.image("logo.jpg", use_container_width=True)
        except:
            pass

if not st.session_state.authenticated:
    st.write("<br>", unsafe_allow_html=True)
    display_centered_logo(width_ratio=1.5)
    st.write("<br>", unsafe_allow_html=True)
        
    st.session_state.selected_lang = st.selectbox(
        "🌐 Language / ພາສາ / Ngôn ngữ", 
        list(lang_options.keys()), 
        index=list(lang_options.keys()).index(st.session_state.selected_lang)
    )
    
    ui_text = lang_options[st.session_state.selected_lang]
    
    st.title(ui_text["login_title"])
    st.markdown(ui_text["login_sub"])
    pwd = st.text_input(ui_text["pwd_prompt"], type="password")
    
    if st.button(ui_text["login_btn"], use_container_width=True):
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

st.write("<br>", unsafe_allow_html=True)
display_centered_logo(width_ratio=2)

# 🟢 บังคับให้หัวข้ออยู่บรรทัดเดียวกัน จัดกึ่งกลาง และใช้ไอคอนดอกจำปา
st.markdown(f"<h3 style='text-align: center; white-space: nowrap;'>🌼 {ui_text['title']}</h3>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #555;'><b>{ui_text['subtitle']}</b></p>", unsafe_allow_html=True)
st.divider() 

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

# 🟢 เปลี่ยนไอคอนแชท AI เป็นดอกจำปา
USER_AVATAR = "👤"
BOT_AVATAR = "🌼"

for msg in st.session_state.messages:
    avatar_icon = USER_AVATAR if msg["role"] == "user" else BOT_AVATAR
    with st.chat_message(msg["role"], avatar=avatar_icon):
        st.markdown(msg["content"])

user_input = st.chat_input(ui_text["input"])

if user_input:
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    prompt = f"""
    คุณคือผู้ช่วย AI อัจฉริยะของบริษัท จำปาประกันภัย (Champa Insurance) สปป.ลาว
    จงตอบคำถามพนักงานโดยอ้างอิงจากข้อมูลของบริษัทด้านล่างนี้เท่านั้น 
    จัดรูปแบบการตอบให้สวยงาม อ่านง่าย ใช้ Bullet points เมื่อจำเป็น
    
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

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        st.markdown(bot_reply)
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
