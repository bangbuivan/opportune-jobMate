import streamlit as st
import ui.render_footer as footer
import ui.render_header as header
from analyzer.analysis_enhancer import (
    get_gemini_api_key,
    perform_ai_ats_analysis
)
from analyzer.resume_analysis import run_local_ats_analysis
from preprocessor.parser import extract_text_from_uploaded_file

# Page configuration
st.set_page_config(page_title="Tối ưu hóa ATS", page_icon="🛠️", layout="centered", initial_sidebar_state="collapsed")
st.logo("ui/assets/header.png", size="large", icon_image="ui/assets/logo.png")

# Header
header.render_header()

# Sidebar
st.sidebar.title("🛠️ Tối ưu hóa ATS")
st.sidebar.markdown("Phân tích mức độ tương thích của CV với Hệ thống Quản lý Tuyển dụng (ATS) bằng quy tắc chuyên gia và tối ưu bằng AI.")

# Title
st.title("🛠️ Tối ưu hóa ATS")
st.caption("Giúp CV của bạn thực sự sẵn sàng cho ATS bằng cách xác định điểm yếu và điểm mạnh thông qua các quy tắc heuristic hoặc AI.")
st.divider()

# Upload Section
uploaded_file = st.file_uploader("📄 Tải lên CV của bạn (PDF hoặc DOCX)", type=["pdf", "docx"])
st.write("")

# AI Key Input Section
api_key = get_gemini_api_key()

# Buttons
col1, col2 = st.columns([1, 1])
run_local = col1.button("🔍 Phân tích ATS Heuristic", use_container_width=True)
run_ai = col2.button("✨ Phân tích ATS bằng AI", use_container_width=True)

if uploaded_file:
    resume_text = extract_text_from_uploaded_file(uploaded_file)

    if run_local:
        st.divider()
        st.subheader("🔍 Kết quả Phân tích ATS")
        st.write("")
        with st.spinner("Đang phân tích CV..."):
            local_feedback = run_local_ats_analysis(resume_text, uploaded_file)
            
            # --- Category scorecard ---
            from analyzer.resume_analysis import calculate_ats_category_scores
            scores = calculate_ats_category_scores(local_feedback)
            
            st.markdown("### 📊 Điểm số ATS Heuristic")
            cols = st.columns(5)
            for i, (cat, val) in enumerate(scores.items()):
                with cols[i]:
                    st.metric(label=cat, value=f"{val}/100")
                    st.progress(val)
            st.write("")
            
            st.divider()
            for step in local_feedback:
                st.markdown(f"### 🧩 Bước {step['step']}: {step['title']}")
                for level, msg in step["findings"]:
                    if level == "warning":
                        st.warning(msg)
                    else:
                        st.success(msg)
            
            st.divider()
            st.write("")
            st.info("""Chúng tôi khuyên bạn nên sử dụng thêm các công cụ phân tích ATS trực tuyến khác, vì đôi khi mỗi công cụ sẽ cung cấp những góc nhìn hữu ích khác nhau. Một số công cụ khuyên dùng được liệt kê dưới đây:""")
            cols = st.columns([1, 1, 1], vertical_alignment='center', gap='small')
            with cols[0]:
                st.link_button("Weekday", "https://www.weekday.works/resume-checker-and-scoring-tool", use_container_width= True)
                st.link_button("MyPerfectResume", "https://www.myperfectresume.com/resume/ats-resume-checker", use_container_width= True)
            with cols[1]:
                st.link_button("Resume-Now", "https://www.resume-now.com/build-resume?mode=ats", use_container_width= True)
                st.link_button("Enhancv", "https://enhancv.com/resources/resume-checker/", use_container_width= True)
            with cols[2]:
                st.link_button("Jobscan", "https://www.jobscan.co/", use_container_width= True)
                st.link_button("1MillionResume", "https://1millionresume.com/resume-checker", use_container_width= True)

    elif run_ai:
        st.divider()
        if not api_key:
            st.error("Vui lòng nhập API key Google Gemini để sử dụng tính năng phân tích bằng AI.")
        else:
            st.subheader("✨ Phân tích ATS bằng AI")
            st.write("")
            with st.spinner("AI đang đánh giá CV của bạn..."):
                ai_feedback = perform_ai_ats_analysis(resume_text, api_key)

                # --- Category scorecard ---
                from analyzer.resume_analysis import calculate_ai_ats_category_scores
                scores = calculate_ai_ats_category_scores(ai_feedback)

                # Display ATS score if present
                ats_score = ai_feedback.get("ATS_Score")
                if ats_score is not None:
                    st.markdown(f"### 🧠 Điểm Tương thích ATS: **{ats_score}/100**")
                    st.progress(min(int(ats_score), 100), text = "Điểm ATS")
                    if ats_score >= 80:
                        st.success("Xuất sắc! CV của bạn tương thích rất tốt với ATS.")
                    elif ats_score >= 60:
                        st.info("Khá tốt, nhưng vẫn có điểm có thể cải thiện thêm.")
                    else:
                        st.warning("Cần cải thiện. Vui lòng làm theo các gợi ý bên dưới.")

                st.write("")
                st.markdown("### 📊 Chi tiết các hạng mục ATS")
                cols = st.columns(5)
                for i, (cat, val) in enumerate(scores.items()):
                    with cols[i]:
                        st.metric(label=cat, value=f"{val}/100")
                        st.progress(val)
                st.write("")

                # Render all category feedback
                for category, results in ai_feedback.items():
                    if category == "ATS_Score":
                        continue
                    st.markdown(f"### 🎗️ {category}")
                    positives = results.get("Positives", [])
                    negatives = results.get("Negatives", [])
                    for pos in positives:
                        st.success(pos)
                    for neg in negatives:
                        st.warning(neg)
                
                st.divider()
                st.write("")
                st.info("""Chúng tôi khuyên bạn nên sử dụng thêm các công cụ phân tích ATS trực tuyến khác, vì đôi khi mỗi công cụ sẽ cung cấp những góc nhìn hữu ích khác nhau. Một số công cụ khuyên dùng được liệt kê dưới đây:""")
                cols = st.columns([1, 1, 1], vertical_alignment='center', gap='small')
                with cols[0]:
                    st.link_button("Weekday", "https://www.weekday.works/resume-checker-and-scoring-tool", use_container_width= True)
                    st.link_button("MyPerfectResume", "https://www.myperfectresume.com/resume/ats-resume-checker", use_container_width= True)
                with cols[1]:
                    st.link_button("Resume-Now", "https://www.resume-now.com/build-resume?mode=ats", use_container_width= True)
                    st.link_button("Enhancv", "https://enhancv.com/resources/resume-checker/", use_container_width= True)
                with cols[2]:
                    st.link_button("Jobscan", "https://www.jobscan.co/", use_container_width= True)
                    st.link_button("1MillionResume", "https://1millionresume.com/resume-checker", use_container_width= True)
else:
    st.info("Vui lòng tải lên CV ở trên để bắt đầu phân tích.")

# Footer
footer.render_footer("🛠️ Tối ưu hóa ATS")