import streamlit as st
import ui.render_footer as footer
import ui.render_header as header

# Page configuration
st.set_page_config(page_title="Home", page_icon="🏠", layout="centered", initial_sidebar_state="collapsed")
st.logo("ui/assets/header.png", size = "large", icon_image= "ui/assets/logo.png")

# Sidebar configuration
st.sidebar.title("CareerForge AI")
st.sidebar.markdown("Chào mừng bạn đến với Bộ công cụ Hỗ trợ Nghề nghiệp CareerForge AI!")

# Diagnostics panel in sidebar
import os
has_embeddings = os.path.exists("data/dataset/job_embeddings.npy")
st.sidebar.divider()
st.sidebar.subheader("⚙️ Trạng thái Hệ thống")
st.sidebar.markdown(f"- **Động cơ NLP spaCy**: `Hoạt động` 🟢")
st.sidebar.markdown(f"- **Chỉ mục Ngữ nghĩa FAISS**: `{'Đã tải' if has_embeddings else 'Chưa tải'}` 🟢")
st.sidebar.markdown(f"- **Lõi Gemini AI**: `Sẵn sàng dự phòng` 🟢")

# Header
header.render_header()

# Intro Section
st.title("👋 Chào mừng bạn đến với CareerForge AI")
st.caption("Trao quyền cho người tìm việc bằng công nghệ tối ưu hóa CV và mô phỏng phỏng vấn thử bằng AI.")

# Analytics & Dashboard Section
st.divider()
st.subheader("📊 Bảng điều khiển & Thống kê Thị trường IT")

# Inject Custom CSS for premium metrics grid and estimator
st.markdown("""
<style>
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1.2rem;
    margin: 0.8rem 0 1.8rem 0;
}
.metric-card {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0.75) 100%);
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    border-right: 1px solid rgba(255, 255, 255, 0.08);
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 125px;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
}
.metric-card.sal-card { border-left: 4px solid #10b981; --accent-glow: rgba(16, 185, 129, 0.15); }
.metric-card.comp-card { border-left: 4px solid #ef4444; --accent-glow: rgba(239, 68, 68, 0.15); }
.metric-card.work-card { border-left: 4px solid #8b5cf6; --accent-glow: rgba(139, 92, 246, 0.15); }
.metric-card.ats-card { border-left: 4px solid #f59e0b; --accent-glow: rgba(245, 158, 11, 0.15); }
.metric-card.port-card { border-left: 4px solid #06b6d4; --accent-glow: rgba(6, 182, 212, 0.15); }
.metric-card.skill-card { border-left: 4px solid #ec4899; --accent-glow: rgba(236, 72, 153, 0.15); }

.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 25px var(--accent-glow, rgba(59, 130, 246, 0.25));
    border-top-color: rgba(255, 255, 255, 0.15);
    border-right-color: rgba(255, 255, 255, 0.15);
}
.metric-header-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    margin-bottom: 0.2rem;
}
.metric-header {
    color: #94a3b8;
    font-size: 0.85rem;
    font-weight: 600;
    line-height: 1.3;
    white-space: normal !important;
    word-break: break-word !important;
}
.metric-value {
    color: #ffffff;
    font-size: 1.4rem;
    font-weight: 700;
    line-height: 1.25;
    margin: 0.3rem 0;
    white-space: normal !important;
    word-break: break-word !important;
    overflow-wrap: break-word !important;
    text-overflow: clip !important;
    overflow: visible !important;
}
.metric-delta {
    font-size: 0.78rem;
    font-weight: 600;
    color: #10b981;
    margin-top: 0.1rem;
    line-height: 1.3;
    white-space: normal !important;
    word-break: break-word !important;
}
.metric-delta.info {
    color: #3b82f6;
}
.metric-icon {
    width: 20px;
    height: 20px;
    flex-shrink: 0;
}
.skill-pills-container {
    display: flex;
    flex-wrap: wrap;
    gap: 0.8rem;
    margin: 0.8rem 0 1.8rem 0;
}
.skill-pill {
    padding: 0.35rem 0.8rem;
    border-radius: 50px;
    font-size: 0.8rem;
    font-weight: 600;
    transition: all 0.2s ease;
    cursor: default;
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
}
.skill-pill:hover {
    transform: translateY(-2px);
}
.skill-pill-green {
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.25);
    color: #10b981;
}
.skill-pill-blue {
    background: rgba(59, 130, 246, 0.12);
    border: 1px solid rgba(59, 130, 246, 0.25);
    color: #3b82f6;
}
.skill-pill-purple {
    background: rgba(139, 92, 246, 0.12);
    border: 1px solid rgba(139, 92, 246, 0.25);
    color: #8b5cf6;
}
.skill-pill-cyan {
    background: rgba(6, 182, 212, 0.12);
    border: 1px solid rgba(6, 182, 212, 0.25);
    color: #06b6d4;
}
.skill-pill-pink {
    background: rgba(236, 72, 153, 0.12);
    border: 1px solid rgba(236, 72, 153, 0.25);
    color: #ec4899;
}
.skill-pill-orange {
    background: rgba(245, 158, 11, 0.12);
    border: 1px solid rgba(245, 158, 11, 0.25);
    color: #f59e0b;
}

.estimator-card {
    background: rgba(30, 41, 59, 0.35);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 1.3rem;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    margin-bottom: 1rem;
}
.estimator-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    padding: 0.55rem 0;
}
.estimator-row:last-child {
    border-bottom: none;
}
.estimator-label {
    color: #94a3b8;
    font-size: 0.85rem;
    font-weight: 500;
}
.estimator-val {
    color: #ffffff;
    font-size: 0.98rem;
    font-weight: 600;
    text-align: right;
}
.job-feed-card {
    background: rgba(30, 41, 59, 0.25);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    padding: 0.85rem 1.1rem;
    margin-bottom: 0.7rem;
    transition: all 0.2s ease;
}
.job-feed-card:hover {
    background: rgba(30, 41, 59, 0.4);
    border-color: rgba(59, 130, 246, 0.3);
}
.booster-card {
    background: rgba(245, 158, 11, 0.04);
    border-left: 3px solid #f59e0b;
    border-radius: 6px;
    padding: 0.85rem;
    margin-bottom: 0.7rem;
}
.booster-header {
    color: #f59e0b;
    font-weight: 700;
    font-size: 0.88rem;
    margin-bottom: 0.25rem;
    display: flex;
    align-items: center;
    gap: 0.3rem;
}
.booster-body {
    color: #cbd5e1;
    font-size: 0.85rem;
    line-height: 1.35;
}

@media (max-width: 768px) {
    .metrics-grid {
        grid-template-columns: 1fr;
    }
}
</style>
""", unsafe_allow_html=True)

