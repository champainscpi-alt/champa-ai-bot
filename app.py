import streamlit as st
import pandas as pd
import google.generativeai as genai

# ==========================================
# ตั้งค่าหน้าเว็บ (ย้ายมารวมไว้ด้านบนสุด)
# ==========================================
st.set_page_config(page_title="Champa AI Assistant", page_icon="🏢")

# ==========================================
# 1. ระบบรักษาความปลอดภัย
# ==========================================
COMPANY_PASSWORD = "Champa@2026"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    # 🟢 แสดงโลโก้ที่หน้าล็อกอิน
    st.image("logo.jpg", width=250)
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
# 2. โหลดข้อมูลจำปาประกันภัย
# ==========================================
# 🟢 แสดงโลโก้ที่หน้าหลัก
st.image("logo.jpg", width=200)
st.title("🐘 ระบบถาม-ตอบ ภายในจำปาประกันภัย")
st.markdown("พิมพ์คำถามเกี่ยวกับแผนธุรกิจปี 2026, โครงสร้างองค์กร, หรือนโยบายการรับประกันภัยได้เลยครับ")

# ดึงรหัส API แบบปลอดภัย (สำหรับการรันบน Cloud)
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
# 3. ระบบแชท 
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("พิมพ์คำถามของคุณที่นี่...")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    prompt = f"""
    คุณคือผู้ช่วย AI อัจฉริยะของบริษัท จำปาประกันภัย (Champa Insurance) สปป.ลาว
    จงตอบคำถามพนักงานโดยอ้างอิงจากข้อมูลของบริษัทด้านล่างนี้เท่านั้น 
    หากข้อมูลไม่มีคำตอบ ให้ตอบว่า "ขออภัยครับ ยังไม่มีข้อมูลนี้ในฐานข้อมูลของจำปาประกันภัย" ห้ามคิดข้อมูลหรือนโยบายขึ้นมาเองเด็ดขาด

    ข้อมูลภายในบริษัท:
    {company_knowledge}

    คำถามของพนักงาน: {user_input}
    """

    try:
        model = genai.GenerativeModel('gemini-3.6-flash')
        response = model.generate_content(prompt)
        bot_reply = response.text
    except Exception as e:
        bot_reply = f"ระบบขัดข้องชั่วคราว: {e}"

    with st.chat_message("assistant"):
        st.markdown(bot_reply)
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
