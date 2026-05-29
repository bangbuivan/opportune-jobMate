import streamlit as st  # type: ignore
from builder import form_inputs, generator_standard, resume_enhancer
from analyzer.analysis_enhancer import get_gemini_api_key
import ui.render_footer as footer
import ui.render_header as header
import re
from io import BytesIO
import time # Import the time module for delays

# Page configuration
st.set_page_config(page_title="Tạo CV", page_icon="📝", layout="centered", initial_sidebar_state="collapsed")
st.logo("ui/assets/header.png", size="large", icon_image="ui/assets/logo.png")

# Header
header.render_header()

# Sidebar configuration
st.sidebar.title("📝 Tạo CV")
st.sidebar.markdown("Tạo CV chuyên nghiệp được thiết kế theo kỹ năng của bạn. Điền thông tin chi tiết và để chúng tôi giúp bạn tạo ra một bản CV nổi bật!")

# Main content
st.title("📝 Tạo CV")
st.caption("Tạo CV thân thiện với hệ thống ATS. Hãy để AI tinh chỉnh để tăng cơ hội thành công khi phỏng vấn.")
st.divider()

# Step 1: Ask how many entries user wants to give
st.header("📌 Số lượng mục cho các phần")
st.write("")
col1, col2 = st.columns([1, 1], gap="small", vertical_alignment="center")
with col1:
    num_edu = st.number_input("Số lượng mục học vấn?", 0, 10, 1, key="edu_count")
    num_proj = st.number_input("Số lượng dự án?", 0, 10, 1, key="proj_count")
with col2:
    num_exp = st.number_input("Số lượng kinh nghiệm làm việc?", 0, 10, 1, key="exp_count")
    num_cert = st.number_input("Số lượng chứng chỉ?", 0, 10, 1, key="cert_count")
st.divider()

# Gemini API Key Input and Tone Control
st.header("🤖 Tùy chọn Tối ưu hóa bằng AI")
st.write("")
gemini_api_key = get_gemini_api_key() # Get API key using the analysis enhancer module
st.write("")
selected_tone = st.selectbox(
    "Chọn giọng văn tối ưu hóa:",
    ["Professional", "Executive", "Technical", "Creative"],
    key="ai_tone_select",
    help="Chọn giọng văn cho các phần được tối ưu bằng AI (Tóm tắt, Nhiệm vụ, Dự án, Kỹ năng, Thành tựu)."
)
st.divider()

# Display dynamic form based on counts
st.header("✒️ Thông tin chi tiết của bạn")
st.write("")
with st.form("resume_form"):
    personal = form_inputs.personal_section()
    summary = form_inputs.summary_section()
    education = form_inputs.education_section(num_edu) if num_edu > 0 else []
    experience = form_inputs.experience_section(num_exp) if num_exp > 0 else []
    projects = form_inputs.project_section(num_proj) if num_proj > 0 else []
    skills = form_inputs.skills_section()
    certifications = form_inputs.certification_section(num_cert) if num_cert > 0 else []
    extras = form_inputs.additional_section()

    col_buttons = st.columns(2)
    with col_buttons[0]:
        generate_standard = st.form_submit_button("✅ Tạo CV", use_container_width=True)
    with col_buttons[1]:
        generate_ai_enhanced = st.form_submit_button("✨ Tạo CV tối ưu bằng AI", use_container_width=True)

