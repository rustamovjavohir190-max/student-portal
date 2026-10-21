import streamlit as st
from pypdf import PdfWriter, PdfReader
from PIL import Image
import io
import zipfile

# Sahifa sozlamalari
st.set_page_config(
    page_title="Student Smart Portal",
    page_icon="🍎",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Apple Style Glassmorphism CSS (Tuzatilgan oraliqlar bilan)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif;
    }
    
    .apple-header {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.2);
        margin-bottom: 25px;
    }

    .stButton > button {
        width: 100%;
        border-radius: 14px;
        font-weight: 600;
        font-size: 16px;
        background: linear-gradient(180deg, #007aff 0%, #0056b3 100%);
        color: #ffffff;
        border: none;
        padding: 10px 20px;
        box-shadow: 0 8px 16px rgba(0, 122, 255, 0.3);
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 20px rgba(0, 122, 255, 0.4);
    }

    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.03);
        border: 2px dashed rgba(255, 255, 255, 0.2);
        border-radius: 16px;
        padding: 15px;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.05);
        padding: 6px;
        border-radius: 14px;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(255, 255, 255, 0.15) !important;
        color: #ffffff !important;
    }
    
    .course-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-top: 10px;
        margin-bottom: 10px;
    }
    
    .section-title {
        margin-top: 20px;
        margin-bottom: 15px;
        font-size: 18px;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="apple-header">
        <h1 style="margin:0; font-size: 28px; font-weight:700;">🎓 Student Smart Portal</h1>
        <p style="margin-top:8px; margin-bottom:0; color: #cbd5e1; font-size: 14px;">Dars jadvali, Prezentatsiyalar va Fayl Asboblari</p>
    </div>
""", unsafe_allow_html=True)

# Session state ma'lumotlarini saqlash
if "uploaded_materials" not in st.session_state:
    st.session_state["uploaded_materials"] = {}

# Tablar (Menyu)
tab_study, tab_pdf, tab_img, tab_zip = st.tabs(["📚 O'quv Portali", "📄 PDF Asboblari", "🖼️ Rasm Siqish", "📦 ZIP Arxiv"])

# ==========================================
# 0. O'QUV PORTALI (Dars jadvali va Fanlar)
# ==========================================
with tab_study:
    st.subheader("🎓 Talabalar Portali")
    
    col_kurs, col_admin = st.columns([2, 1])
    with col_kurs:
        selected_kurs = st.selectbox("Kursni tanlang:", ["1-kurs", "2-kurs", "3-kurs", "4-kurs"])
    
    # MAXFIY ADMIN REJIMI (Parol bilan)
    with col_admin:
        admin_pass = st.text_input("🔑 Admin paroli:", type="password", placeholder="Parol yozing", help="Faqat administratorlar uchun")
        is_admin = (admin_pass == "admin123") # Maxfiy parol: admin123
        if admin_pass and not is_admin:
            st.error("Noto'g'ri parol!")
        elif is_admin:
            st.success("Admin rejimi aktiv!")

    sub_tab1, sub_tab2 = st.tabs(["📅 Dars Jadvali", "📂 Fanlar va Prezentatsiyalar"])
    
    # ------------------------------------------
    # DARS JADVALI
    # ------------------------------------------
    with sub_tab1:
        st.markdown(f"### 📅 {selected_kurs} Dars Jadvali")
        
        if selected_kurs == "2-kurs":
            jadval = {
                "Dushanba": ["09:00 - Kiberxavfsizlik asoslari (302-xona)", "10:30 - C++ va Qt Dasturlash (Lab 4)"],
                "SeshDynamic": ["09:00 - Operatsion Tizimlar (201-xona)", "10:30 - Tarmoq Xavfsizligi (305-xona)"],
                "Chorshanba": ["09:00 - Kriptografiya Usullari (104-xona)", "10:30 - Ingliz tili (IELTS) (402-xona)"],
                "Payshanba": ["09:00 - Ma'lumotlar Bazasi (Lab 2)", "10:30 - Kiber Huquq (301-xona)"],
                "Juma": ["09:00 - Linux Tizim Ma'murligi (Lab 5)", "10:30 - Mustaqil Ta'lim"],
            }
            for kun, darslar in jadval.items():
                with st.expander(f"📌 {kun}"):
                    for dars in darslar:
                        st.write(f"• {dars}")
        else:
            st.info(f"{selected_kurs} uchun dars jadvali tez orada yuklanadi.")

    # ------------------------------------------
    # FANLAR VA PREZENTATSIYALAR
    # ------------------------------------------
    with sub_tab2:
        st.markdown(f"### 📚 {selected_kurs} Fan Materiallari")
        
        fanlar_dict = {
            "1-kurs": ["Matematika", "Fizika", "Dasturlash Asoslari", "Kirish IT"],
            "2-kurs": ["Kiberxavfsizlik asoslari", "C++ va Qt Dasturlash", "Operatsion Tizimlar", "Tarmoq Xavfsizligi"],
            "3-kurs": ["Penetration Testing", "Web Application Security", "Reverse Engineering"],
            "4-kurs": ["Diplom Ishi", "Kiber Insidentlarni Boshqarish", "Amaliyot"]
        }
        
        available_fanlar = fanlar_dict.get(selected_kurs, [])
        selected_fan = st.selectbox("Fanni tanlang:", available_fanlar)
        
        storage_key = f"{selected_kurs}_{selected_fan}"
        
        # PAROL TO'G'RI BO'LSA ADMIN FAYL YUKLAY OLADI
        if is_admin:
            st.warning("⚙️ Admin Rejimi: Bu yerda yangi prezentatsiyalarni yuklashingiz mumkin.")
            uploaded_file = st.file_uploader(f"'{selected_fan}' fani uchun fayl yuklang", type=["pdf", "pptx", "ppt", "zip"], key="admin_uploader")
            
            if uploaded_file:
                if st.button("📤 Faylni Saqlash / Ulashish", use_container_width=True):
                    if storage_key not in st.session_state["uploaded_materials"]:
                        st.session_state["uploaded_materials"][storage_key] = []
                    
                    st.session_state["uploaded_materials"][storage_key].append({
                        "name": uploaded_file.name,
                        "bytes": uploaded_file.getvalue(),
                        "type": uploaded_file.type
                    })
                    st.success(f"'{uploaded_file.name}' fayli muvaffaqiyatli yuklandi!")

        # PREZENTATSIYALAR RO'YXATI
        st.markdown(f"<div class='section-title'>📄 '{selected_fan}' bo'yicha prezentatsiyalar:</div>", unsafe_allow_html=True)
        
        materials = st.session_state["uploaded_materials"].get(storage_key, [])
        
        if materials:
            for idx, mat in enumerate(materials):
                st.markdown(f"""
                <div class="course-card">
                    <b>📁 {mat['name']}</b>
                </div>
                """, unsafe_allow_html=True)
                
                st.download_button(
                    label=f"⬇️ Yuklab olish: {mat['name']}",
                    data=mat['bytes'],
                    file_name=mat['name'],
                    mime=mat['type'],
                    key=f"dl_{storage_key}_{idx}",
                    use_container_width=True
                )
        else:
            st.info("Hozircha bu fan bo'yicha prezentatsiya yuklanmagan.")

# ==========================================
# 1. PDF BO'LIMI
# ==========================================
with tab_pdf:
    st.subheader("📄 PDF Asboblari")
    pdf_option = st.radio("Amalni tanlang:", ["PDF Fayllarni Birlashtirish", "PDF Hajmini Kichraytirish"], horizontal=True)
    
    if pdf_option == "PDF Fayllarni Birlashtirish":
        uploaded_pdfs = st.file_uploader("PDF fayllarni tanlang", type=["pdf"], accept_multiple_files=True, key="pdf_merge")
        if uploaded_pdfs:
            if st.button("🚀 PDF-larni Birlashtirish", use_container_width=True):
                with st.spinner("Qayta ishlanmoqda..."):
                    merger = PdfWriter()
                    for pdf in uploaded_pdfs:
                        merger.append(pdf)
                    output = io.BytesIO()
                    merger.write(output)
                    merger.close()
                    output.seek(0)
                st.success("Birlashtirildi! ✨")
                st.download_button(label="⬇️ Natijani Yuklab Olish", data=output, file_name="merged_document.pdf", mime="application/pdf", use_container_width=True)

    elif pdf_option == "PDF Hajmini Kichraytirish":
        uploaded_pdf = st.file_uploader("PDF faylni tanlang", type=["pdf"], key="pdf_compress")
        if uploaded_pdf:
            if st.button("⚡ PDF Hajmini Kichraytirish", use_container_width=True):
                with st.spinner("Siqilmoqda..."):
                    reader = PdfReader(uploaded_pdf)
                    writer = PdfWriter()
                    for page in reader.pages:
                        page.compress_content_streams()
                        writer.add_page(page)
                    output = io.BytesIO()
                    writer.write(output)
                    writer.close()
                    output.seek(0)
                    orig_size = len(uploaded_pdf.getvalue()) / 1024
                    comp_size = len(output.getvalue()) / 1024
                st.success(f"Natija: {orig_size:.1f} KB ➔ {comp_size:.1f} KB ✨")
                st.download_button(label="⬇️ Siqilgan PDF-ni Yuklab Olish", data=output, file_name="compressed_document.pdf", mime="application/pdf", use_container_width=True)

# ==========================================
# 2. RASM BO'LIMI
# ==========================================
with tab_img:
    st.subheader("🖼️ Rasmlar Hajmi")
    uploaded_images = st.file_uploader("Rasmlarni tanlang (JPG, PNG, WEBP)", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True, key="img_compress")
    if uploaded_images:
        quality = st.slider("Rasm sifati (%)", min_value=10, max_value=90, value=65)
        if st.button("⚡ Rasmlarni Siqish", use_container_width=True):
            with st.spinner("Siqilmoqda..."):
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for img_file in uploaded_images:
                        img = Image.open(img_file)
                        if img.mode in ("RGBA", "P"):
                            img = img.convert("RGB")
                        output_img = io.BytesIO()
                        img.save(output_img, format="JPEG", quality=quality, optimize=True)
                        output_img.seek(0)
                        zip_file.writestr(f"compressed_{img_file.name}.jpg", output_img.getvalue())
                zip_buffer.seek(0)
            st.success("Rasmlar tayyor! ✨")
            st.download_button(label="⬇️ Siqilgan Rasmlarni (ZIP) Yuklab Olish", data=zip_buffer, file_name="compressed_images.zip", mime="application/zip", use_container_width=True)

# ==========================================
# 3. ZIP BO'LIMI
# ==========================================
with tab_zip:
    st.subheader("📦 ZIP Arxivlash")
    uploaded_any_files = st.file_uploader("Istalgan fayllarni tanlang", accept_multiple_files=True, key="zip_creator")
    if uploaded_any_files:
        compression_level = st.selectbox("Siqish darajasi", ["Maksimal siqish (LZMA)", "Odatiy siqish (Deflated)"])
        if st.button("⚡ ZIP Arxiv Yaratish", use_container_width=True):
            with st.spinner("Arxivlanmoqda..."):
                compress_type = zipfile.ZIP_LZMA if "Maksimal" in compression_level else zipfile.ZIP_DEFLATED
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", compress_type) as zip_file:
                    for file in uploaded_any_files:
                        zip_file.writestr(file.name, file.getvalue())
                zip_buffer.seek(0)
            st.success("Arxiv tayyor! ✨")
            st.download_button(label="⬇️ Arxivni Yuklab Olish", data=zip_buffer, file_name="archive_compressed.zip", mime="application/zip", use_container_width=True)