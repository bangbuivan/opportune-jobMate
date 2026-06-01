import streamlit as st # type: ignore
import ui.render_footer as footer
import ui. render_header as header
import preprocessor.parser as parser
from preprocessor.skills import extract_skills_fuzzy
import preprocessor.personal_info as pf
import recommender.top_n_jobs as jobRec
from preprocessor.spacy_nlp import load_spacy_nlp_model
from recommender.ai_model import JobRecommendationSystem

@st.cache_resource
def load_ai_recommender():
    return JobRecommendationSystem("data/dataset/JobsFE.csv")

#Page configuration
st.set_page_config(page_title="Định hướng Nghề nghiệp", page_icon="💼", layout="centered", initial_sidebar_state="collapsed")
st.logo("ui/assets/header.png", size = "large", icon_image= "ui/assets/logo.png")

# Header
header.render_header()

# Sidebar configuration
st.sidebar.title("💼 Định hướng Nghề nghiệp")
st.sidebar.markdown("Nhận đề xuất công việc hàng đầu dựa trên các kỹ năng trong CV của bạn. Tải lên CV và để chúng tôi tìm kiếm các vị trí phù hợp nhất!")

# Main content
st.title("💼 Định hướng Nghề nghiệp")
st.caption("Tải lên CV của bạn để nhận đề xuất việc làm được cá nhân hóa dựa trên kỹ năng và bằng cấp của bạn.")
st.divider()
uploaded_file = st.file_uploader("Tải lên CV của bạn (PDF hoặc DOCX)", type=["pdf", "docx"])

