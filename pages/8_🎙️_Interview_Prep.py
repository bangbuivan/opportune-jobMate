import streamlit as st
import json
import ui.render_footer as footer
import ui.render_header as header
from analyzer.analysis_enhancer import get_gemini_api_key
from preprocessor.parser import extract_text_from_uploaded_file
from builder.ai_features import (
    generate_interview_questions_with_gemini,
    evaluate_interview_answers_with_gemini
)

# Page configuration
st.set_page_config(page_title="Luyện phỏng vấn", page_icon="🎙️", layout="centered", initial_sidebar_state="collapsed")
st.logo("ui/assets/header.png", size="large", icon_image="ui/assets/logo.png")

# Header
header.render_header()

# Sidebar
st.sidebar.title("Luyện phỏng vấn")
st.sidebar.markdown("Tạo các câu hỏi phỏng vấn thử được thiết kế riêng và nhận báo cáo đánh giá chi tiết về phần thể hiện của bạn.")

st.title("🎙️ Luyện phỏng vấn AI")
st.caption("Chuẩn bị cho công việc mơ ước của bạn với các buổi phỏng vấn thử chuyên môn và hành vi được cá nhân hóa.")
st.divider()

# Initialize session state variables
if "ip_step" not in st.session_state:
    st.session_state.ip_step = "setup"
if "ip_questions" not in st.session_state:
    st.session_state.ip_questions = []
if "ip_answers" not in st.session_state:
    st.session_state.ip_answers = []
if "ip_resume_text" not in st.session_state:
    st.session_state.ip_resume_text = ""
if "ip_jd_text" not in st.session_state:
    st.session_state.ip_jd_text = ""
if "ip_evaluation" not in st.session_state:
    st.session_state.ip_evaluation = None

def reset_interview():
    st.session_state.ip_step = "setup"
    st.session_state.ip_questions = []
    st.session_state.ip_answers = []
    st.session_state.ip_resume_text = ""
    st.session_state.ip_jd_text = ""
    st.session_state.ip_evaluation = None

api_key = get_gemini_api_key()

# STEP 1: Setup Mock Interview
if st.session_state.ip_step == "setup":
    st.subheader("🛠️ Thiết lập Buổi Phỏng vấn Thử")
    st.write("Tải lên CV và dán mô tả công việc mục tiêu để tạo ra các câu hỏi cá nhân hóa.")
    
    uploaded_resume = st.file_uploader("📄 Tải lên CV của bạn (PDF hoặc DOCX)", type=["pdf", "docx"], key="ip_setup_resume")
    uploaded_jd = st.file_uploader("💼 Tải lên Mô tả Công việc (Tùy chọn PDF hoặc DOCX)", type=["pdf", "docx"], key="ip_setup_jd")
    jd_text = st.text_area("✍️ Hoặc dán văn bản Mô tả Công việc", height=200, placeholder="Dán mô tả công việc tại đây...")
    
    start_btn = st.button("🚀 Bắt đầu Phỏng vấn Thử", use_container_width=True)
    
    if start_btn:
        if not uploaded_resume:
            st.error("Vui lòng tải lên CV của bạn trước.")
        elif not jd_text.strip() and not uploaded_jd:
            st.error("Vui lòng cung cấp mô tả công việc (tải lên tệp hoặc dán văn bản).")
        else:
            if not api_key:
                st.info("⚠️ Đang chạy ở Chế độ Bản mẫu Ngoại tuyến (Không cung cấp API key)")
            with st.spinner("Đang tạo câu hỏi phỏng vấn riêng..."):
                try:
                    resume_text = extract_text_from_uploaded_file(uploaded_resume)
                    final_jd = extract_text_from_uploaded_file(uploaded_jd) if uploaded_jd else jd_text
                    
                    st.session_state.ip_resume_text = resume_text
                    st.session_state.ip_jd_text = final_jd
                    
                    questions_raw = generate_interview_questions_with_gemini(resume_text, final_jd, api_key)
                    questions = json.loads(questions_raw)
                    
                    if isinstance(questions, list) and len(questions) > 0:
                        st.session_state.ip_questions = questions
                        st.session_state.ip_answers = [""] * len(questions)
                        st.session_state.ip_step = 0
                        st.rerun()
                    else:
                        st.error("Không thể tạo câu hỏi hợp lệ. Vui lòng kiểm tra lại thông tin đã nhập.")
                except Exception as e:
                    st.error(f"Đã xảy ra lỗi khi bắt đầu phỏng vấn: {e}")

