# --- TAB 3: ดาวน์โหลดและดูตัวอย่างแบบฟอร์ม (อัปเดตระบบดูตัวอย่าง) ---
with tab3:
    st.markdown("### 🗂️ เอกสารและแบบฟอร์มภายในบริษัท")
    st.info("💡 คำแนะนำ: เพื่อให้ระบบแสดงหน้าตัวอย่างเอกสารได้สมบูรณ์ ต้องเป็นไฟล์สกุล .pdf ที่ใช้งานได้จริงครับ")
    
    forms = [
        {"name": "CPI Company Profile", "filename": "cpi_company_profile.pdf"},
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
                
        # 👁️ หน้าต่างดูตัวอย่างแบบเต็มจอ (อัปเดตใช้คำสั่ง embed)
        with st.expander("คลิกเพื่อดูหน้าตัวอย่างเอกสาร (Preview)"):
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                
                # 🟢 ใช้ <embed> แทน <iframe> ช่วยลดปัญหาหน้าขาวบน Google Chrome
                pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf" />'
                st.markdown(pdf_display, unsafe_allow_html=True)
            else:
                st.info(f"*(ระบบจะแสดงตัวอย่างเอกสารที่นี่ เมื่อคุณอัปโหลดไฟล์ {file_path} ขึ้น GitHub เรียบร้อยแล้ว)*")
        
        st.markdown("---")