# 1. Labor Market Overview
st.markdown("##### 📈 Tổng quan Thị trường Lao động (Ngành IT)")
html_market = """
<div class="metrics-grid">
    <div class="metric-card sal-card">
        <div class="metric-header-container">
            <div class="metric-header">Mức Lương Trung Bình</div>
            <svg class="metric-icon" style="color: #10b981; filter: drop-shadow(0 0 4px rgba(16, 185, 129, 0.4));" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        </div>
        <div class="metric-value">1,450 USD/tháng</div>
        <div class="metric-delta">↑ +6.5% Tăng trưởng</div>
    </div>
    <div class="metric-card comp-card">
        <div class="metric-header-container">
            <div class="metric-header">Tỷ Lệ Cạnh Tranh</div>
            <svg class="metric-icon" style="color: #ef4444; filter: drop-shadow(0 0 4px rgba(239, 68, 68, 0.4));" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z"></path></svg>
        </div>
        <div class="metric-value">28 CV / Tin đăng</div>
        <div class="metric-delta">Mật độ cạnh tranh cao</div>
    </div>
    <div class="metric-card work-card">
        <div class="metric-header-container">
            <div class="metric-header">Hình Thức Làm Việc</div>
            <svg class="metric-icon" style="color: #8b5cf6; filter: drop-shadow(0 0 4px rgba(139, 92, 246, 0.4));" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"></path></svg>
        </div>
        <div class="metric-value">Hybrid & Remote</div>
        <div class="metric-delta">Chiếm 58% tin đăng</div>
    </div>
</div>
"""
st.markdown(html_market, unsafe_allow_html=True)

