import streamlit as st

def personal_section():
    with st.expander("👤 Thông tin Cá nhân"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Họ và tên *")
            email = st.text_input("Email *")
            location = st.text_input("Địa chỉ (Khuyến nghị)")
            linkedin = st.text_input("Liên kết LinkedIn (Khuyến nghị)")
        with col2:
            title = st.text_input("Tiêu đề Nghề nghiệp")
            phone = st.text_input("Số điện thoại *")
            website = st.text_input("Trang web cá nhân (Khuyến nghị)")
            github = st.text_input("Liên kết GitHub (Khuyến nghị)")
    return {
        "name": name,
        "email": email,
        "phone": phone,
        "location": location,
        "linkedin": linkedin,
        "github": github,
        "website": website,
        "title": title
    }

def summary_section():
    with st.expander("📝 Tóm tắt chuyên môn"):
        summary = st.text_area("Tóm tắt Chuyên môn *")
    return summary

def education_section(count):
    entries = []
    with st.expander("🎓 Học vấn"):
        for i in range(count):
            st.write("")
            st.markdown(f"#### Học vấn {i + 1}")
            col1, col2 = st.columns(2)
            with col1:
                university = st.text_input(f"Trường học/Đại học *", key=f"edu_uni_{i}")
                location = st.text_input("Địa điểm", key=f"edu_loc_{i}")
                start_date = st.text_input("Ngày bắt đầu", key=f"edu_sdate_{i}")
            with col2:
                degree = st.text_input(f"Bằng cấp/Học vị *", key=f"edu_degree_{i}")
                gpa = st.text_input("Điểm trung bình GPA (Khuyến nghị)", key=f"edu_gpa_{i}")
                end_date = st.text_input("Ngày kết thúc *", key=f"edu_edate_{i}")
            coursework = st.text_area("Các môn học liên quan (Khuyến nghị)", key=f"edu_course_{i}")
            entries.append({
                "degree": degree,
                "university": university,
                "location": location,
                "start_date": start_date,
                "end_date": end_date,
                "gpa": gpa,
                "coursework": coursework
            })
    return entries

def experience_section(count):
    entries = []
    with st.expander("💼 Kinh nghiệm Làm việc"):
        for i in range(count):
            st.write("")
            st.markdown(f"#### Kinh nghiệm làm việc {i + 1}")
            job_title = st.text_input("Vị trí công việc *", key=f"exp_title_{i}")
            col1, col2 = st.columns(2)
            with col1:
                company = st.text_input("Công ty *", key=f"exp_company_{i}")
                start_date = st.text_input("Ngày bắt đầu", key=f"exp_sdate_{i}")
            with col2:
                location = st.text_input("Địa điểm", key=f"exp_loc_{i}")
                end_date = st.text_input("Ngày kết thúc *", key=f"exp_edate_{i}")
            responsibilities = st.text_area("Nhiệm vụ (mỗi nhiệm vụ một dòng) (Khuyến nghị)", key=f"exp_resp_{i}").splitlines()
            entries.append({
                "job_title": job_title,
                "company": company,
                "location": location,
                "start_date": start_date,
                "end_date": end_date,
                "responsibilities": responsibilities
            })
    return entries

def project_section(count):
    entries = []
    with st.expander("🛠️ Dự án"):
        for i in range(count):
            st.write("")
            st.markdown(f"#### Dự án {i + 1}")
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Tên dự án *", key=f"proj_title_{i}")
                tech_stack = st.text_input("Công nghệ sử dụng", key=f"proj_tech_{i}")
            with col2:
                deployment = st.text_input("Liên kết triển khai (Khuyến nghị)", key=f"proj_deploy_{i}")
                link = st.text_input("Liên kết GitHub (Khuyến nghị)", key=f"proj_link_{i}")
            description = st.text_area("Mô tả dự án *", key=f"proj_desc_{i}")
            entries.append({
                "title": title,
                "tech_stack": tech_stack,
                "deployment": deployment,
                "link": link,
                "description": description
            })
    return entries

def skills_section():
    with st.expander("🧠 Kỹ năng"):
        hard_skills = st.text_area("Kỹ năng Chuyên môn (ngăn cách bằng dấu phẩy hoặc dòng mới)").replace("\n", ",").split(",")
        soft_skills = st.text_area("Kỹ năng Mềm (ngăn cách bằng dấu phẩy hoặc dòng mới)").replace("\n", ",").split(",")
    return {
        "technical": [h.strip() for h in hard_skills if h.strip()],
        "soft": [s.strip() for s in soft_skills if s.strip()]
    }

def certification_section(count):
    entries = []
    with st.expander("📜 Chứng chỉ"):
        for i in range(count):
            st.write("")
            st.markdown(f"#### Chứng chỉ {i + 1}")
            title = st.text_input("Tên chứng chỉ *", key=f"cert_title_{i}")
            col1, col2 = st.columns(2)
            with col1:
                issuer = st.text_input("Tổ chức cấp", key=f"cert_issuer_{i}")
            with col2:
                link = st.text_input("Liên kết chứng chỉ (Khuyến nghị)", key=f"cert_link_{i}")
            entries.append({
                "title": title,
                "issuer": issuer,
                "link": link
            })
    return entries

def additional_section():
    with st.expander("🏆 Thành tựu & Sở thích"):
        achievements = st.text_area("Thành tựu (ngăn cách bằng dấu phẩy hoặc dòng mới)").replace("\n", ",").split(",")
        hobbies = st.text_area("Sở thích (ngăn cách bằng dấu phẩy hoặc dòng mới)").replace("\n", ",").split(",")
    return {
        "achievements": [a.strip() for a in achievements if a.strip()],
        "hobbies": [h.strip() for h in hobbies if h.strip()]
    }
