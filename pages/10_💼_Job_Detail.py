import streamlit as st # type: ignore
import ui.render_footer as footer
import ui.render_header as header
import urllib.parse
from data.mock_jobs_detail import mock_jobs_feed

# Page configuration
st.set_page_config(page_title="Chi tiết Công việc", page_icon="💼", layout="centered", initial_sidebar_state="collapsed")
st.logo("ui/assets/header.png", size="large", icon_image="ui/assets/logo.png")

# Header
header.render_header()

# Sidebar configuration
st.sidebar.title("💼 Chi tiết Công việc")
st.sidebar.markdown("Xem thông tin chi tiết về cơ hội việc làm tuyển chọn và kết nối trực tiếp đến các công cụ phân tích CV, viết Cover Letter và luyện phỏng vấn thử.")

# Retrieve job data
job = None
role_name = None

# 1. Try to get job from session state
if "selected_job" in st.session_state and st.session_state.selected_job:
    job = st.session_state.selected_job
    role_name = st.session_state.get("selected_job_role", "Frontend Developer")
else:
    # 2. Try to get job from query parameters
    try:
        q_role = st.query_params.get("role")
        q_idx = st.query_params.get("idx")
        if q_role and q_idx is not None:
            idx = int(q_idx)
            if q_role in mock_jobs_feed and 0 <= idx < len(mock_jobs_feed[q_role]):
                job = mock_jobs_feed[q_role][idx]
                role_name = q_role
    except Exception:
        pass

# Main UI layout
if job is None:
    st.title("💼 Không tìm thấy thông tin công việc")
    st.warning("Vui lòng quay lại Trang chủ và chọn một tin tuyển dụng để xem chi tiết.")
    if st.button("🏠 Quay lại Trang chủ", use_container_width=True):
        st.switch_page("Home.py")