# 2. CareerForge Statistics
st.markdown("##### 💼 Thống kê Hệ thống CareerForge")
html_cf = """
<div class="metrics-grid">
    <div class="metric-card ats-card">
        <div class="metric-header-container">
            <div class="metric-header">Độ Tương Thích ATS</div>
            <svg class="metric-icon" style="color: #f59e0b; filter: drop-shadow(0 0 4px rgba(245, 158, 11, 0.4));" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        </div>
        <div class="metric-value">75% - 80%</div>
        <div class="metric-delta">↑ Tăng 3% so với 2025</div>
    </div>
    <div class="metric-card port-card">
        <div class="metric-header-container">
            <div class="metric-header">Cổng Tuyển Dụng</div>
            <svg class="metric-icon" style="color: #06b6d4; filter: drop-shadow(0 0 4px rgba(6, 182, 212, 0.4));" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4a2 2 0 012 2v2M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V9a2 2 0 00-2-2h-2M10 11a1 1 0 100-2 1 1 0 000 2zm0 4a1 1 0 100-2 1 1 0 000 2zm4-4a1 1 0 100-2 1 1 0 000 2zm0 4a1 1 0 100-2 1 1 0 000 2z"></path></svg>
        </div>
        <div class="metric-value">5 Kênh Lớn</div>
        <div class="metric-delta info">Đồng bộ thời gian thực</div>
    </div>
    <div class="metric-card skill-card">
        <div class="metric-header-container">
            <div class="metric-header">Kỹ Năng Hàng Đầu</div>
            <svg class="metric-icon" style="color: #ec4899; filter: drop-shadow(0 0 4px rgba(236, 72, 153, 0.4));" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path></svg>
        </div>
        <div class="metric-value">Python, SQL, JS</div>
        <div class="metric-delta">Tần suất xuất hiện cao</div>
    </div>
</div>
"""
st.markdown(html_cf, unsafe_allow_html=True)

st.write("")

