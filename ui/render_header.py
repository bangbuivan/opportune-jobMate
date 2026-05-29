import streamlit as st

def render_header():
    st.image("ui/assets/header.png", use_container_width=True)
    st.write("")
    st.caption("<p style='text-align: center;'>Công cụ thông minh giúp phân tích CV, gợi ý vị trí tuyển dụng và đánh giá mức độ tương thích công việc — tất cả trong một nơi</p>", unsafe_allow_html=True)
    st.divider()