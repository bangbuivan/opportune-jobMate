from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

# Ensure the root directory is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import preprocessor.parser as parser
from preprocessor.skills import extract_skills_fuzzy
import preprocessor.personal_info as pf
import recommender.top_n_jobs as jobRec
from preprocessor.spacy_nlp import load_spacy_nlp_model
from recommender.ai_model import JobRecommendationSystem
from preprocessor.skills import extract_soft_skills_fuzzy, weighted_skill_analysis
import json
from analyzer.resume_analysis import run_local_ats_analysis
from analyzer.analysis_enhancer import perform_ai_ats_analysis
from fastapi import Request
from fastapi.responses import StreamingResponse
from builder import generator_standard, resume_enhancer
from builder.ai_features import (
    generate_cover_letter_with_gemini,
    generate_interview_questions_with_gemini,
    evaluate_interview_answers_with_gemini
)
import time

class MockUploadedFile:
    def __init__(self, name, size):
        self.name = name
        self.size = size

app = FastAPI(title="CareerForge API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Models
nlp = load_spacy_nlp_model()
ai_recommender = JobRecommendationSystem("data/dataset/JobsFE.csv")

@app.post("/api/recommend-jobs")
async def recommend_jobs(
    file: UploadFile = File(...),
    search_method: str = Form("AI Semantic Search"),
    top_n: int = Form(5)
):
    try:
        content = await file.read()
        file_type = file.content_type or ""
        
        if "pdf" in file_type or file.filename.endswith(".pdf"):
            extracted_text = parser.extract_text_from_pdf(content)
        elif "wordprocessingml.document" in file_type or file.filename.endswith(".docx"):
            extracted_text = parser.extract_text_from_docx(content)
        else:
            return {"error": "Định dạng tệp không được hỗ trợ. Vui lòng tải lên tệp PDF hoặc DOCX."}
            
        doc = nlp(extracted_text)
        
        name = pf.extract_name(doc, extracted_text)
        email = pf.extract_mail(extracted_text)
        phone = pf.extract_phone(extracted_text)
        result = pf.extract_education_details(extracted_text)
        degree = result.get("degree") if result else None
        
        skills = sorted(extract_skills_fuzzy(doc))
        
        jobs = []
        if "Basic" in search_method:
            recommended_jobs = jobRec.recommend_top_jobs(skills, top_n)
            if recommended_jobs:
                jobs = recommended_jobs
        elif "Transformer" in search_method or "Semantic" in search_method:
            recommendations = ai_recommender.recommend_jobs(extracted_text, top_n=top_n)
            jobs = recommendations.get("recommended_jobs", [])
        else:
            recommendations = ai_recommender.recommend_jobs_tfidf(extracted_text, top_n=top_n)
            jobs = recommendations.get("recommended_jobs", [])

        return {
            "success": True,
            "personal_info": {
                "name": name,
                "email": email,
                "phone": phone,
                "degree": degree,
                "skills": skills
            },
            "recommended_jobs": jobs,
            "search_method": search_method
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/skill-bridge/roles")
def get_roles():
    try:
        with open("data/dataset/job_to_skill.json", "r") as f:
            job_skills_map = json.load(f)
        return {"success": True, "roles": sorted(job_skills_map.keys())}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/skill-bridge/analyze")
async def analyze_skill_bridge(
    file: UploadFile = File(...), 
    role: str = Form(...),
    gemini_key: str = Form(None)
):
    try:
        content = await file.read()
        file_type = file.content_type or ""
        if "pdf" in file_type or file.filename.endswith(".pdf"):
            resume_text = parser.extract_text_from_pdf(content)
        elif "wordprocessingml.document" in file_type or file.filename.endswith(".docx"):
            resume_text = parser.extract_text_from_docx(content)
        else:
            return {"error": "Định dạng tệp không được hỗ trợ."}
            
        doc = nlp(resume_text)
        extracted_skills = set(extract_skills_fuzzy(doc))
        
        with open("data/dataset/job_to_skill.json", "r") as f:
            job_skills_map = json.load(f)
            
        if role not in job_skills_map:
            return {"success": False, "error": "Không tìm thấy vị trí công việc."}
            
        required_skills = set(job_skills_map[role])
        matched_skills = extracted_skills & required_skills
        missing_skills = required_skills - extracted_skills
        
        # Generate learning roadmap
        from builder.ai_features import generate_ai_roadmap
        roadmap = generate_ai_roadmap(role, missing_skills, gemini_key)
        
        return {
            "success": True,
            "matched_skills": sorted(list(matched_skills)),
            "missing_skills": sorted(list(missing_skills)),
            "roadmap": roadmap
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/ats-tuneup")
async def ats_tuneup(
    file: UploadFile = File(...), 
    gemini_key: str = Form(None),
    analysis_type: str = Form("local")
):
    try:
        content = await file.read()
        file_type = file.content_type or ""
        if "pdf" in file_type or file.filename.endswith(".pdf"):
            resume_text = parser.extract_text_from_pdf(content)
        elif "wordprocessingml.document" in file_type or file.filename.endswith(".docx"):
            resume_text = parser.extract_text_from_docx(content)
        else:
            return {"error": "Định dạng tệp không được hỗ trợ."}

        mock_file = MockUploadedFile(file.filename, len(content))
        
        if analysis_type == "ai":
            if not gemini_key:
                return {"success": False, "error": "Yêu cầu nhập Gemini API key để thực hiện phân tích bằng AI."}
            results = perform_ai_ats_analysis(resume_text, gemini_key)
            from analyzer.resume_analysis import calculate_ai_ats_category_scores
            scores = calculate_ai_ats_category_scores(results)
            return {"success": True, "type": "ai", "results": results, "scores": scores}
        else:
            results = run_local_ats_analysis(resume_text, mock_file)
            from analyzer.resume_analysis import calculate_ats_category_scores
            scores = calculate_ats_category_scores(results)
            return {"success": True, "type": "local", "results": results, "scores": scores}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/job-matcher")
async def job_matcher(
    resume: UploadFile = File(...),
    jd_text: str = Form(""),
    jd_file: UploadFile = File(None)
):
    try:
        content = await resume.read()
        if (resume.content_type and "pdf" in resume.content_type) or resume.filename.endswith(".pdf"):
            resume_txt = parser.extract_text_from_pdf(content)
        else:
            resume_txt = parser.extract_text_from_docx(content)
            
        final_jd_text = jd_text
        if jd_file and jd_file.filename:
            jd_content = await jd_file.read()
            if (jd_file.content_type and "pdf" in jd_file.content_type) or jd_file.filename.endswith(".pdf"):
                final_jd_text = parser.extract_text_from_pdf(jd_content)
            else:
                final_jd_text = parser.extract_text_from_docx(jd_content)
                
        if not final_jd_text:
            return {"success": False, "error": "Yêu cầu nhập văn bản mô tả công việc hoặc tải lên tệp JD."}

        resume_doc = nlp(resume_txt)
        resume_hard_skills = set(extract_skills_fuzzy(resume_doc))
        resume_soft_skills = set(extract_soft_skills_fuzzy(resume_doc))
        jd_hard_skills_weighted, jd_soft_skills = weighted_skill_analysis(final_jd_text, nlp)
        
        jd_hard_skills = set(jd_hard_skills_weighted.keys())
        matched_hard_skills = resume_hard_skills.intersection(jd_hard_skills)
        missing_hard_skills = jd_hard_skills.difference(resume_hard_skills)
        matched_soft_skills = resume_soft_skills.intersection(jd_soft_skills)
        missing_soft_skills = jd_soft_skills.difference(resume_soft_skills)

        total_jd_hard_weight = sum(jd_hard_skills_weighted.values())
        matched_hard_weight = sum(jd_hard_skills_weighted[s] for s in matched_hard_skills)

        hard_pct = (matched_hard_weight / total_jd_hard_weight) * 100 if total_jd_hard_weight else 0
        soft_pct = (len(matched_soft_skills) / len(jd_soft_skills)) * 100 if jd_soft_skills else 0

        hard_score_contribution = hard_pct * 0.9 
        soft_score_contribution = soft_pct * 0.1 
        final_score = round(hard_score_contribution + soft_score_contribution)
        
        return {
            "success": True,
            "score": final_score,
            "hard_pct": round(hard_pct),
            "soft_pct": round(soft_pct),
            "matched_hard": list(matched_hard_skills),
            "missing_hard": list(missing_hard_skills),
            "matched_soft": list(matched_soft_skills),
            "missing_soft": list(missing_soft_skills)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/resume-builder")
async def build_resume(request: Request):
    try:
        payload = await request.json()
        api_key = payload.get("gemini_key")
        tone = payload.get("tone", "Professional")
        data = payload.get("resume_data")
        
        if not data:
            return {"success": False, "error": "Không có dữ liệu CV nào được cung cấp."}
            
        if api_key:
            if data.get("summary"):
                data["summary"] = resume_enhancer.enhance_content_with_gemini(
                    "professional summary", data["summary"], tone, api_key
                )
                time.sleep(1)
                
            for exp in data.get("experience", []):
                resp_text = "\n".join(exp.get("responsibilities", []))
                if resp_text.strip():
                    enhanced = resume_enhancer.enhance_content_with_gemini(
                        "job responsibility", resp_text, tone, api_key
                    )
                    exp["responsibilities"] = [r.strip() for r in enhanced.split('\n') if r.strip()]
                    time.sleep(1)
                    
            for proj in data.get("projects", []):
                desc_text = "\n".join(proj.get("description", []))
                if desc_text.strip():
                    enhanced = resume_enhancer.enhance_content_with_gemini(
                        "project description", desc_text, tone, api_key
                    )
                    proj["description"] = [d.strip() for d in enhanced.split('\n') if d.strip()]
                    time.sleep(1)

        doc_io = generator_standard.generate_structured_resume(data, "data/template.docx")
        
        return StreamingResponse(
            doc_io, 
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=Resume.docx", "Access-Control-Expose-Headers": "Content-Disposition"}
        )
    except Exception as e:
        return {"success": False, "error": str(e)}

class InterviewEvaluateRequest(BaseModel):
    resume_text: str
    jd_text: str
    questions: list[str]
    answers: list[str]
    gemini_key: str = None

class CoverLetterDocxRequest(BaseModel):
    name: str
    email: str
    phone: str
    body_text: str

@app.post("/api/cover-letter")
async def cover_letter_endpoint(
    file: UploadFile = File(...),
    jd_text: str = Form(""),
    jd_file: UploadFile = File(None),
    tone: str = Form("Professional"),
    gemini_key: str = Form(None)
):
    try:
        content = await file.read()
        file_type = file.content_type or ""
        if "pdf" in file_type or file.filename.endswith(".pdf"):
            resume_text = parser.extract_text_from_pdf(content)
        else:
            resume_text = parser.extract_text_from_docx(content)
        
        final_jd = jd_text
        if jd_file and jd_file.filename:
            jd_content = await jd_file.read()
            if (jd_file.content_type and "pdf" in jd_file.content_type) or jd_file.filename.endswith(".pdf"):
                final_jd = parser.extract_text_from_pdf(jd_content)
            else:
                final_jd = parser.extract_text_from_docx(jd_content)
        
        if not final_jd:
            return {"success": False, "error": "Yêu cầu nhập văn bản mô tả công việc hoặc tải lên tệp JD."}
            
        cl_text = generate_cover_letter_with_gemini(resume_text, final_jd, tone, gemini_key)
        
        # Extract candidate details for DOCX letterhead
        doc = nlp(resume_text)
        name = pf.extract_name(doc, resume_text) or "Tên ứng viên"
        email = pf.extract_mail(resume_text) or "ungvien@example.com"
        phone = pf.extract_phone(resume_text) or "090-000-0000"
        
        return {
            "success": True, 
            "cover_letter": cl_text,
            "personal_info": {
                "name": name,
                "email": email,
                "phone": phone
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/cover-letter/download-docx")
def download_cover_letter_docx(payload: CoverLetterDocxRequest):
    try:
        from builder.ai_features import generate_cover_letter_docx
        file_io = generate_cover_letter_docx(
            payload.name,
            payload.email,
            payload.phone,
            payload.body_text
        )
        return StreamingResponse(
            file_io,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=Cover_Letter.docx", "Access-Control-Expose-Headers": "Content-Disposition"}
        )
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/interview/questions")
async def interview_questions_endpoint(
    file: UploadFile = File(...),
    jd_text: str = Form(""),
    jd_file: UploadFile = File(None),
    gemini_key: str = Form(None)
):
    try:
        content = await file.read()
        file_type = file.content_type or ""
        if "pdf" in file_type or file.filename.endswith(".pdf"):
            resume_text = parser.extract_text_from_pdf(content)
        else:
            resume_text = parser.extract_text_from_docx(content)
        
        final_jd = jd_text
        if jd_file and jd_file.filename:
            jd_content = await jd_file.read()
            if (jd_file.content_type and "pdf" in jd_file.content_type) or jd_file.filename.endswith(".pdf"):
                final_jd = parser.extract_text_from_pdf(jd_content)
            else:
                final_jd = parser.extract_text_from_docx(jd_content)
                
        if not final_jd:
            return {"success": False, "error": "Yêu cầu nhập văn bản mô tả công việc hoặc tải lên tệp JD."}
            
        questions_raw = generate_interview_questions_with_gemini(resume_text, final_jd, gemini_key)
        questions = json.loads(questions_raw)
        return {
            "success": True, 
            "questions": questions,
            "resume_text": resume_text,
            "jd_text": final_jd
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/interview/evaluate")
async def interview_evaluate_endpoint(payload: InterviewEvaluateRequest):
    try:
        eval_raw = evaluate_interview_answers_with_gemini(
            payload.resume_text,
            payload.jd_text,
            payload.questions,
            payload.answers,
            payload.gemini_key
        )
        eval_data = json.loads(eval_raw)
        return {"success": True, "evaluation": eval_data}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