# Market data definitions
market_roles_data = {
    'Frontend Developer': {
        'Junior': {'salary': '600 - 1,100 USD/tháng', 'competition': 'Trung bình', 'growth': '+8.5%', 'skills': 'React, JavaScript, CSS/HTML, TailwindCSS, Git', 'actions': 'Tập trung xây dựng portfolio cá nhân và tối ưu hóa hiệu suất giao diện.'},
        'Mid-level': {'salary': '1,100 - 2,000 USD/tháng', 'competition': 'Cao', 'growth': '+10.2%', 'skills': 'TypeScript, Next.js, Redux, Performance Tuning, Unit Testing', 'actions': 'Bổ sung các kỹ năng tối ưu hóa Web Vitals và kiến thức về CI/CD.'},
        'Senior/Lead': {'salary': '2,000 - 3,500 USD/tháng', 'competition': 'Rất cao', 'growth': '+12.4%', 'skills': 'Architecture design, Micro-frontends, Security, System Design, Team Leadership', 'actions': 'Tìm hiểu các mô hình kiến trúc Micro-frontends và nâng cao kỹ năng lãnh đạo kỹ thuật.'}
    },
    'Backend Developer': {
        'Junior': {'salary': '650 - 1,200 USD/tháng', 'competition': 'Cao', 'growth': '+9.2%', 'skills': 'Node.js/Python, SQL Databases, REST API, Git, Basic Docker', 'actions': 'Nắm vững kiến trúc cơ sở dữ liệu quan hệ và cách tối ưu hóa các câu truy vấn.'},
        'Mid-level': {'salary': '1,200 - 2,300 USD/tháng', 'competition': 'Cao', 'growth': '+11.8%', 'skills': 'Golang/Java/FastAPI, Redis, Docker, NoSQL, Message Brokers (RabbitMQ/Kafka)', 'actions': 'Tìm hiểu về xử lý bất đồng bộ, lập lịch tác vụ nền, và thiết kế hệ thống phân tán.'},
        'Senior/Lead': {'salary': '2,300 - 4,000 USD/tháng', 'competition': 'Rất cao', 'growth': '+14.5%', 'skills': 'System Design, Microservices, Kubernetes, Cloud Architecture (AWS/GCP), High Availability', 'actions': 'Tập trung vào tối ưu hóa chi phí đám mây, bảo mật hệ thống và kiến trúc Microservices.'}
    },
    'Fullstack Developer': {
        'Junior': {'salary': '700 - 1,300 USD/tháng', 'competition': 'Cao', 'growth': '+11.0%', 'skills': 'React, Node.js, Express, MongoDB/PostgreSQL, Git', 'actions': 'Tập trung vào khả năng tự xây dựng ứng dụng hoàn chỉnh từ đầu đến cuối.'},
        'Mid-level': {'salary': '1,300 - 2,500 USD/tháng', 'competition': 'Cao', 'growth': '+12.5%', 'skills': 'Next.js, NestJS/Django, Docker, Redis, RESTful/GraphQL APIs', 'actions': 'Học cách thiết kế API chuẩn RESTful, tích hợp cơ chế phân quyền (OAuth/JWT) và tự động hóa CI/CD.'},
        'Senior/Lead': {'salary': '2,500 - 4,500 USD/tháng', 'competition': 'Rất cao', 'growth': '+15.2%', 'skills': 'Cloud Deployments, System Architecture, Performance Tuning, Security Audit, Agile/Scrum', 'actions': 'Nâng cao khả năng thiết kế giải pháp đám mây phức tạp và dẫn dắt đội ngũ kỹ thuật.'}
    },
    'Mobile Developer': {
        'Junior': {'salary': '600 - 1,150 USD/tháng', 'competition': 'Trung bình', 'growth': '+7.5%', 'skills': 'Flutter/React Native, Dart/JavaScript, REST APIs, Git', 'actions': 'Xây dựng ứng dụng mẫu chạy ổn định trên cả iOS và Android.'},
        'Mid-level': {'salary': '1,150 - 2,100 USD/tháng', 'competition': 'Cao', 'growth': '+9.0%', 'skills': 'Swift/Kotlin, State Management, Local Storage (SQLite/Realm), Push Notifications', 'actions': 'Tìm hiểu chuyên sâu về tối ưu hóa bộ nhớ và vòng đời của ứng dụng di động.'},
        'Senior/Lead': {'salary': '2,100 - 3,600 USD/tháng', 'competition': 'Rất cao', 'growth': '+11.5%', 'skills': 'App Store/Play Store Publishing, Architecture (MVVM/VIPER), App Performance, Security', 'actions': 'Quản lý quy trình phân phối tự động thông qua Fastlane và thiết kế kiến trúc sạch (Clean Architecture).'}
    },
    'DevOps Engineer': {
        'Junior': {'salary': '700 - 1,250 USD/tháng', 'competition': 'Trung bình', 'growth': '+13.0%', 'skills': 'Linux admin, Git, Bash scripting, CI/CD tools (Github Actions), Basic Docker', 'actions': 'Nắm vững kiến thức nền tảng về Linux và tự động hóa các tác vụ lặp lại thông qua kịch bản shell.'},
        'Mid-level': {'salary': '1,250 - 2,400 USD/tháng', 'competition': 'Cao', 'growth': '+15.5%', 'skills': 'Kubernetes, Terraform (IaC), AWS/Azure, Python, Monitoring (Prometheus/Grafana)', 'actions': 'Học cách triển khai và quản lý cụm Kubernetes trong môi trường production.'},
        'Senior/Lead': {'salary': '2,400 - 4,200 USD/tháng', 'competition': 'Cao', 'growth': '+18.2%', 'skills': 'Multi-cloud strategy, DevSecOps, Helm, GitOps (ArgoCD), Chaos Engineering', 'actions': 'Thiết kế hệ thống tự động hóa khôi phục sau thảm họa (Disaster Recovery) và tối ưu hóa hạ tầng lớn.'}
    },
    'Data Specialist': {
        'Junior': {'salary': '650 - 1,200 USD/tháng', 'competition': 'Cao', 'growth': '+10.5%', 'skills': 'Python, SQL, Pandas, PowerBI/Tableau, Statistics', 'actions': 'Tập trung rèn luyện tư duy phân tích và khả năng trực quan hóa dữ liệu có tính thuyết phục.'},
        'Mid-level': {'salary': '1,200 - 2,250 USD/tháng', 'competition': 'Cao', 'growth': '+13.0%', 'skills': 'Machine Learning models, Scikit-Learn, PySpark, Airflow, Data Pipelines', 'actions': 'Xây dựng các luồng thu thập dữ liệu (ETL/ELT) và tối ưu hóa hiệu suất mô hình học máy.'},
        'Senior/Lead': {'salary': '2,250 - 4,000 USD/tháng', 'competition': 'Rất cao', 'growth': '+16.8%', 'skills': 'Deep Learning (PyTorch/TensorFlow), MLOps, Big Data Architecture, LLM fine-tuning', 'actions': 'Triển khai quy trình MLOps khép kín và thiết kế hệ thống xử lý dữ liệu lớn thời gian thực.'}
    }
}