# STEP 2: Questionnaire Wizard
elif isinstance(st.session_state.ip_step, int):
    step = st.session_state.ip_step
    questions = st.session_state.ip_questions
    
    st.subheader(f"🎙️ Phỏng vấn Thử - Câu hỏi {step + 1}/{len(questions)}")
    st.progress((step) / len(questions), text=f"Tiến độ: Đã trả lời {step}/{len(questions)} câu hỏi")
    
    # Display Question card
    st.info(f"**Câu hỏi:**\n{questions[step]}")
    
    # Input response
    user_resp = st.text_area("Câu trả lời của bạn", value=st.session_state.ip_answers[step], key=f"ip_ans_{step}", height=150, placeholder="Nhập câu trả lời của bạn tại đây... (Nên tập trung vào các thành tựu cụ thể, sử dụng phương pháp STAR: Situation, Task, Action, Result)")
    
    # Navigation buttons
    col1, col2 = st.columns([1, 1])
    
    with col1:
        prev_btn = st.button("⬅️ Câu hỏi trước", disabled=(step == 0), use_container_width=True)
    with col2:
        is_last = (step == len(questions) - 1)
        next_btn_label = "🏁 Nộp bài phỏng vấn" if is_last else "➡️ Câu hỏi tiếp theo"
        next_btn = st.button(next_btn_label, use_container_width=True)
        
    if prev_btn:
        st.session_state.ip_answers[step] = user_resp
        st.session_state.ip_step -= 1
        st.rerun()
        
    if next_btn:
        st.session_state.ip_answers[step] = user_resp
        if is_last:
            st.session_state.ip_step = "evaluating"
        else:
            st.session_state.ip_step += 1
        st.rerun()
 
# STEP 3: Evaluation Phase
elif st.session_state.ip_step == "evaluating":
    st.subheader("🏁 Hoàn thành Phỏng vấn Thử")
    if not api_key:
        st.info("⚠️ Đang đánh giá ở Chế độ Bản mẫu Ngoại tuyến (Không cung cấp API key)")
    else:
        st.info("Câu trả lời của bạn đã được nộp! AI đang phân tích phần thể hiện của bạn và tạo các đề xuất cải thiện...")
    
    with st.spinner("Đang phân tích câu trả lời..."):
        try:
            eval_raw = evaluate_interview_answers_with_gemini(
                st.session_state.ip_resume_text,
                st.session_state.ip_jd_text,
                st.session_state.ip_questions,
                st.session_state.ip_answers,
                api_key
            )
            eval_data = json.loads(eval_raw)
            
            st.session_state.ip_evaluation = eval_data
            st.session_state.ip_step = "results"
            st.rerun()
        except Exception as e:
            st.error(f"Đã xảy ra lỗi khi đánh giá câu trả lời: {e}")
            if st.button("🔄 Thử đánh giá lại", use_container_width=True):
                st.rerun()
            if st.button("⬅️ Quay lại câu hỏi trước", use_container_width=True):
                st.session_state.ip_step = len(st.session_state.ip_questions) - 1
                st.rerun()

# STEP 4: Results Dashboard
elif st.session_state.ip_step == "results":
    eval_data = st.session_state.ip_evaluation
    
    if eval_data:
        score = eval_data.get("OverallScore", 0)
        
        st.subheader("📊 Báo cáo Kết quả Phỏng vấn")
        st.write("")
        
        # Display Score Card
        st.markdown(f"### 🎯 Điểm số Tổng quan: **{score}/100**")
        st.progress(min(int(score), 100), text="Điểm phỏng vấn")
        
        if score >= 80:
            st.success("Thành tích xuất sắc! Bạn đã trả lời rõ ràng, áp dụng tốt phương pháp STAR và chứng minh được năng lực vững vàng.")
        elif score >= 60:
            st.info("Làm tốt lắm! Bạn đã trả lời tốt, nhưng việc bổ sung thêm các thành tựu định lượng hoặc làm rõ hơn hành động cụ thể của bạn sẽ giúp câu trả lời xuất sắc hơn.")
        else:
            st.warning("Hãy tiếp tục luyện tập. Câu trả lời của bạn vẫn thiếu một số chi tiết quan trọng được chỉ ra trong phần nhận xét. Hãy tham khảo gợi ý bên dưới.")
            
        st.divider()
        st.markdown("### 📝 Chi tiết từng câu hỏi")
        st.write("")
        
        # Display individual evaluations
        evaluations = eval_data.get("Evaluation", [])
        for i, item in enumerate(evaluations):
            st.markdown(f"#### ❓ Câu hỏi {i + 1}: {item.get('Question')}")
            
            ans = item.get("Answer", "").strip()
            st.markdown(f"**Câu trả lời của bạn:** {ans if ans else '*[Không cung cấp câu trả lời]*'}")
            
            score_q = item.get("Score", 0)
            st.markdown(f"**Điểm:** `{score_q}/10`")
            
            # Feedback
            st.info(f"**Nhận xét:**\n{item.get('Feedback')}")
            
            # Sample Response
            with st.expander(f"✨ Xem câu trả lời gợi ý"):
                st.markdown(item.get("ExcellentResponse"))
            st.divider()
            
        # Reset Button
        st.button("🔄 Bắt đầu phỏng vấn mới", on_click=reset_interview, use_container_width=True)
    else:
        st.error("Không tìm thấy dữ liệu đánh giá.")
        st.button("🔄 Thiết lập lại từ đầu", on_click=reset_interview, use_container_width=True)

st.divider()
# Footer
footer.render_footer("🎙️ Luyện phỏng vấn")
