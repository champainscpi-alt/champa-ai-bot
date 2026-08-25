import streamlit as st
import pandas as pd
import google.generativeai as genai
import plotly.express as px
import os
import base64

# ==========================================
# ตั้งค่าหน้าเว็บ 
# ==========================================
st.set_page_config(page_title="Champa AI Assistant", page_icon="🌼", layout="centered")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Lao:wght@300;400;500;700&family=Noto+Sans+Thai:wght@300;400;500;700&display=swap');
        
        * {
            font-family: 'Noto Sans Lao', 'Noto Sans Thai', sans-serif !important;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. ฐานข้อมูลภาษา (รองรับ 4 ภาษา)
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
        "ai_instruction": "You must answer the question in Lao language (ພາສາລາວ) naturally and professionally.",
        "tab_chat": "💬 ຖາມ-ຕອບ",
        "tab_dash": "📊 ຂໍ້ມູນສະຖິຕິ",
        "tab_forms": "📥 ດາວໂຫຼດແບບຟອມ",
        "chart_title": "ສັດສ່ວນເປົ້າໝາຍທຸລະກິດ ປະກັນໄພປີ 2026"
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
        "ai_instruction": "You must answer the question in Thai language naturally and professionally.",
        "tab_chat": "💬 ถาม-ตอบ",
        "tab_dash": "📊 แดชบอร์ด",
        "tab_forms": "📥 ดาวน์โหลดแบบฟอร์ม",
        "chart_title": "สัดส่วนเป้าหมายธุรกิจ ประกันภัยปี 2026"
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
        "ai_instruction": "You must answer the question in English naturally and professionally.",
        "tab_chat": "💬 Q&A",
        "tab_dash": "📊 Dashboard",
        "tab_forms": "📥 Download Forms",
        "chart_title": "2026 Business Target Portfolio"
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
        "ai_instruction": "You must answer the question in Vietnamese (Tiếng Việt) naturally and professionally.",
        "tab_chat": "💬 Hỏi đáp",
        "tab_dash": "📊 Thống kê",
        "tab_forms": "📥 Tải biểu mẫu",
        "chart_title": "Mục tiêu Kinh doanh năm 2026"
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
# 3. ส่วนหัวของเว็บ (โหลดข้อมูลและแสดงโลโก้)
# ==========================================
ui_text = lang_options[st.session_state.selected_lang]

st.write("<br>", unsafe_allow_html=True)
display_centered_logo(width_ratio=2)

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
# 4. ระบบแท็บ (Tabs): แชท / กราฟ / แบบฟอร์ม
# ==========================================
tab1, tab2, tab3 = st.tabs([ui_text["tab_chat"], ui_text["tab_dash"], ui_text["tab_forms"]])

# --- TAB 1: ระบบถาม-ตอบ ---
with tab1:
    if "messages" not in st.session_state:
        st.session_state.messages = []

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

# --- TAB 2: แดชบอร์ด & รูปพาย ---
with tab2:
    st.subheader(ui_text["chart_title"])
    chart_data = {
        'Category': ['ປະກັນໄພລົດຍົນ (Motor)', 'ປະກັນໄພສ່ວນບຸກຄົນ (Personal)', 'ປະກັນໄພຊັບສິນ (Property)', 'ອື່ນໆ (Others)'],
        'Percentage': [55, 25, 15, 5]
    }
    df_chart = pd.DataFrame(chart_data)
    
    fig = px.pie(df_chart, values='Percentage', names='Category', hole=0.3, 
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_layout(margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig, use_container_width=True)

# --- TAB 3: ดาวน์โหลดและดูตัวอย่างแบบฟอร์ม (อัปเดตเลย์เอาต์ใหม่) ---
with tab3:
    st.markdown("### 🗂️ เอกสารและแบบฟอร์มภายในบริษัท")
    st.info("💡 คำแนะนำ: เพื่อให้ระบบแสดงหน้าตัวอย่างเอกสารได้สมบูรณ์ ควรใช้ไฟล์สกุล .pdf ครับ")
    
    forms = [
        {"name": "CPI Company Profile", "filename": "CPI Company Profile.pdf"},
        {"name": "นโยบายการพิจารณารับประกันภัย 2026 (Underwriting Guidelines)", "filename": "underwriting_2026.pdf"},
        {"name": "แบบฟอร์มคำขอลาพักร้อน (Leave Request)", "filename": "leave_request.pdf"}
    ]
    
    for form in forms:
        st.markdown(f"#### 📄 {form['name']}")
        
        file_path = form['filename']
        
        # ปุ่มดาวน์โหลด
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                st.download_button("📥 ดาวน์โหลดไฟล์", data=f, file_name=file_path, key=f"dl_{file_path}")
        else:
            st.download_button("📥 ดาวน์โหลดไฟล์", data="นี่คือไฟล์ทดสอบระบบ", file_name=file_path, key=f"mock_{file_path}")
                
        # หน้าต่างดูตัวอย่างแบบเต็มจอ
        with st.expander("คลิกเพื่อดูหน้าตัวอย่างเอกสาร (Preview)"):
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="500" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
            else:
                st.info(f"*(ระบบจะแสดงตัวอย่างเอกสารที่นี่ เมื่อคุณอัปโหลดไฟล์ {file_path} ขึ้น GitHub เรียบร้อยแล้ว)*")
        
        st.markdown("---")