from data.mock_jobs_detail import mock_jobs_feed


career_boosters = {
    'Frontend Developer': [
        {'target': 'Tăng điểm ATS thêm 15%', 'action': 'Bổ dung từ khóa liên quan đến **TypeScript**, **Next.js** và **Vite** vào phần kỹ năng chuyên môn của CV.', 'page': 'pages/6_🛠️_ATS_TuneUp.py', 'btn_text': 'Tối ưu hóa ATS'},
        {'target': 'Tăng tỷ lệ gọi phỏng vấn thêm 20%', 'action': 'Thực hành trả lời các câu hỏi tình huống về **Tối ưu hóa tốc độ tải trang (Web Vitals)** và **Bảo mật Frontend**.', 'page': 'pages/8_🎙️_Interview_Prep.py', 'btn_text': 'Luyện phỏng vấn'}
    ],
    'Backend Developer': [
        {'target': 'Tăng điểm ATS thêm 12%', 'action': 'Đưa các từ khóa về **Docker**, **Redis**, **Kafka** và thiết kế API chuẩn **RESTful** vào CV.', 'page': 'pages/6_🛠️_ATS_TuneUp.py', 'btn_text': 'Tối ưu hóa ATS'},
        {'target': 'Tự tin phỏng vấn System Design (+30%)', 'action': 'Luyện tập các kịch bản thiết kế hệ thống chịu tải cao và cơ chế đồng bộ dữ liệu.', 'page': 'pages/8_🎙️_Interview_Prep.py', 'btn_text': 'Luyện phỏng vấn'}
    ],
    'Fullstack Developer': [
        {'target': 'Tăng điểm tương thích ATS thêm 18%', 'action': 'Cân bằng từ khóa giữa Client-side (React/Next) và Server-side (Node/NestJS) kèm kỹ năng deployment.', 'page': 'pages/6_🛠️_ATS_TuneUp.py', 'btn_text': 'Tối ưu hóa ATS'},
        {'target': 'Bù đắp khoảng trống kỹ năng', 'action': 'Đối chiếu kỹ năng CV của bạn với bản đồ năng lực của vị trí Fullstack để kịp thời bổ sung kiến thức.', 'page': 'pages/4_📚_SkillBridge.py', 'btn_text': 'Cầu nối Kỹ năng'}
    ],
    'Mobile Developer': [
        {'target': 'Tăng độ tin cậy của CV thêm 14%', 'action': 'Nêu bật các dự án đã phát hành lên **App Store / Play Store** hoặc các thư viện mã nguồn mở tự viết.', 'page': 'pages/5_📝_ResumeBuilder.py', 'btn_text': 'Cập nhật CV'},
        {'target': 'Tăng điểm trả lời câu hỏi hành vi', 'action': 'Luyện tập phương pháp STAR cho các tình huống giải quyết hiệu năng hoặc xung đột luồng trên mobile.', 'page': 'pages/8_🎙️_Interview_Prep.py', 'btn_text': 'Luyện phỏng vấn'}
    ],
    'DevOps Engineer': [
        {'target': 'Nhận diện khoảng trống kỹ năng cốt lõi', 'action': 'Đối chiếu CV với bản đồ năng lực DevOps (IaC, Kubernetes, CI/CD, Monitoring) để lập lộ trình học bổ sung.', 'page': 'pages/4_📚_SkillBridge.py', 'btn_text': 'Cầu nối Kỹ năng'},
        {'target': 'Tăng điểm ATS thêm 15%', 'action': 'Thêm các từ khóa **Terraform**, **GitOps**, **Prometheus** và chứng chỉ đám mây (AWS/Azure) vào CV.', 'page': 'pages/6_🛠️_ATS_TuneUp.py', 'btn_text': 'Tối ưu hóa ATS'}
    ],
    'Data Specialist': [
        {'target': 'Cải thiện mức độ phù hợp công việc (+20%)', 'action': 'So khớp CV của bạn với bản mô tả công việc (JD) vị trí Data Analyst/Scientist cụ thể để tinh chỉnh từ khóa.', 'page': 'pages/2_🔎_JobMatcher.py', 'btn_text': 'So khớp Việc làm'},
        {'target': 'Luyện phỏng vấn chuyên sâu SQL/Python', 'action': 'Thực hành các câu hỏi thuật toán xử lý dữ liệu lớn và thiết kế kho dữ liệu (Data Warehouse).', 'page': 'pages/8_🎙️_Interview_Prep.py', 'btn_text': 'Luyện phỏng vấn'}
    ]
}

