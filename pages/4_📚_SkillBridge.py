import streamlit as st # type: ignore
import ui.render_footer as footer
import ui.render_header as header
import json
import preprocessor.parser as parser
from preprocessor.skills import extract_skills_fuzzy
from recommender.resources import learning_resources
from preprocessor.spacy_nlp import load_spacy_nlp_model
from analyzer.analysis_enhancer import get_gemini_api_key
from builder.ai_features import generate_ai_roadmap

#Page configuration
st.set_page_config(page_title="Cầu nối Kỹ năng", page_icon="📚", layout="centered", initial_sidebar_state="collapsed")
st.logo("ui/assets/header.png", size = "large", icon_image= "ui/assets/logo.png")

# Header
header.render_header()

# Sidebar configuration
st.sidebar.title("📚 Cầu nối Kỹ năng")
st.sidebar.markdown("Xác định khoảng cách kỹ năng đối với các vai trò công việc cụ thể. Tải lên CV và chọn một công việc để xem các kỹ năng bạn cần phát triển!")

# Main content
st.title("📚 Cầu nối Kỹ năng")
st.caption("Tìm hiểu vị trí hiện tại của bạn — và những gì bạn cần học để thăng tiến.")
st.divider()

# Get API key
api_key = get_gemini_api_key()

resume_file = st.file_uploader("Tải lên CV của bạn (PDF hoặc DOCX)", type=["pdf", "docx"])

# Load Job Roles
@st.cache_data
def load_job_roles():
    with open("data/dataset/job_to_skill.json", "r") as f:
        return json.load(f)

job_skills_map = load_job_roles()
available_roles = sorted(job_skills_map.keys())

