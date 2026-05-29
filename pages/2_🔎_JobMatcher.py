import streamlit as st # type: ignore
import ui.render_footer as footer
import ui.render_header as header
import preprocessor.parser as parser
from preprocessor.skills import extract_skills_fuzzy, extract_soft_skills_fuzzy, weighted_skill_analysis
from recommender.resources import learning_resources
from preprocessor.spacy_nlp import load_spacy_nlp_model

# Page configuration
st.set_page_config(page_title="So Khớp Việc làm", page_icon="🔎", layout="centered", initial_sidebar_state="collapsed")
st.logo("ui/assets/header.png", size="large", icon_image="ui/assets/logo.png")

# Header
header.render_header()

# Sidebar configuration
st.sidebar.title("🔎 So Khớp Việc làm")
st.sidebar.markdown("Đánh giá mức độ tương thích của CV với mô tả công việc cụ thể. Tải lên cả hai tài liệu để có phân tích so khớp chi tiết!")

# Main content
st.title("🔎 So Khớp Việc làm")
st.caption("Kiểm tra mức độ phù hợp của CV với mô tả công việc mục tiêu.")
st.divider()

# Session state setup
if "resume_text_jobmatcher" not in st.session_state:
    st.session_state.resume_text_jobmatcher = None
if "jd_text_jobmatcher" not in st.session_state:
    st.session_state.jd_text_jobmatcher = None

# Resume Upload
st.subheader("CV của bạn")
resume_file = st.file_uploader("Tải lên CV của bạn (PDF hoặc DOCX)", type=["pdf", "docx"], key="jobmatcher_resume_uploader")
if resume_file:
    with st.spinner("Đang xử lý CV..."):
        file_type = resume_file.type
        if file_type == "application/pdf":
            st.session_state.resume_text_jobmatcher = parser.extract_text_from_pdf(resume_file.read())
        elif file_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            st.session_state.resume_text_jobmatcher = parser.extract_text_from_docx(resume_file.read())
        else:
            st.error("Định dạng tệp CV không hỗ trợ. Vui lòng tải lên tệp PDF hoặc DOCX.")
            st.session_state.resume_text_jobmatcher = None
            st.stop()
    st.markdown("<br>", unsafe_allow_html=True)
    st.success("Đã xử lý CV thành công!")
st.divider()

# Job Description Input
st.subheader("Mô tả Công việc Mục tiêu")

# Tabs for JD input method
tab_labels = ["📂 Tải lên Mô tả Công việc", "✍️ Dán Mô tả Công việc"]
if "jobmatcher_jd_tab_selected" not in st.session_state:
    st.session_state.jobmatcher_jd_tab_selected = 0 # Default to upload tab

selected_tab = st.radio("Chọn Phương thức Nhập Mô tả Công việc", tab_labels, index=st.session_state.jobmatcher_jd_tab_selected, horizontal=True, key="jobmatcher_jd_input_method_radio")

# Update session state if tab changed
if selected_tab != tab_labels[st.session_state.jobmatcher_jd_tab_selected]:
    st.session_state.jobmatcher_jd_tab_selected = tab_labels.index(selected_tab)
    st.rerun()

jd_text = None
if selected_tab == "📂 Tải lên Mô tả Công việc":
    st.write("")
    jd_file = st.file_uploader("Tải lên Mô tả Công việc (PDF hoặc DOCX)", type=["pdf", "docx"], key="jobmatcher_jd_uploader")
    if jd_file:
        with st.spinner("Đang xử lý mô tả công việc..."):
            jd_type = jd_file.type
            if jd_type == "application/pdf":
                jd_text = parser.extract_text_from_pdf(jd_file.read())
            elif jd_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
                jd_text = parser.extract_text_from_docx(jd_file.read())
            else:
                st.error("Định dạng tệp mô tả công việc không hỗ trợ. Vui lòng tải lên tệp PDF hoặc DOCX.")
                jd_text = None
                st.stop()
        st.markdown("<br>", unsafe_allow_html=True)
        st.success("Đã xử lý Mô tả Công việc thành công!")

elif selected_tab == "✍️ Dán Mô tả Công việc":
    st.write("")
    pasted_text = st.text_area("Dán Mô tả Công việc tại đây:", height=300, key="jobmatcher_jd_pasted_text")
    if pasted_text:
        jd_text = pasted_text