# 3. Interactive Salary & Market Estimator Section
st.markdown("#### 💡 Định vị Lương & Gợi ý Sự nghiệp Tương tác")
col_est1, col_est2 = st.columns([0.45, 0.55], gap="medium")

with col_est1:
    st.markdown("<p style='font-size:0.88rem; color:#94a3b8; margin-top:-0.5rem;'>Lựa chọn vai trò công việc và kinh nghiệm của bạn để xem định vị thị trường thời gian thực.</p>", unsafe_allow_html=True)
    selected_role = st.selectbox(
        "💼 Vị trí công việc mục tiêu (Job Role)",
        list(market_roles_data.keys()),
        index=0
    )
    selected_exp = st.radio(
        "⭐ Cấp độ kinh nghiệm hiện tại",
        ["Junior", "Mid-level", "Senior/Lead"],
        horizontal=True
    )
    st.write("")

role_data = market_roles_data[selected_role][selected_exp]

with col_est2:
    estimator_html = f"""
    <div class="estimator-card">
        <h4 style="margin-top:0; color:#3b82f6; font-size:1.05rem; display:flex; align-items:center; gap:0.4rem; margin-bottom:0.8rem;">
            <svg style="width:18px; height:18px;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
            Phân tích thị trường cho {selected_role}
        </h4>
        <div class="estimator-row">
            <span class="estimator-label">💵 Lương trung bình thị trường</span>
            <span class="estimator-val" style="color:#10b981;">{role_data['salary']}</span>
        </div>
        <div class="estimator-row">
            <span class="estimator-label">🔥 Mức độ cạnh tranh hồ sơ</span>
            <span class="estimator-val" style="color:#ef4444;">{role_data['competition']}</span>
        </div>
        <div class="estimator-row">
            <span class="estimator-label">📈 Tăng trưởng nhu cầu tuyển dụng</span>
            <span class="estimator-val" style="color:#3b82f6;">{role_data['growth']}</span>
        </div>
        <div class="estimator-row" style="flex-direction:column; align-items:flex-start; gap:0.25rem;">
            <span class="estimator-label" style="margin-bottom:0.1rem;">🛠️ Kỹ năng cốt lõi bắt buộc:</span>
            <span class="estimator-val" style="text-align:left; font-size:0.85rem; color:#cbd5e1; font-weight:normal; line-height:1.4;">{role_data['skills']}</span>
        </div>
    </div>
    """
    st.markdown(estimator_html, unsafe_allow_html=True)

# 4. Career Booster & Hot Jobs section
col_boost, col_jobs = st.columns([0.5, 0.5], gap="medium")

with col_boost:
    st.markdown("##### 🚀 Hành động tăng tốc sự nghiệp")
    boost_items = career_boosters[selected_role]
    for item in boost_items:
        boost_html = f"""
        <div class="booster-card">
            <div class="booster-header">
                <svg style="width:15px; height:15px;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                {item['target']}
            </div>
            <div class="booster-body">{item['action']}</div>
        </div>
        """
        st.markdown(boost_html, unsafe_allow_html=True)
        st.page_link(item['page'], label=item['btn_text'], icon="👉", use_container_width=True)

with col_jobs:
    st.markdown("##### 💼 Tin tuyển dụng Nổi bật (Hot Jobs)")
    jobs = mock_jobs_feed[selected_role]
    import urllib.parse
    for idx, job in enumerate(jobs):
        role_enc = urllib.parse.quote(selected_role)
        job_html = f"""
        <a href="/Job_Detail?role={role_enc}&idx={idx}" target="_self" style="text-decoration: none; color: inherit;">
            <div class="job-feed-card" style="cursor: pointer; margin-bottom: 0.3rem;">
                <div style="font-weight:700; color:#ffffff; font-size:0.88rem; margin-bottom:0.15rem;">{job['title']}</div>
                <div style="font-size:0.8rem; color:#3b82f6; font-weight:600; margin-bottom:0.35rem;">🏢 {job['company']}</div>
                <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.75rem; color:#94a3b8;">
                    <span>📍 {job['location']}</span>
                    <span style="color:#10b981; font-weight:700;">💵 {job['salary']}</span>
                </div>
            </div>
        </a>
        """
        st.markdown(job_html, unsafe_allow_html=True)
        if st.button("👁️ Xem chi tiết", key=f"btn_job_det_{role_enc}_{idx}", use_container_width=True):
            st.session_state.selected_job = job
            st.session_state.selected_job_role = selected_role
            st.switch_page("pages/10_💼_Job_Detail.py")
        st.write("")