if uploaded_file is not None:
    with st.spinner("Đang phân tích CV và trích xuất thông tin..."): # Updated spinner text
        file_type = uploaded_file.type  # MIME type

        if file_type == "application/pdf":
            extracted_text = parser.extract_text_from_pdf(uploaded_file.read())
        elif file_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            extracted_text = parser.extract_text_from_docx(uploaded_file.read())
        elif file_type == "application/msword":  # This is .doc MIME type
            st.error("Rất tiếc, định dạng tệp .doc không được hỗ trợ. Vui lòng tải lên tệp PDF hoặc DOCX.")
            st.stop()
        else:
            st.error("Định dạng tệp không hỗ trợ.")
            st.stop()

        nlp = load_spacy_nlp_model()
        
        doc = nlp(extracted_text)

        name = pf.extract_name(doc, extracted_text)
        email = pf.extract_mail(extracted_text)
        phone = pf.extract_phone(extracted_text)
        result = pf.extract_education_details(extracted_text)
        degree = result.get("degree") if result else None
        specialization = result.get("specialization") if result else None
        university = result.get("university") if result else None
        year = result.get("year") if result else None
        skills = sorted(extract_skills_fuzzy(doc))

    # Display extracted information
    st.divider()
    st.header("📄 Thông tin Trích xuất")
    st.write("")
    
    st.markdown(f"##### 👤 Họ và tên: <span style='font-weight:normal'>{name if name else 'Không thể tìm thấy họ tên — hãy thử điều chỉnh định dạng CV của bạn.'}</span>", unsafe_allow_html=True)
    st.markdown(f"##### 📧 Email: <span style='font-weight:normal'>{email if email else 'Không thể tìm thấy email — hãy đảm bảo email được viết rõ ràng.'}</span>", unsafe_allow_html=True)
    st.markdown(f"##### 📱 Số điện thoại: <span style='font-weight:normal'>{phone if phone else 'Không thể trích xuất số điện thoại — hãy viết rõ ràng số điện thoại.'}</span>", unsafe_allow_html=True)
    st.markdown(f"##### 🗞️ Bằng cấp: <span style='font-weight:normal'>{degree.title() if degree else 'Không thể xác định bằng cấp — cân nhắc viết rõ ràng hơn.'}</span>", unsafe_allow_html=True)
    st.markdown(f"##### 🧠 Chuyên ngành: <span style='font-weight:normal'>{specialization.title() if specialization else 'Không thể xác định chuyên ngành — đảm bảo chuyên ngành được ghi gần bằng cấp.'}</span>", unsafe_allow_html=True)
    st.markdown(f"##### 🏫 Trường đại học: <span style='font-weight:normal'>{university.title() if university else 'Không thể xác định trường đại học — thử viết rõ ràng tên đầy đủ của trường.'}</span>", unsafe_allow_html=True)
    st.markdown(f"##### 🎓 Năm tốt nghiệp: <span style='font-weight:normal'>{year if year else 'Không thể xác định năm tốt nghiệp — hãy sử dụng định dạng 4 chữ số như 2020.'}</span>", unsafe_allow_html=True)

    st.write("")
    st.write(f"#### 💭 Kỹ năng phát hiện:")
    st.markdown("#### " + " ".join(f":blue-badge[{skill}]" for skill in skills if skill))
    st.divider()

    st.write("### ⚙️ Động cơ Gợi ý")
    search_method = st.radio(
        "Chọn thuật toán gợi ý:", 
        ["AI Lai (Hybrid: FAISS + TF-IDF)", "So khớp Kỹ năng Cơ bản", "Tìm kiếm Ngữ nghĩa AI (Transformer)", "Tìm kiếm Từ khóa AI (TF-IDF)"]
    )
    
    hybrid_alpha = 0.5
    if search_method == "AI Lai (Hybrid: FAISS + TF-IDF)":
        st.write("Trọng số Ngữ nghĩa (Alpha):")
        hybrid_alpha = st.slider("1.0 = Chỉ dùng Ngữ nghĩa, 0.0 = Chỉ dùng Từ khóa", min_value=0.0, max_value=1.0, value=0.6, step=0.1)

    st.write("Số lượng việc làm gợi ý:")
    topNJobs = st.slider("", min_value=1, max_value=20, value=5, key="topNJobs", label_visibility="collapsed")
    st.divider()
    
    st.markdown("""
    <style>
    .job-feed-card {
        background: rgba(30, 41, 59, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 1.1rem 1.3rem;
        margin-bottom: 0.3rem;
        transition: all 0.2s ease;
    }
    .job-feed-card:hover {
        background: rgba(30, 41, 59, 0.4);
        border-color: rgba(59, 130, 246, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("## 🧭 Vị trí Công việc Đề xuất")
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("Tìm việc làm phù hợp", use_container_width=True, type="primary"):
        with st.spinner("Đang tìm kiếm việc làm phù hợp cho bạn..."):
            if search_method == "So khớp Kỹ năng Cơ bản":
                recommended_jobs = jobRec.recommend_top_jobs(skills, topNJobs)
                if recommended_jobs:
                    for idx, job in enumerate(recommended_jobs):
                        job_html = f"""
                        <div class="job-feed-card">
                            <div style="font-weight:700; color:#ffffff; font-size:1.05rem; margin-bottom:0.35rem;">{job['title']}</div>
                            <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:0.5rem;">🎯 Trùng khớp {job['match_count']} kỹ năng</div>
                            <div style="font-size:0.8rem; color:#3b82f6; font-weight:600;">🛠️ {", ".join(job['matched_skills']).title()}</div>
                        </div>
                        """
                        st.markdown(job_html, unsafe_allow_html=True)
                        if st.button("👁️ Xem chi tiết công việc", key=f"btn_basic_{idx}", use_container_width=True):
                            st.session_state.selected_job = {
                                "title": job['title'],
                                "company": "Công ty Đối tác",
                                "location": "Linh hoạt / Việt Nam",
                                "salary": "Thỏa thuận",
                                "skills": ", ".join(job['matched_skills']).title(),
                                "description": job['description'] or "Xem chi tiết nhiệm vụ và vai trò bên dưới.",
                                "requirements": "Yêu cầu có kinh nghiệm và thành thạo các kỹ năng cốt lõi: " + ", ".join(job['matched_skills']).title(),
                                "benefits": "- Môi trường năng động, thân thiện.\n- Chế độ đãi ngộ theo quy định của công ty."
                            }
                            st.session_state.selected_job_role = "CareerMatch Basic"
                            st.switch_page("pages/10_💼_Job_Detail.py")
                        st.write("")
                else:
                    st.write("Không tìm thấy việc làm nào khớp với kỹ năng của bạn.")
            else:
                st.info("Đang tải động cơ AI...")
                ai_recommender = load_ai_recommender()
                st.info("Đang phân tích CV bằng AI...")
                if "Hybrid" in search_method:
                    recommendations = ai_recommender.recommend_jobs_hybrid(extracted_text, top_n=topNJobs, alpha=hybrid_alpha)
                elif "Transformer" in search_method:
                    recommendations = ai_recommender.recommend_jobs(extracted_text, top_n=topNJobs)
                else:
                    recommendations = ai_recommender.recommend_jobs_tfidf(extracted_text, top_n=topNJobs)
                
                job_results = recommendations["recommended_jobs"]
                if job_results:
                    for idx, job in enumerate(job_results, start=1):
                        job_html = f"""
                        <div class="job-feed-card">
                            <div style="font-weight:700; color:#ffffff; font-size:1.05rem; margin-bottom:0.25rem;">Công việc {idx}: {job['position']}</div>
                            <div style="font-size:0.88rem; color:#3b82f6; font-weight:600; margin-bottom:0.35rem;">🏢 {job['workplace'].title()}</div>
                            <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.8rem; color:#94a3b8;">
                                <span>📍 {job['working_mode'].title()}</span>
                                <span style="color:#10b981; font-weight:700;">💵 Thỏa thuận</span>
                            </div>
                        </div>
                        """
                        st.markdown(job_html, unsafe_allow_html=True)
                        if st.button("👁️ Xem chi tiết công việc", key=f"btn_ai_{idx}", use_container_width=True):
                            st.session_state.selected_job = {
                                "title": job['position'],
                                "company": job['workplace'].title(),
                                "location": job['working_mode'].title(),
                                "salary": "Thỏa thuận",
                                "skills": job['requisite_skill'],
                                "description": job['job_role_and_duties'],
                                "requirements": job['requisite_skill'],
                                "benefits": "- Mức lương thỏa thuận cạnh tranh theo năng lực.\n- Được hưởng đầy đủ bảo hiểm và các chế độ đãi ngộ theo luật lao động.\n- Cơ hội thăng tiến và đào tạo phát triển nghề nghiệp nâng cao chuyên môn."
                            }
                            st.session_state.selected_job_role = "CareerMatch AI"
                            st.switch_page("pages/10_💼_Job_Detail.py")
                        st.write("")
                else:
                    st.write("Không tìm thấy việc làm nào.")

# Footer
footer.render_footer("💼 Định hướng Nghề nghiệp")