# Main Analysis Logic
if st.session_state.resume_text_jobmatcher and jd_text:
    st.divider()
    st.subheader("Kết quả Phân tích So khớp")

    with st.spinner("Đang thực hiện phân tích so khớp..."):
        nlp = load_spacy_nlp_model()

        resume_doc = nlp(st.session_state.resume_text_jobmatcher)
        jd_doc = nlp(jd_text)

        # Skill Matching
        resume_hard_skills = set(extract_skills_fuzzy(resume_doc))
        resume_soft_skills = set(extract_soft_skills_fuzzy(resume_doc))
        jd_hard_skills_weighted, jd_soft_skills = weighted_skill_analysis(jd_text, nlp)

        # jd_hard_skills_weighted is a dictionary, so .keys() is appropriate here
        jd_hard_skills = set(jd_hard_skills_weighted.keys())

        matched_hard_skills = resume_hard_skills.intersection(jd_hard_skills)
        missing_hard_skills = jd_hard_skills.difference(resume_hard_skills)
        matched_soft_skills = resume_soft_skills.intersection(jd_soft_skills)
        missing_soft_skills = jd_soft_skills.difference(resume_soft_skills)

        # Score Generation
        total_jd_hard_weight = sum(jd_hard_skills_weighted.values())
        matched_hard_weight = sum(jd_hard_skills_weighted[s] for s in matched_hard_skills)

        hard_pct = (matched_hard_weight / total_jd_hard_weight) * 100 if total_jd_hard_weight else 0
        soft_pct = (len(matched_soft_skills) / len(jd_soft_skills)) * 100 if jd_soft_skills else 0

        # Define weighting for overall score
        hard_score_contribution = hard_pct * 0.9 # Hard skills contribute 90%
        soft_score_contribution = soft_pct * 0.1 # Soft skills contribute 10%

        final_score = round(hard_score_contribution + soft_score_contribution)

        # Categorize hard skills for display
        def categorize(skills_dict):
            core, imp, opt = [], [], []
            for s, w in skills_dict.items():
                if w >= 2.5: core.append(s)
                elif w >= 1.0: imp.append(s)
                else: opt.append(s)
            return sorted(core), sorted(imp), sorted(opt)

        matched_hard_core, matched_hard_imp, matched_hard_opt = categorize(
            {s: jd_hard_skills_weighted[s] for s in matched_hard_skills}
        )
        missing_hard_core, missing_hard_imp, missing_hard_opt = categorize(
            {s: jd_hard_skills_weighted[s] for s in missing_hard_skills}
        )

        # Display Results
        st.header("📊 Điểm Tương thích Công việc")
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"### Độ Tương thích Tổng quan: <span style='font-weight:normal'>{final_score}%</span>", unsafe_allow_html=True)
        st.progress(final_score / 100)
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(f"### 🧱 Khớp Kỹ năng Chuyên môn: <span style='font-weight:normal'>{round(hard_pct)}% của 90 → {round(hard_score_contribution)} điểm</span>", unsafe_allow_html=True)
        st.markdown(f"### 🎭 Khớp Kỹ năng Mềm: <span style='font-weight:normal'>{round(soft_pct)}% của 10 → {round(soft_score_contribution)} điểm</span>", unsafe_allow_html=True)
        st.write("")
        st.divider()

        def show_skills_section(label, badge_color, core_skills, important_skills, optional_skills):
            st.subheader(label)
            st.markdown("<br>", unsafe_allow_html=True)
            if core_skills:
                st.markdown(f"##### 🔐 Kỹ năng Cốt lõi: " + " ".join(f":{badge_color}-badge[{s.title()}]" for s in core_skills))
            if important_skills:
                st.markdown(f"##### 💡 Kỹ năng Quan trọng: " + " ".join(f":{badge_color}-badge[{s.title()}]" for s in important_skills))
            if optional_skills:
                st.markdown(f"##### 🧩 Kỹ năng Bổ trợ: " + " ".join(f":{badge_color}-badge[{s.title()}]" for s in optional_skills))
            if not (core_skills or important_skills or optional_skills):
                st.info(f"Không phát hiện kỹ năng chuyên môn tương ứng.")

        # Matched Skills
        st.subheader("✅ Kỹ năng Trùng khớp")
        st.markdown("<br>", unsafe_allow_html=True)
        show_skills_section("Kỹ năng Chuyên môn", "green", matched_hard_core, matched_hard_imp, matched_hard_opt)
        if matched_soft_skills:
            st.markdown(f"##### Kỹ năng Mềm: " + " ".join(f":green-badge[{s.title()}]" for s in sorted(matched_soft_skills)))
        elif not matched_soft_skills:
            st.write("")
            st.info("Không phát hiện kỹ năng mềm trùng khớp nào.")
        st.markdown("<br>", unsafe_allow_html=True)
        st.divider()

        # Missing Skills
        st.subheader("❌ Kỹ năng Còn thiếu")
        st.markdown("<br>", unsafe_allow_html=True)
        show_skills_section("Kỹ năng Chuyên môn", "red", missing_hard_core, missing_hard_imp, missing_hard_opt)
        if missing_soft_skills:
            st.markdown(f"##### Kỹ năng Mềm: " + " ".join(f":red-badge[{s.title()}]" for s in sorted(missing_soft_skills)))
        elif not missing_soft_skills:
            st.success("Bạn đã có đầy đủ kỹ năng mềm!")
        st.markdown("<br>", unsafe_allow_html=True)
        st.divider()

        # Overall recommendation based on score
        if final_score >= 80:
            st.success("✅ Độ Tương thích Xuất sắc! CV của bạn cực kỳ phù hợp với mô tả công việc này. Hãy tập trung chuẩn bị luyện phỏng vấn!")
        elif final_score >= 65:
            st.info("✨ Độ Tương thích Tốt! Bạn rất phù hợp với vị trí này. Hãy xem lại các kỹ năng còn thiếu và cân nhắc điều chỉnh CV chi tiết hơn.")
        else:
            st.warning("⚠️ Cần Cải thiện. Có một khoảng cách kỹ năng đáng kể. Hãy tập trung học tập các kỹ năng còn thiếu hoặc tối ưu hóa lại CV của bạn.")

        # Learning resources for missing skills
        st.divider()
        st.header("📚 Tài liệu Gợi ý cho Kỹ năng Còn thiếu")
        st.write("")
        all_missing_skills = list(missing_hard_skills) + list(missing_soft_skills)
        if all_missing_skills:
            learning_resources(all_missing_skills)
        else:
            st.info("Bạn đã có đầy đủ tất cả các kỹ năng thiết yếu cho vai trò này!")


# Footer
footer.render_footer("🔎 So Khớp Việc làm")