# Resume Extraction and Analysis
if resume_file:
    with st.spinner("Đang phân tích CV và trích xuất kỹ năng..."):
        if resume_file.type == "application/pdf":
            resume_text = parser.extract_text_from_pdf(resume_file.read())
        elif resume_file.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            resume_text = parser.extract_text_from_docx(resume_file.read())
        else:
            st.error("Định dạng tệp không hỗ trợ. Vui lòng tải lên tệp PDF hoặc DOCX.")
            st.stop()
        
        # Load the SpaCy model using the cached function
        nlp = load_spacy_nlp_model()

        resume_doc = nlp(resume_text)
        extracted_skills = set(extract_skills_fuzzy(resume_doc))

    # Role Selection
    st.divider()
    selected_role = st.selectbox("Chọn vị trí công việc mục tiêu:", available_roles)
    if selected_role:
        required_skills = set(job_skills_map[selected_role])
        matched_skills = extracted_skills & required_skills
        missing_skills = required_skills - extracted_skills

        st.divider()
        st.markdown(f"## 🎯 Mức độ khớp Kỹ năng với vị trí: {selected_role}")
        st.markdown("<br><br>", unsafe_allow_html=True)

        st.markdown(f"#### ✅ Kỹ năng Trùng khớp: <span style='font-weight:normal'>({len(matched_skills)}/{len(required_skills)})</span>", unsafe_allow_html=True)
        st.markdown("#### " + " ".join(f":green-badge[{skill}]" for skill in sorted(matched_skills)) or "_Không có_")
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(f"#### 💡 Kỹ năng Đề xuất Học thêm: <span style='font-weight:normal'>({len(missing_skills)} kỹ năng)</span>", unsafe_allow_html=True)
        st.markdown("#### " + " ".join(f":blue-badge[{skill}]" for skill in sorted(missing_skills)) or "_Không có_")

        # Visual Career Roadmap
        st.divider()
        st.markdown("### 🗺️ Sơ đồ Phân vùng Kiến thức & Lộ trình Học tập")
        
        with st.spinner("Đang xây dựng lộ trình học tập của bạn..."):
            roadmap = generate_ai_roadmap(selected_role, missing_skills, api_key)

        if roadmap:
            if "roadmap_ticks" not in st.session_state:
                st.session_state.roadmap_ticks = {}
            # Helper to check matching completion
            def is_skill_completed(title, sub_tasks):
                matched = [s.lower() for s in matched_skills]
                text_to_match = (title + " " + " ".join(sub_tasks)).lower()
                return any(skill in text_to_match for skill in matched)

            # Custom styling for interactive mind map in Streamlit
            css_style = """
            <style>
            .st-roadmap-mindmap {
                display: flex;
                flex-direction: column;
                align-items: center;
                width: 100%;
                position: relative;
                padding: 1.5rem 0;
            }
            .st-roadmap-root {
                background: linear-gradient(135deg, #0d9488, #d97706);
                color: white;
                font-size: 1.1rem;
                font-weight: 800;
                padding: 0.6rem 1.8rem;
                border-radius: 9999px;
                text-align: center;
                box-shadow: 0 4px 10px rgba(13, 148, 136, 0.3);
                z-index: 10;
                margin-bottom: 2.5rem;
                position: relative;
            }
            .st-roadmap-root::after {
                content: '';
                position: absolute;
                bottom: -2.5rem;
                left: 50%;
                transform: translateX(-50%);
                width: 2px;
                height: 2.5rem;
                border-left: 2px dotted #0d9488;
                z-index: 1;
            }
            .st-roadmap-branches-wrapper {
                display: flex;
                justify-content: space-around;
                width: 100%;
                position: relative;
                padding-top: 1.5rem;
            }
            .st-roadmap-branches-wrapper::before {
                content: '';
                position: absolute;
                top: 0;
                left: 12.5%;
                right: 12.5%;
                height: 2px;
                border-top: 2px dotted #0d9488;
                z-index: 1;
            }
            .st-roadmap-branch {
                display: flex;
                flex-direction: column;
                align-items: center;
                width: 23%;
                position: relative;
            }
            .st-roadmap-branch::before {
                content: '';
                position: absolute;
                top: -1.5rem;
                left: 50%;
                transform: translateX(-50%);
                width: 2px;
                height: 1.5rem;
                border-left: 2px dotted #0d9488;
                z-index: 1;
            }
            .st-partition-header {
                background-color: #fef08a;
                border: 2px solid #ca8a04;
                color: #854d0e;
                font-weight: 800;
                font-size: 0.8rem;
                text-transform: uppercase;
                padding: 0.5rem;
                border-radius: 8px;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.15);
                z-index: 5;
                width: 100%;
                min-height: 4.2rem;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                position: relative;
            }
            .st-partition-header::after {
                content: '';
                position: absolute;
                bottom: -1.5rem;
                left: 50%;
                transform: translateX(-50%);
                width: 2px;
                height: 1.5rem;
                border-left: 2px dotted #3b82f6;
                z-index: 1;
            }
            .st-partition-meta {
                font-size: 0.65rem;
                font-weight: 700;
                color: #b45309;
                margin-bottom: 0.15rem;
                display: block;
            }
            .st-partition-nodes {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 1rem;
                margin-top: 1.5rem;
                width: 100%;
                position: relative;
            }
            .st-partition-nodes::before {
                content: '';
                position: absolute;
                top: 0;
                bottom: 1rem;
                left: 50%;
                transform: translateX(-50%);
                width: 2px;
                border-left: 2px dotted #3b82f6;
                z-index: 1;
            }
            .st-roadmap-task {
                background-color: #fef08a;
                border: 2px solid #ca8a04;
                color: #854d0e;
                border-radius: 8px;
                padding: 0.4rem 0.6rem;
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 0.4rem;
                width: 95%;
                font-size: 0.75rem;
                font-weight: 700;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                z-index: 5;
                position: relative;
            }
            .st-roadmap-task::before {
                content: '';
                position: absolute;
                left: -0.2rem;
                top: 50%;
                transform: translateY(-50%);
                width: 0.2rem;
                border-top: 2px dotted #3b82f6;
                z-index: 1;
            }
            .st-task-badge {
                width: 1rem;
                height: 1rem;
                border-radius: 50%;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-size: 0.65rem;
                font-weight: bold;
                flex-shrink: 0;
            }
            .st-task-completed {
                background: #a855f7;
                color: white;
            }
            .st-task-todo {
                border: 1px solid #854d0e;
                background: rgba(0,0,0,0.05);
                color: transparent;
            }
            .st-task-title {
                flex: 1;
                text-align: left;
                line-height: 1.2;
            }
            @media (max-width: 991px) {
                .st-roadmap-branches-wrapper {
                    flex-direction: column;
                    gap: 1.8rem;
                    align-items: center;
                    padding-top: 0;
                }
                .st-roadmap-branches-wrapper::before {
                    display: none;
                }
                .st-roadmap-branch {
                    width: 80%;
                }
                .st-roadmap-branch::before {
                    display: none;
                }
            }
            </style>
            """
            st.markdown("\n".join(line.strip() for line in css_style.split("\n")), unsafe_allow_html=True)

            # Build the visual mindmap HTML
            map_html = f"""
            <div class="st-roadmap-mindmap">
                <div class="st-roadmap-root">Lộ trình: {selected_role}</div>
                <div class="st-roadmap-branches-wrapper">
            """

            # Group tasks by domain for cleaner dual-selectbox organization
            domains_list = []
            domain_tasks_map = {}  # display_phase -> list of task_titles
            task_lookup = {}       # (display_phase, task_title) -> (domain, task, domain_phase)

            for d_idx, domain in enumerate(roadmap):
                domain_phase = domain.get("phase", f"Vùng {d_idx + 1}")
                domain_title = domain.get("title", "Chuyên đề")
                tasks = domain.get("tasks", [])
                
                # Format clean domain name for the first dropdown (e.g. Vùng 1: Kiến thức Nền tảng)
                if ":" in domain_phase:
                    parts = domain_phase.split(":")
                    short_phase = parts[0].strip()
                    phase_desc = parts[1].strip()
                    if "(" in phase_desc:
                        phase_desc = phase_desc.split("(")[0].strip()
                    display_phase = f"{short_phase}: {phase_desc}"
                else:
                    display_phase = domain_phase
                
                domains_list.append(display_phase)
                domain_tasks_map[display_phase] = []
                
                map_html += f"""
                <div class="st-roadmap-branch">
                    <div class="st-partition-header">
                        <span class="st-partition-meta">{domain_phase}</span>
                        <div>{domain_title}</div>
                    </div>
                    <div class="st-partition-nodes">
                """
                
                for t_idx, task in enumerate(tasks):
                    task_title = task.get("task_title", "Nhiệm vụ")
                    sub_tasks = task.get("sub_tasks", [])
                    
                    # Consistent tick key format using original domain_phase and task_title
                    completed = True
                    if sub_tasks:
                        for s_idx in range(len(sub_tasks)):
                            tick_key = f"{selected_role}_{domain_phase}_{task_title}_{s_idx}"
                            if tick_key not in st.session_state.roadmap_ticks:
                                st.session_state.roadmap_ticks[tick_key] = is_skill_completed(task_title, sub_tasks)
                            if not st.session_state.roadmap_ticks[tick_key]:
                                completed = False
                    else:
                        completed = is_skill_completed(task_title, [])
                        
                    badge_class = "st-task-completed" if completed else "st-task-todo"
                    badge_icon = "✓" if completed else ""
                    
                    map_html += f"""
                        <div class="st-roadmap-task">
                            <span class="st-task-title">{task_title}</span>
                            <span class="st-task-badge {badge_class}">{badge_icon}</span>
                        </div>
                    """
                    
                    domain_tasks_map[display_phase].append(task_title)
                    task_lookup[(display_phase, task_title)] = (domain, task, domain_phase)
                    
                map_html += "</div></div>"
                
            map_html += "</div></div>"
            st.markdown("\n".join(line.strip() for line in map_html.split("\n")), unsafe_allow_html=True)
            
            # Grouped Sub-task checklist selectors
            st.write("")
            st.markdown("##### 🔍 Chọn chủ đề để xem nhiệm vụ chi tiết:")
            
            col1, col2 = st.columns(2)
            with col1:
                selected_domain = st.selectbox(
                    "Chọn Phân vùng Kiến thức:",
                    options=domains_list,
                    key="sb_selected_domain"
                )
            
            with col2:
                available_tasks = domain_tasks_map.get(selected_domain, [])
                selected_task_title = st.selectbox(
                    "Chọn chủ đề cần học:",
                    options=available_tasks,
                    key="sb_selected_task"
                )
            
            if selected_domain and selected_task_title:
                domain_item, task_item, domain_phase_key = task_lookup[(selected_domain, selected_task_title)]
                task_title = task_item.get("task_title", "Nhiệm vụ")
                sub_tasks = task_item.get("sub_tasks", [])
                
                st.info(f"**📌 {task_title}**\n\n*{domain_item.get('description', '')}*")
                
                st.markdown("##### 📝 Nhiệm vụ cần làm:")
                for s_idx, sub_task in enumerate(sub_tasks):
                    tick_key = f"{selected_role}_{domain_phase_key}_{task_title}_{s_idx}"
                    if tick_key not in st.session_state.roadmap_ticks:
                        st.session_state.roadmap_ticks[tick_key] = is_skill_completed(task_title, sub_tasks)
                    
                    widget_key = f"w_{tick_key}"
                    checked = st.checkbox(
                        sub_task,
                        value=st.session_state.roadmap_ticks[tick_key],
                        key=widget_key
                    )
                    st.session_state.roadmap_ticks[tick_key] = checked
                st.write("")
        
        st.divider()
        if missing_skills:
            st.markdown("### 📚 Tài liệu Học tập cho Kỹ năng Còn thiếu")
            learning_resources(missing_skills)
        else:
            st.success("Bạn đã được trang bị đầy đủ kỹ năng cho vai trò này! 💼")

# Footer
footer.render_footer("📚 Cầu nối Kỹ năng")