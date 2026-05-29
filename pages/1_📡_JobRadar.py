import streamlit as st  # type: ignore
import ui.render_footer as footer
import ui.render_header as header
import urllib
import urllib.parse

#Page configuration
st.set_page_config(page_title="Dò Tìm Việc làm", page_icon="📡", layout="centered", initial_sidebar_state="collapsed")
st.logo("ui/assets/header.png", size = "large", icon_image= "ui/assets/logo.png")

# Header
header.render_header()

# Sidebar configuration
st.sidebar.title("📡 Dò Tìm Việc làm")
st.sidebar.markdown("Trợ lý tìm kiếm việc làm toàn diện của bạn. Nhập thông tin chi tiết và khám phá danh sách công việc được tuyển chọn từ các nền tảng hàng đầu.")

# Main content
st.title("📡 Dò Tìm Việc làm")
st.caption("Khám phá các cơ hội việc làm phù hợp với vai trò, địa điểm và kinh nghiệm của bạn — tất cả từ một bảng điều khiển duy nhất.")
st.divider()

cols = st.columns([1, 1], vertical_alignment='center', gap='small')
with cols[0]:
    job = st.text_input("Vị trí / Vai trò", placeholder="ví dụ: Software Engineer")
    location = st.text_input("Địa điểm mong muốn", value="Vietnam", placeholder="ví dụ: Hà Nội")
with cols[1]:
    experience = st.selectbox("Số năm kinh nghiệm", ["Mới tốt nghiệp", "0-1", "1-3", "3-5", "5+"])
    job_type = st.selectbox("Loại công việc", ["Tất cả", "Toàn thời gian", "Bán thời gian", "Làm việc từ xa", "Làm việc linh hoạt (Hybrid)"])
st.write("")

if st.button("🔍 Tìm kiếm Việc làm", use_container_width=True):
    st.divider()
    job_enc = urllib.parse.quote_plus(job)              # URL-safe job role
    loc_enc = urllib.parse.quote_plus(location)         # URL-safe location
    job_dash = job.lower().replace(" ", "-")            # For slug-based URLs
    loc_dash = location.lower().replace(" ", "-")       # For slug-based URLs

    st.success("Khám phá cơ hội việc làm từ các nền tảng dưới đây:")

    col1, col2 = st.columns(2, gap='small')

    with col1:
        st.image("ui/assets/LinkedIn.png", use_container_width=True)
        st.link_button("🧑‍💼 LinkedIn", f"https://www.linkedin.com/jobs/search/?keywords={job_enc}&location={loc_enc}", use_container_width=True)
        st.write("")

        st.image("ui/assets/Foundit.png", use_container_width=True)
        st.link_button("🧭 Foundit", f"https://www.foundit.in/srp/results?query={job_enc}&location={loc_enc}", use_container_width=True)
        st.write("")

        st.image("ui/assets/TimesJobs.png", use_container_width=True)
        st.link_button("🕒 TimesJobs", f"https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords={job_enc}&txtLocation={loc_enc}", use_container_width=True)
        st.write("")

        st.image("ui/assets/Indeed.png", use_container_width=True)
        st.link_button("🌎 Indeed", f"https://www.indeed.com/jobs?q={job_enc}&l={loc_enc}", use_container_width=True)

    with col2:
        st.image("ui/assets/Naukri.png", use_container_width=True)
        st.link_button("📘 Naukri", f"https://www.naukri.com/{job_dash}-jobs-in-{loc_dash}", use_container_width=True)
        st.write("")

        st.image("ui/assets/FreshersWorld.png", use_container_width=True)
        st.link_button("🎓 FreshersWorld", f"https://www.freshersworld.com/jobs/jobsearch/{job_dash}-jobs-in-{loc_dash}", use_container_width=True)
        st.write("")

        st.image("ui/assets/Instahyre.png", use_container_width=True)
        st.link_button("⚡ Instahyre", f"https://www.instahyre.com/jobs/?q={job_enc}&l={loc_enc}", use_container_width=True)
        st.write("")

        st.image("ui/assets/Shine.png", use_container_width=True)
        st.link_button("🌟 Shine", f"https://www.shine.com/job-search/{job_dash}-jobs-in-{loc_dash}", use_container_width=True)

# Footer
footer.render_footer("📡 Dò Tìm Việc làm")