st.write("")

# 5. Charts Section (Side-by-Side)
import pandas as pd
import altair as alt

job_demand_data = pd.DataFrame({
    'Role': [
        'Fullstack Developer', 
        'Backend Developer', 
        'Software Engineer', 
        'Frontend Developer', 
        'DevOps Engineer', 
        'Data Scientist', 
        'Data Analyst'
    ],
    'Nhu cầu Tuyển dụng (%)': [85, 80, 75, 70, 65, 55, 50]
})

geo_dist_data = pd.DataFrame({
    'Địa điểm': ['TP. Hồ Chí Minh', 'Hà Nội', 'Đà Nẵng', 'Từ xa (Remote)'],
    'Tỷ lệ tuyển dụng (%)': [52, 38, 8, 2]
})

col_chart1, col_chart2 = st.columns([0.55, 0.45], gap="medium")

with col_chart1:
    with st.container(border=True):
        st.markdown("<h5 style='margin-top:0;'>📈 Nhu cầu Tuyển dụng các Vai trò chính</h5>", unsafe_allow_html=True)
        chart_data = job_demand_data.sort_values(by='Nhu cầu Tuyển dụng (%)', ascending=True)
        
        chart = alt.Chart(chart_data).mark_bar(
            color='#3b82f6',  
            cornerRadiusEnd=4,
            height=14
        ).encode(
            x=alt.X('Nhu cầu Tuyển dụng (%):Q', title='Nhu cầu (%)', scale=alt.Scale(domain=[0, 100])),
            y=alt.Y('Role:N', title='', sort='-x'),  
            tooltip=['Role', 'Nhu cầu Tuyển dụng (%)']
        ).properties(
            height=210
        ).configure_axis(
            labelFontSize=10,
            titleFontSize=10,
            grid=False
        ).configure_view(
            strokeWidth=0
        )
        st.altair_chart(chart, use_container_width=True)

with col_chart2:
    with st.container(border=True):
        st.markdown("<h5 style='margin-top:0;'>📍 Phân bổ Việc làm theo Địa lý</h5>", unsafe_allow_html=True)
        
        donut_chart = alt.Chart(geo_dist_data).mark_arc(innerRadius=45, outerRadius=75).encode(
            theta=alt.Theta(field="Tỷ lệ tuyển dụng (%)", type="quantitative"),
            color=alt.Color(field="Địa điểm", type="nominal", scale=alt.Scale(
                domain=['TP. Hồ Chí Minh', 'Hà Nội', 'Đà Nẵng', 'Từ xa (Remote)'],
                range=['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6']
            ), legend=alt.Legend(
                orient="bottom", 
                direction="horizontal",
                labelFontSize=9,
                symbolSize=80,
                rowPadding=3
            )),
            tooltip=['Địa điểm', 'Tỷ lệ tuyển dụng (%)']
        ).properties(
            height=210
        ).configure_view(
            strokeWidth=0
        )
        st.altair_chart(donut_chart, use_container_width=True)

# 6. Trending Skills Section
st.markdown("##### 🔥 Xu hướng Kỹ năng Công nghệ đang lên")
st.markdown("""
<div class="skill-pills-container">
    <span class="skill-pill skill-pill-green">FastAPI (+14.2% ↑)</span>
    <span class="skill-pill skill-pill-blue">Next.js (+9.8% ↑)</span>
    <span class="skill-pill skill-pill-purple">PyTorch (+18.5% ↑)</span>
    <span class="skill-pill skill-pill-cyan">Kubernetes (+12.3% ↑)</span>
    <span class="skill-pill skill-pill-pink">Docker (+10.5% ↑)</span>
    <span class="skill-pill skill-pill-orange">TypeScript (+11.4% ↑)</span>
</div>
""", unsafe_allow_html=True)