# Validation logic before rendering resume
if generate_standard or generate_ai_enhanced:
    errors = []
    warnings = []

    # Personal Info Check
    if not personal["name"].strip():
        errors.append("❌ Yêu cầu nhập Họ và tên.")
    if not personal["email"].strip():
        errors.append("❌ Yêu cầu nhập Email.")
    elif not re.match(r"[^@]+@[^@]+\.[^@]+", personal["email"]):
        errors.append("❌ Định dạng Email không hợp lệ.")
    if not personal["phone"].strip():
        errors.append("❌ Yêu cầu nhập Số điện thoại.")
    if not personal["location"].strip():
        warnings.append("⚠️ Nên thêm Địa chỉ/Nơi cư trú.")
    if not personal["linkedin"].strip():
        warnings.append("⚠️ Nên thêm liên kết LinkedIn.")
    if not personal["github"].strip():
        warnings.append("⚠️ Nên thêm liên kết GitHub.")
    if not personal["website"].strip():
        warnings.append("⚠️ Nên thêm liên kết Trang web cá nhân.")

    # Summary Check
    if not summary.strip():
        errors.append("❌ Yêu cầu nhập Tóm tắt chuyên môn.")

    # Education Check
    for i in range (num_edu):
        if not education[i]["university"]:
            errors.append(f"❌ Yêu cầu nhập Trường học {i + 1}.")
        if not education[i]["degree"]:
            errors.append(f"❌ Yêu cầu nhập Bằng cấp {i + 1}.")
        if not education[i]["end_date"]:
            errors.append(f"❌ Yêu cầu nhập Ngày tốt nghiệp {i + 1}.")
        if not education[i]["gpa"]:
            warnings.append(f"⚠️ Nên thêm điểm trung bình GPA {i + 1}.")
        if not education[i]["coursework"].strip():
            warnings.append(f"⚠️ Nên thêm các môn học chính {i + 1}.")

    # Work Experience Check
    for i in range (num_exp):
        if not experience[i]["job_title"]:
            errors.append(f"❌ Yêu cầu nhập Vị trí công việc {i + 1}.")
        if not experience[i]["company"]:
            errors.append(f"❌ Yêu cầu nhập Công ty {i + 1}.")
        if not experience[i]["end_date"]:
            errors.append(f"❌ Yêu cầu nhập Ngày kết thúc công việc {i + 1}.")
        if not experience[i]["responsibilities"]:
            warnings.append(f"⚠️ Nên thêm Nhiệm vụ & Thử thách trong công việc {i + 1}.")
    
    # Project Check
    for i in range (num_proj):
        if not projects[i]["title"]:
            errors.append(f"❌ Yêu cầu nhập Tên dự án {i + 1}.")
        if not projects[i]["tech_stack"]:
            warnings.append(f"⚠️ Nên thêm Công nghệ sử dụng trong dự án {i + 1}.")
        if not projects[i]["link"]:
            warnings.append(f"⚠️ Nên thêm Liên kết mã nguồn dự án {i + 1}.")
        if not projects[i]["deployment"]:
            warnings.append(f"⚠️ Nên thêm Liên kết triển khai dự án {i + 1}.")
        if not projects[i]["description"].strip():
            errors.append(f"❌ Yêu cầu nhập Mô tả dự án {i + 1}.")

    # Skills Check
    if len(skills["technical"]) + len(skills["soft"]) == 0:
        errors.append("❌ Vui lòng nhập ít nhất một kỹ năng (chuyên môn hoặc mềm).")
    elif len(skills["technical"]) <= 4:
        warnings.append("⚠️ Nên thêm nhiều kỹ năng chuyên môn hơn.")
    elif len(skills["soft"]) <= 2:
        warnings.append("⚠️ Nên thêm nhiều kỹ năng mềm hơn.")
    
    # Certification Check
    for i in range (num_cert):
        if not certifications[i]["title"]:
            errors.append(f"❌ Yêu cầu nhập Tên chứng chỉ {i + 1}.")
        if not certifications[i]["issuer"]:
            warnings.append(f"⚠️ Nên thêm Tổ chức cấp chứng chỉ {i + 1}.")
        if not certifications[i]["link"]:
            warnings.append(f"⚠️ Nên thêm Liên kết chứng chỉ {i + 1}.")

    # Experience/project validation if count > 0
    if num_exp > 0 and not experience:
        errors.append("❌ Bạn đã chọn thêm kinh nghiệm làm việc nhưng không điền thông tin nào.")
    if num_proj > 0 and not projects:
        errors.append("❌ Bạn đã chọn thêm dự án nhưng không điền thông tin nào.")

    # Display errors
    if errors and warnings:
        st.markdown("<br>", unsafe_allow_html=True)
        st.error("Vui lòng khắc phục các lỗi sau trước khi tạo CV:\n\n" + "\n\n".join(f"{e}" for e in errors))
        st.write("")
        st.warning("Vui lòng cân nhắc bổ sung các thông tin sau để CV thân thiện hơn với ATS:\n\n" + "\n\n".join(f"{w}" for w in warnings))
    elif warnings:
        st.markdown("<br>", unsafe_allow_html=True)
        st.warning("Vui lòng cân nhắc bổ sung các thông tin sau để CV thân thiện hơn với ATS:\n\n" + "\n\n".join(f"{w}" for w in warnings))
    elif errors:
        st.markdown("<br>", unsafe_allow_html=True)
        st.error("Vui lòng khắc phục các lỗi sau trước khi tạo CV:\n\n" + "\n\n".join(f"{e}" for e in errors))
        st.stop()

    if not errors:
        st.divider()
        with st.spinner("AI đang tối ưu hóa CV của bạn... Quá trình này có thể mất một chút thời gian."):
            processed_personal = personal
            processed_summary = summary
            processed_education = education
            processed_skills = skills
            processed_certifications = certifications
            processed_extras = extras
            processed_experience = []
            processed_projects = []

            # Check if AI enhancement is requested but API key is missing
            if generate_ai_enhanced and not gemini_api_key:
                st.warning("Không cung cấp API key Gemini. Hệ thống sẽ tạo CV không qua tối ưu bằng AI.")
                generate_ai_enhanced = False # Disable enhancement for this run

            # Process Summary
            if generate_ai_enhanced and gemini_api_key and summary:
                processed_summary = resume_enhancer.enhance_content_with_gemini(
                    "professional summary", summary, selected_tone, gemini_api_key
                )
                time.sleep(3) # Add delay to respect API rate limits

            # Process Work Experience
            for i, exp_entry in enumerate(experience):
                current_exp = exp_entry.copy()
                
                if generate_ai_enhanced and gemini_api_key and experience[i]:
                    enhanced_resp_text = resume_enhancer.enhance_content_with_gemini(
                        "job responsibility", "\n".join(current_exp["responsibilities"]), selected_tone, gemini_api_key
                    )
                    current_exp["responsibilities"] = [line.strip() for line in enhanced_resp_text.split('\n') if line.strip()] 
                elif isinstance(current_exp["responsibilities"], list):
                    current_exp["responsibilities"] = [r.strip() for r in current_exp["responsibilities"] if r.strip()] # Clean list elements
                
                processed_experience.append(current_exp)
                if generate_ai_enhanced and gemini_api_key:
                    time.sleep(3) # Add delay after each experience enhancement

            # Process Projects
            for i, proj_entry in enumerate(projects):
                current_proj = proj_entry.copy()

                if generate_ai_enhanced and gemini_api_key and projects[i]:
                    enhanced_desc_text = resume_enhancer.enhance_content_with_gemini(
                        "project description", current_proj["description"], selected_tone, gemini_api_key
                    )
                    current_proj["description"] = [line.strip() for line in enhanced_desc_text.split('\n') if line.strip()]
                elif isinstance(current_proj["description"], str):
                    current_proj["description"] = [line.strip() for line in current_proj["description"].split('\n') if line.strip()]

                processed_projects.append(current_proj)
                if generate_ai_enhanced and gemini_api_key:
                    time.sleep(3) # Add delay after each project enhancement

            # Process Skills
            if generate_ai_enhanced and gemini_api_key and skills:
                # Combine technical and soft skills into a single string for enhancement
                all_skills_text = ", ".join(skills["technical"] + skills["soft"])
                enhanced_skills_string = resume_enhancer.enhance_content_with_gemini(
                    "skills section", all_skills_text, selected_tone, gemini_api_key
                )
                # Parse the specific output format: "Technical Skills: ..., Soft Skills: ..."
                tech_skills = []
                soft_skills = []
                lines = enhanced_skills_string.split('\n')
                for line in lines:
                    if line.startswith("Technical Skills:"):
                        tech_str = line.replace("Technical Skills:", "").strip()
                        tech_skills = [s.strip() for s in tech_str.split(',') if s.strip()]
                    elif line.startswith("Soft Skills:"):
                        soft_str = line.replace("Soft Skills:", "").strip()
                        soft_skills = [s.strip() for s in soft_str.split(',') if s.strip()]
                
                processed_skills = {"technical": tech_skills, "soft": soft_skills}
                time.sleep(3) # Add delay after skills enhancement
            else:
                # Ensure skills are lists for generator
                processed_skills["technical"] = [s.strip() for s in processed_skills["technical"] if s.strip()]
                processed_skills["soft"] = [s.strip() for s in processed_skills["soft"] if s.strip()]


            # Process Achievements
            if generate_ai_enhanced and gemini_api_key and extras["achievements"]:
                # Join all achievements into a single string for enhancement
                all_achievements_text = "\n".join(extras["achievements"])
                enhanced_achievements_string = resume_enhancer.enhance_content_with_gemini(
                    "achievements", all_achievements_text, selected_tone, gemini_api_key
                )
                processed_extras["achievements"] = [a.strip() for a in enhanced_achievements_string.split(',') if a.strip()]
            else:
                processed_extras["achievements"] = [a.strip() for a in processed_extras["achievements"] if a.strip()]


        # Assemble data dictionary for generator
        data = {
            "personal": processed_personal,
            "summary": processed_summary,
            "education": processed_education,
            "experience": processed_experience,
            "projects": processed_projects,
            "skills": processed_skills,
            "certifications": processed_certifications,
            "achievements_hobbies": processed_extras
        }

        # Generate and display resume
        try:
            docx_buffer = generator_standard.generate_structured_resume(data, "data/template.docx")
            
            if warnings:
                st.write("")
                st.success("Tạo CV thành công!")
                st.info("Vui lòng lưu ý các đề xuất sau:\n\n" + "\n\n".join(f"{w}" for w in warnings))
            else:
                st.markdown("<br>", unsafe_allow_html=True)
                st.success("Tạo CV thành công!")
            
            if generate_ai_enhanced:
                st.info("Vui lòng kiểm tra lại CV thật kỹ khi sử dụng tính năng tối ưu bằng AI. Đôi khi AI có thể tự động thêm các số liệu không thực tế.")

            st.divider()
            st.write("")
            st.download_button(
                label="Tải xuống CV (DOCX)",
                data=docx_buffer.getvalue(),
                file_name=f"{personal['name'].replace(' ', '_')}_Resume.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )

        except Exception as e:
            if warnings:
                st.write("")
                st.error(f"Đã xảy ra lỗi trong quá trình tạo CV: {e}")
                st.info("Điều này có thể do vấn đề về mẫu hoặc định dạng dữ liệu. Vui lòng kiểm tra lại thông tin đã nhập.")
            else:
                st.markdown("<br>", unsafe_allow_html=True)
                st.error(f"Đã xảy ra lỗi trong quá trình tạo CV: {e}")
                st.info("Điều này có thể do vấn đề về mẫu hoặc định dạng dữ liệu. Vui lòng kiểm tra lại thông tin đã nhập.")

# Footer
footer.render_footer("📝 Tạo CV")