# --- TAB 3: ดาวน์โหลดและดูตัวอย่างแบบฟอร์ม ---
with tab3:
    st.markdown("### 🗂️ เอกสารและแบบฟอร์มภายในบริษัท")
    st.info("💡 คำแนะนำ: เพื่อให้ระบบแสดงหน้าตัวอย่างเอกสารได้สมบูรณ์ ควรใช้ไฟล์สกุล .pdf ครับ")
    
    # อัปเดตรายชื่อตามที่คุณต้องการใช้งานจริง
    forms = [
        {"name": "CPI Company Profile", "filename": "cpi_company_profile.pdf"},
        {"name": "นโยบายการพิจารณารับประกันภัย 2026 (Underwriting Guidelines)", "filename": "underwriting_2026.pdf"},
        {"name": "แบบฟอร์มคำขอลาพักร้อน (Leave Request)", "filename": "leave_request.pdf"}
    ]
    
    for form in forms:
        # 1. ชื่อเอกสาร
        st.markdown(f"#### 📄 {form['name']}")
        
        file_path = form['filename']
        
        # 2. ปุ่มดาวน์โหลด (ปรับขนาดให้พอดีคำ ไม่ยืดเต็มจอ)
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                st.download_button("📥 ดาวน์โหลดไฟล์", data=f, file_name=file_path, key=f"dl_{file_path}")
        else:
            st.download_button("📥 ดาวน์โหลดไฟล์", data="นี่คือไฟล์ทดสอบระบบ", file_name=file_path, key=f"mock_{file_path}")
                
        # 3. หน้าต่างดูตัวอย่าง (จัดวางด้านล่าง กางเต็มจอเพื่อให้อ่านง่าย)
        with st.expander("คลิกเพื่อดูหน้าตัวอย่างเอกสาร (Preview)"):
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                # เพิ่มความสูงเป็น 500 เพื่อให้อ่านชัดเจนขึ้น
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="500" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
            else:
                st.info(f"*(ระบบจะแสดงตัวอย่างเอกสารที่นี่ เมื่อคุณอัปโหลดไฟล์ {file_path} ขึ้น GitHub เรียบร้อยแล้ว)*")
        
        st.markdown("---") # เส้นคั่นบางๆ ให้ดูสบายตา
