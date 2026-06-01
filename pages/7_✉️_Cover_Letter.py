import streamlit as st
import ui.render_footer as footer
import ui.render_header as header
from analyzer.analysis_enhancer import get_gemini_api_key
from preprocessor.parser import extract_text_from_uploaded_file
from builder.ai_features import generate_cover_letter_with_gemini

# Page configuration
st.set_page_config(page_title="Viết Thư ứng tuyển", page_icon="✉️", layout="centered", initial_sidebar_state="collapsed")
st.logo("ui/assets/header.png", size="large", icon_image="ui/assets/logo.png")

# Header
header.render_header()

# Sidebar
st.sidebar.title("Thư ứng tuyển")
st.sidebar.markdown("Tạo một bức thư ứng tuyển được tùy chỉnh cao bằng cách sử dụng thông tin chi tiết trong CV của bạn và mô tả công việc mục tiêu.")

st.title("✉️ Viết Thư ứng tuyển")
st.caption("Tạo thư ứng tuyển chuyên nghiệp, phù hợp với mô tả công việc mục tiêu của bạn.")
st.divider()

# Inputs
uploaded_resume = st.file_uploader("📄 Tải lên CV của bạn (PDF hoặc DOCX)", type=["pdf", "docx"], key="cl_resume")
uploaded_jd = st.file_uploader("💼 Tải lên Mô tả Công việc (Tùy chọn PDF hoặc DOCX)", type=["pdf", "docx"], key="cl_jd")
jd_text = st.text_area("✍️ Hoặc dán văn bản Mô tả Công việc", height=200, placeholder="Dán các yêu cầu và nhiệm vụ của công việc mục tiêu tại đây...", key="cl_jd_text")

tone = st.selectbox("🎭 Chọn Giọng văn Thư ứng tuyển", ["Chuyên nghiệp", "Trò chuyện", "Nhiệt huyết", "Tự tin"])

# Get API key
api_key = get_gemini_api_key()

# Check session state
if "cover_letter_data" not in st.session_state:
    st.session_state.cover_letter_data = None

st.write("")
generate_btn = st.button("✨ Tạo Thư ứng tuyển", use_container_width=True)

if generate_btn:
    if not uploaded_resume:
        st.error("Vui lòng tải lên CV của bạn để tạo thư ứng tuyển.")
    elif not jd_text.strip() and not uploaded_jd:
        st.error("Vui lòng cung cấp mô tả công việc (tải lên tệp hoặc dán văn bản).")
    else:
        st.divider()
        if not api_key:
            st.info("⚠️ Đang chạy ở Chế độ Bản mẫu Ngoại tuyến (Không cung cấp API key)")
        with st.spinner("Đang soạn thảo thư ứng tuyển của bạn..."):
            try:
                # Extract texts
                resume_content = extract_text_from_uploaded_file(uploaded_resume)
                
                final_jd = ""
                if uploaded_jd:
                    final_jd = extract_text_from_uploaded_file(uploaded_jd)
                else:
                    final_jd = jd_text
                
                # Generate
                cover_letter = generate_cover_letter_with_gemini(resume_content, final_jd, tone, api_key)
                
                # Parse contact info
                from preprocessor.spacy_nlp import load_spacy_nlp_model
                import preprocessor.personal_info as pf
                
                nlp = load_spacy_nlp_model()
                doc = nlp(resume_content)
                name = pf.extract_name(doc, resume_content) or "Applicant Name"
                email = pf.extract_mail(resume_content) or "applicant@example.com"
                phone = pf.extract_phone(resume_content) or "555-0199"
                
                if cover_letter:
                    st.session_state.cover_letter_data = {
                        "text": cover_letter,
                        "name": name,
                        "email": email,
                        "phone": phone
                    }
                else:
                    st.error("Tạo thư ứng tuyển thất bại. Vui lòng thử lại.")
            except Exception as e:
                st.error(f"Đã xảy ra lỗi khi tạo thư ứng tuyển: {e}")

# Render results from session state if available
if st.session_state.cover_letter_data:
    cl_data = st.session_state.cover_letter_data
    cover_letter = cl_data["text"]
    name = cl_data["name"]
    email = cl_data["email"]
    phone = cl_data["phone"]
    
    st.subheader("✉️ Thư ứng tuyển của bạn")
    st.write("")
    
    # Display cover letter
    st.text_area("Văn bản Thư ứng tuyển", value=cover_letter, height=400, disabled=True)
    
    # Download buttons
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="💾 Tải xuống định dạng TXT",
            data=cover_letter,
            file_name="Cover_Letter.txt",
            mime="text/plain",
            use_container_width=True
        )
    with col2:
        from builder.ai_features import generate_cover_letter_docx
        docx_io = generate_cover_letter_docx(name, email, phone, cover_letter)
        st.download_button(
            label="📄 Tải xuống định dạng DOCX",
            data=docx_io,
            file_name="Cover_Letter.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
    st.success("Tạo thư ứng tuyển thành công! Bạn có thể tải xuống ở trên.")

st.divider()
# Footer
footer.render_footer("✉️ Viết Thư ứng tuyển")