else:
    # Breadcrumb/Back button
    col_back, _ = st.columns([0.3, 0.7])
    with col_back:
        if st.button("⬅️ Quay lại Trang chủ", use_container_width=True):
            st.switch_page("Home.py")

    st.write("")

    # Premium Job Header Card using custom CSS
    st.markdown(f"""
    <style>
    .job-header-card {{
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.85) 100%);
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        border-left: 4px solid #3b82f6;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        margin-bottom: 1.5rem;
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
    }}
    .job-title-text {{
        color: #ffffff;
        font-size: 1.45rem;
        font-weight: 700;
        margin-bottom: 0.4rem;
        line-height: 1.3;
    }}
    .company-text {{
        color: #3b82f6;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }}
    .badge-container {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem;
        margin-top: 0.5rem;
    }}
    .job-badge {{
        padding: 0.3rem 0.75rem;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
    }}
    .badge-loc {{
        background: rgba(139, 92, 246, 0.12);
        border: 1px solid rgba(139, 92, 246, 0.25);
        color: #a78bfa;
    }}
    .badge-sal {{
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.25);
        color: #34d399;
    }}
    .badge-skills {{
        background: rgba(245, 158, 11, 0.12);
        border: 1px solid rgba(245, 158, 11, 0.25);
        color: #fbbf24;
    }}
    </style>
    <div class="job-header-card">
        <div class="job-title-text">{job['title']}</div>
        <div class="company-text">🏢 {job['company']}</div>
        <div class="badge-container">
            <span class="job-badge badge-loc">📍 {job['location']}</span>
            <span class="job-badge badge-sal">💵 {job['salary']}</span>
            <span class="job-badge badge-skills">🛠️ {job['skills']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Job Details Section Tabs
    tab_desc, tab_req, tab_ben = st.tabs([
        "📋 Mô tả Công việc", 
        "🎯 Yêu cầu Ứng viên", 
        "🎁 Quyền lợi & Đãi ngộ"
    ])

    with tab_desc:
        st.write("")
        st.markdown(job.get('description', 'Đang cập nhật...').strip())
        
    with tab_req:
        st.write("")
        st.markdown(job.get('requirements', 'Đang cập nhật...').strip())

    with tab_ben:
        st.write("")
        st.markdown(job.get('benefits', 'Đang cập nhật...').strip())

    st.divider()

    # Premium AI Integration & Action Cards
    st.subheader("⚡ Tích hợp Công cụ Hỗ trợ Ứng tuyển AI")
    st.markdown("<p style='font-size:0.88rem; color:#94a3b8; margin-top:-0.5rem;'>Sử dụng trực tiếp thông tin mô tả của vị trí này để phân tích CV, viết Cover Letter hoặc chuẩn bị phỏng vấn.</p>", unsafe_allow_html=True)

    col_act1, col_act2 = st.columns(2, gap="medium")

    with col_act1:
        with st.container(border=True):
            st.markdown("#### 🎯 So khớp & Đánh giá CV")
            st.write("Kiểm tra xem CV của bạn đáp ứng được bao nhiêu % yêu cầu của công việc này và tìm kỹ năng còn thiếu.")
            st.write("")
            if st.button("So khớp CV ngay ➔", key="action_jobmatch", use_container_width=True, type="primary"):
                # Pre-fill JobMatcher data
                jd_full_text = f"Vị trí: {job['title']}\nCông ty: {job['company']}\nĐịa điểm: {job['location']}\nMức lương: {job['salary']}\nKỹ năng chính: {job['skills']}\n\n=== MÔ TẢ CÔNG VIỆC ===\n{job.get('description', '')}\n\n=== YÊU CẦU ===\n{job.get('requirements', '')}"
                st.session_state.jobmatcher_jd_tab_selected = 1  # Select "Paste JD" tab
                st.session_state.jobmatcher_jd_pasted_text = jd_full_text
                st.switch_page("pages/2_🔎_JobMatcher.py")

        st.write("")

        with st.container(border=True):
            st.markdown("#### ✉️ Tạo Cover Letter")
            st.write("Soạn thảo một bức thư ứng tuyển (Cover Letter) được cá nhân hóa hoàn toàn phù hợp với vị trí này.")
            st.write("")
            if st.button("Viết Cover Letter ➔", key="action_coverletter", use_container_width=True):
                # Pre-fill Cover Letter data
                jd_full_text = f"Vị trí: {job['title']}\nCông ty: {job['company']}\n\n=== MÔ TẢ CÔNG VIỆC ===\n{job.get('description', '')}\n\n=== YÊU CẦU ===\n{job.get('requirements', '')}"
                st.session_state.cl_jd_text = jd_full_text
                st.switch_page("pages/7_✉️_Cover_Letter.py")

    with col_act2:
        with st.container(border=True):
            st.markdown("#### 🎙️ Luyện Phỏng vấn Thử AI")
            st.write("Mô phỏng buổi phỏng vấn thử với các câu hỏi chuyên môn và tình huống thực tế dành riêng cho công việc này.")
            st.write("")
            if st.button("Luyện Phỏng vấn ngay ➔", key="action_interview", use_container_width=True, type="primary"):
                # Pre-fill Interview Prep data
                jd_full_text = f"Vị trí: {job['title']}\nCông ty: {job['company']}\n\n=== MÔ TẢ CÔNG VIỆC ===\n{job.get('description', '')}\n\n=== YÊU CẦU ===\n{job.get('requirements', '')}"
                st.session_state.ip_jd_text_input = jd_full_text
                st.session_state.ip_step = "setup"  # Go to setup step
                st.switch_page("pages/8_🎙️_Interview_Prep.py")

        st.write("")

        with st.container(border=True):
            st.markdown("#### 📚 Bổ sung Kỹ năng (SkillBridge)")
            st.write("So sánh kỹ năng của bạn đối với vị trí này và tìm kiếm tài liệu tự học trực tuyến phù hợp.")
            st.write("")
            if st.button("Thu hẹp khoảng cách ➔", key="action_skillbridge", use_container_width=True):
                st.switch_page("pages/4_📚_SkillBridge.py")

st.divider()

# Footer
footer.render_footer("💼 Chi tiết Công việc")