# Add a clean market insight card below the chart
st.info("""
**💡 Nhận xét xu hướng thị trường:** 
- Nhóm ngành **Fullstack Developer** và **Backend Developer** tiếp tục dẫn đầu về nhu cầu tuyển dụng trong quý này.
- Các kỹ năng liên quan đến **Trí tuệ nhân tạo (AI/PyTorch)** và **Đám mây / DevOps** đang có xu hướng tăng mạnh nhất (+18.5% và +12.3%).
- Việc tối ưu hóa từ khóa chuẩn ATS giúp tăng cơ hội được các hệ thống sàng lọc tự động duyệt qua lên đến **78%**.
""")

# Features Section
st.divider()
st.subheader("❔ Công cụ nổi bật")

# Tabbed Layout or columns layout
tab_resume, tab_match, tab_prep = st.tabs(["📂 Tối ưu hóa CV", "🎯 So khớp & Dò tìm Việc làm", "🎙️ Luyện phỏng vấn"])

with tab_resume:
    col1, col2 = st.columns([0.4, 0.6], vertical_alignment="center")
    with col1:
        st.page_link("pages/5_📝_ResumeBuilder.py", label = "Tạo CV", icon = "📝", use_container_width=True)
    with col2:
        st.markdown("Tạo CV chuyên nghiệp được cá nhân hóa theo kỹ năng của bạn.")

    col3, col4 = st.columns([0.4, 0.6], vertical_alignment="center")
    with col3:
        st.page_link("pages/6_🛠️_ATS_TuneUp.py", label = "Tối ưu hóa ATS", icon = "🛠️", use_container_width=True)
    with col4:
        st.markdown("Cải thiện độ tương thích ATS và nhận các mẹo tối ưu hóa CV.")

    col5, col6 = st.columns([0.4, 0.6], vertical_alignment="center")
    with col5:
        st.page_link("pages/7_✉️_Cover_Letter.py", label = "Viết Thư ứng tuyển", icon = "✉️", use_container_width=True)
    with col6:
        st.markdown("Tạo thư ứng tuyển phù hợp với mô tả công việc mục tiêu của bạn.")

with tab_match:
    col7, col8 = st.columns([0.4, 0.6], vertical_alignment="center")
    with col7:
        st.page_link("pages/1_📡_JobRadar.py", label = "Dò Tìm Việc làm", icon = "📡", use_container_width=True)
    with col8:
        st.markdown("Tìm kiếm danh sách việc làm trên nhiều nền tảng tại một nơi.")

    col9, col10 = st.columns([0.4, 0.6], vertical_alignment="center")
    with col9:
        st.page_link("pages/2_🔎_JobMatcher.py", label = "So Khớp Việc làm", icon = "🔎", use_container_width=True)
    with col10:
        st.markdown("Kiểm tra mức độ phù hợp của CV với mô tả công việc cụ thể.")

    col11, col12 = st.columns([0.4, 0.6], vertical_alignment="center")
    with col11:
        st.page_link("pages/3_💼_CareerMatch.py", label = "Gợi ý Nghề nghiệp", icon = "💼", use_container_width=True)
    with col12:
        st.markdown("Gợi ý các vị trí công việc phù hợp nhất dựa trên kỹ năng của bạn.")

    col13, col14 = st.columns([0.4, 0.6], vertical_alignment="center")
    with col13:
        st.page_link("pages/4_📚_SkillBridge.py", label = "Cầu nối Kỹ năng", icon = "📚", use_container_width=True)
    with col14:
        st.markdown("Xác định khoảng trống kỹ năng đối với các vai trò công việc cụ thể.")

with tab_prep:
    col15, col16 = st.columns([0.4, 0.6], vertical_alignment="center")
    with col15:
        st.page_link("pages/8_🎙️_Interview_Prep.py", label = "Luyện phỏng vấn", icon = "🎙️", use_container_width=True)
    with col16:
        st.markdown("Luyện tập các câu hỏi chuyên môn và tình huống được tùy chỉnh theo CV và mô tả công việc.")

# Sidebar hint
st.markdown("---")
st.info("📂 Chọn một thẻ ở trên để sử dụng dịch vụ hoặc dùng thanh điều hướng ở thanh bên.")

# Footer
footer.render_footer("🏠 Trang chủ")