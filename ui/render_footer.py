import streamlit as st

def render_footer(current_page_label: str):
    st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)

    page_links = {
        "🏠 Trang chủ": "Home.py",
        "📡 Dò Tìm Việc làm": "pages/1_📡_JobRadar.py",
        "🔎 So Khớp Việc làm": "pages/2_🔎_JobMatcher.py",
        "💼 Định hướng Nghề nghiệp": "pages/3_💼_CareerMatch.py",
        "📚 Cầu nối Kỹ năng": "pages/4_📚_SkillBridge.py",
        "📝 Tạo CV": "pages/5_📝_ResumeBuilder.py",
        "🛠️ Tối ưu hóa ATS": "pages/6_🛠️_ATS_TuneUp.py",
        "✉️ Viết Thư ứng tuyển": "pages/7_✉️_Cover_Letter.py",
        "🎙️ Luyện phỏng vấn": "pages/8_🎙️_Interview_Prep.py"
    }

    page_links.pop(current_page_label, None)  # Remove the current page from the links

    st.divider()

    st.caption(
    "<p style='text-align:center'>🚀 <strong>CareerForge AI</strong> — bộ công cụ thông minh giúp phân tích CV, so khớp công việc và chuẩn bị phỏng vấn.</p>"
    "<p style='text-align:center'>Được xây dựng với ❤️ sử dụng Streamlit, spaCy và Google Gemini.</p>",
    unsafe_allow_html=True)

    st.divider()

    col_left, col_right = st.columns([0.5, 0.5])

    with col_left:
        st.markdown("#### 🌟 Hệ sinh thái CareerForge")
        st.write("Nền tảng thông minh được thiết kế nhằm giúp người tìm việc và các chuyên gia nâng cao mức độ phù hợp của CV cũng như sự sẵn sàng cho các buổi phỏng vấn thử.")

    with col_right:
        st.markdown("#### 🔗 Điều hướng nhanh")
        for label, path in page_links.items():
            st.page_link(path, label=label, use_container_width=True)
    
    st.divider()
    st.markdown("<p style='font-size: 12px; color: #888; text-align:center'>© 2026 CareerForge AI. Bảo lưu mọi quyền.</p>", unsafe_allow_html=True)
    st.divider()