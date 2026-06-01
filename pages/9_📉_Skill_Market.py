import streamlit as st # type: ignore
import pandas as pd
import altair as alt
import json
import re
import ui.render_header as header
import ui.render_footer as footer

st.set_page_config(page_title="Bản đồ Kỹ năng Thị trường", page_icon="📉", layout="wide", initial_sidebar_state="collapsed")
st.logo("ui/assets/header.png", size="large", icon_image="ui/assets/logo.png")

# Header
header.render_header()

st.sidebar.title("📉 Bản đồ Kỹ năng")
st.sidebar.markdown("Khám phá nhu cầu kỹ năng hiện tại trên thị trường lao động toàn cầu và Việt Nam.")

st.title("📉 Bản đồ Kỹ năng Thị trường (Skill Market Heatmap)")
st.caption("Trực quan hóa dữ liệu từ hàng ngàn tin tuyển dụng để xem kỹ năng nào đang được săn đón nhất.")
st.divider()

# Hàm tính toán chính được cache để tối ưu tốc độ tải trang
@st.cache_data
def get_processed_data(location_filter):
    # Load data
    df = pd.read_csv("data/dataset/JobsFE.csv")
    with open("data/dataset/skills.json", "r", encoding="utf-8") as f:
        skills = json.load(f)
        
    # Lọc dữ liệu theo thị trường
    if location_filter == "Việt Nam":
        filtered_df = df[df['workplace'].str.contains('vietnam|hanoi|ho chi minh|da nang', case=False, na=False)]
        if filtered_df.empty:
            is_fallback = True
            filtered_df = df
        else:
            is_fallback = False
    else:
        filtered_df = df
        is_fallback = False
        
    # Lấy top 10 vai trò công việc phổ biến nhất
    top_positions = filtered_df['position'].value_counts().head(10).index.tolist()
    
    # Hợp nhất toàn bộ mô tả kỹ năng thành một chuỗi văn bản lớn (chuyển sang chữ thường)
    text_data = " ".join(filtered_df['requisite_skill'].astype(str).str.lower().tolist())
    
    # Hàm xây dựng regex thông minh cho các từ/ký tự đặc biệt
    def make_regex(syn):
        escaped = re.escape(syn)
        start = r'\b' if re.match(r'^\w', syn) else ''
        end = r'\b' if re.match(r'.*\w$', syn) else r'(?!\w)'
        return f"{start}{escaped}{end}"
        
    compiled_regexes = {}
    skill_counts = {}
    
    # Đếm số lần xuất hiện của các kỹ năng
    for cat, syns in skills.items():
        # Lọc nhanh bằng 'in' trước khi chạy Regex (tăng tốc độ chạy)
        if not any(syn.lower() in text_data for syn in syns):
            continue
        pat_str = '|'.join(make_regex(syn.lower()) for syn in syns)
        pat = re.compile(pat_str, re.IGNORECASE)
        cnt = len(pat.findall(text_data))
        if cnt > 0:
            skill_counts[cat] = cnt
            compiled_regexes[cat] = pat
            
    # Lấy top 15 kỹ năng được yêu cầu nhiều nhất
    top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:15]
    top_skills_names = [s[0] for s in top_skills]
    
    # Xây dựng ma trận Heatmap: Position vs Skill
    heatmap_data = []
    for pos in top_positions:
        pos_df = filtered_df[filtered_df['position'] == pos]
        pos_text = " ".join(pos_df['requisite_skill'].astype(str).str.lower().tolist())
        for skill in top_skills_names:
            pat = compiled_regexes.get(skill)
            if pat:
                count = len(pat.findall(pos_text))
            else:
                count = 0
            heatmap_data.append({
                "Position": pos.title(),
                "Skill": skill,
                "Count": count
            })
            
    heatmap_df = pd.DataFrame(heatmap_data)
    top_skills_df = pd.DataFrame(top_skills, columns=["Skill", "Count"])
    
    return top_skills_df, heatmap_df, len(filtered_df), is_fallback, top_skills_names

# Giao diện chính
st.write("### 🔍 Bộ lọc Dữ liệu")
location_filter = st.radio("Chọn phạm vi thị trường:", ["Toàn cầu (Global)", "Việt Nam"], horizontal=True)

with st.spinner("Đang xử lý dữ liệu và vẽ biểu đồ..."):
    top_skills_df, heatmap_df, total_jobs, is_fallback, top_skills_names = get_processed_data(location_filter)

if is_fallback:
    st.warning("⚠️ Dữ liệu tuyển dụng tại Việt Nam hiện tại rất hạn chế. Hệ thống đang tự động hiển thị dữ liệu Toàn cầu thay thế.")
elif location_filter == "Việt Nam":
    st.success(f"✅ Đang hiển thị dữ liệu lọc riêng cho thị trường Việt Nam (từ **{total_jobs}** tin tuyển dụng tại các thành phố lớn).")
else:
    st.info(f"📊 Đang phân tích tổng cộng **{total_jobs:,}** tin tuyển dụng trên toàn thế giới.")

st.divider()

# Layout 2 cột cho biểu đồ
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("🔥 Top 15 Kỹ năng Yêu cầu")
    st.caption("Những kỹ năng hoặc công nghệ được nhà tuyển dụng tìm kiếm nhiều nhất.")
    
    # Vẽ biểu đồ cột ngang
    bar_chart = alt.Chart(top_skills_df).mark_bar(
        cornerRadiusEnd=6, 
        color="#6366F1"  # Indigo hiện đại
    ).encode(
        x=alt.X('Count:Q', title='Số lượng Yêu cầu trong Tin tuyển dụng'),
        y=alt.Y('Skill:N', sort='-x', title='Kỹ năng/Công nghệ'),
        tooltip=[
            alt.Tooltip('Skill:N', title='Kỹ năng'),
            alt.Tooltip('Count:Q', title='Số lượng tin tuyển dụng', format=',')
        ]
    ).properties(height=450)
    
    st.altair_chart(bar_chart, use_container_width=True)

with col2:
    st.subheader("🌡️ Heatmap: Vai trò vs Kỹ năng")
    st.caption("Sự tương quan giữa vị trí công việc hàng đầu và các kỹ năng cần thiết.")
    
    # Vẽ biểu đồ Heatmap phẳng sạch sẽ
    heatmap = alt.Chart(heatmap_df).mark_rect().encode(
        x=alt.X('Skill:N', title='Kỹ năng', sort=top_skills_names, axis=alt.Axis(labelAngle=-45)),
        y=alt.Y('Position:N', title='Vai trò Công việc (Job Roles)'),
        color=alt.Color('Count:Q', scale=alt.Scale(scheme='purples'), title='Số lượng tin'),
        tooltip=[
            alt.Tooltip('Position:N', title='Vai trò'),
            alt.Tooltip('Skill:N', title='Kỹ năng'),
            alt.Tooltip('Count:Q', title='Số lượng yêu cầu', format=',')
        ]
    ).properties(height=450)
    
    st.altair_chart(heatmap, use_container_width=True)

st.divider()
st.info("💡 **Gợi ý:** Di chuột vào các ô màu trên Heatmap để xem chính xác số lượng yêu cầu kỹ năng cụ thể cho từng vị trí công việc tương ứng.")

# Footer
footer.render_footer("📉 Bản đồ Kỹ năng Thị trường")
