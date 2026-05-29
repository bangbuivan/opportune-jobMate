import re
from preprocessor.skills import extract_skills_fuzzy, extract_soft_skills_fuzzy
from preprocessor.spacy_nlp import load_spacy_nlp_model
from collections import Counter

nlp = load_spacy_nlp_model("en_core_web_sm")

def run_local_ats_analysis(text, uploaded_file):
    doc = nlp(text)
    sections = []

    # Step 1: Contact Information
    email = re.search(r"[\w\.-]+@[\w\.-]+", text)
    phone = re.search(r"\+?\d[\d\s\-]{7,15}", text)
    linkedin = re.search(r"linkedin\.com/in/\S+", text)
    section_1 = {
        "step": 1,
        "title": "Kiểm tra Thông tin Liên hệ",
        "findings": [],
    }
    section_1["findings"].append(("success", "Đã phát hiện Email") if email else ("warning", "Không tìm thấy Email"))
    section_1["findings"].append(("success", "Đã phát hiện số điện thoại") if phone else ("warning", "Không tìm thấy số điện thoại"))
    section_1["findings"].append(("success", "Tìm thấy hồ sơ LinkedIn") if linkedin else ("warning", "Thiếu hồ sơ LinkedIn"))
    sections.append(section_1)

    # Step 2: Grammar (basic)
    grammar_errors = re.findall(r"\b[A-Z][a-z]+ [a-z]+ [A-Z][a-z]+\b", text)
    sections.append({
        "step": 2,
        "title": "Kiểm tra Chính tả & Ngữ pháp",
        "findings": [("success", "Không phát hiện lỗi chính tả/ngữ pháp rõ ràng")] if len(grammar_errors) < 2 else [("warning", "Phát hiện có thể có lỗi ngữ pháp hoặc lỗi viết hoa")]
    })

    # Step 3: Personal Pronouns
    personal_pronouns = re.findall(r"\b(I|me|my|mine|we|our)\b", text, re.IGNORECASE)
    sections.append({
        "step": 3,
        "title": "Kiểm tra Đại từ Nhân xưng",
        "findings": [("success", "Không sử dụng đại từ nhân xưng")] if not personal_pronouns else [("warning", f"Tìm thấy {len(personal_pronouns)} đại từ nhân xưng. Hãy tránh sử dụng chúng.")]
    })

    # Step 4: Skills & Keywords
    tech_skills = extract_skills_fuzzy(doc)
    soft_skills = extract_soft_skills_fuzzy(doc)
    findings = []
    if tech_skills:
        findings.append(("success", f"Đã phát hiện Kỹ năng Chuyên môn: {', '.join(tech_skills)}"))
    else:
        findings.append(("warning", f"Không phát hiện Kỹ năng Chuyên môn"))
    if soft_skills:
        findings.append(("success", f"Đã phát hiện Kỹ năng Mềm: {', '.join(soft_skills)}"))
    else:
        findings.append(("warning", f"Không phát hiện Kỹ năng Mềm"))
    sections.append({
        "step": 4,
        "title": "Nhắm mục tiêu Kỹ năng & Từ khóa",
        "findings": findings
    })

    # Step 5: Complex Sentences
    long_sents = [sent.text for sent in doc.sents if len(sent.text.split()) > 40]
    sections.append({
        "step": 5,
        "title": "Câu quá dài",
        "findings": [("warning", f"Câu dài: {s[:80]}...") for s in long_sents] if long_sents else [("success", "Không tìm thấy câu nào quá dài")]
    })

    # Step 6: Generic Sentences
    generic_phrases = [
        "responsible for", "worked on", "helped", "tasked with", "participated in", "assisted with", "handled",
        "involved in", "part of", "supported", "duties included", "played a role in", "knowledge of", "familiar with",
        "exposure to", "experience in", "performed", "used to", "took part in", "made", "did", "contributed to", "led",
        "managed", "oversaw", "ran", "coordinated", "scheduled", "organized", "arranged", "created", "built", "developed",
        "designed", "engineered", "deployed", "launched", "implemented", "executed", "collaborated with", "worked closely with",
        "worked as", "worked under", "followed up on", "took responsibility for", "supervised", "trained", "mentored",
        "assumed responsibility for", "provided support", "provided assistance", "gave input on", "attended", "joined",
        "contributed", "assumed the role of", "followed", "performed duties", "assigned to", "utilized", "used",
        "applied knowledge of", "leveraged", "made sure", "ensured", "ensured compliance", "validated", "checked",
        "verified", "responded to", "answered", "dealt with", "addressed", "resolved", "fixed", "improved", "streamlined",
        "upgraded", "enhanced", "maintained", "supported users", "gave feedback", "filled in", "acted as", "liaised with",
        "followed procedures", "enforced policies", "interfaced with", "contributed ideas", "wrote", "edited", "documented",
        "reported on", "compiled", "tracked", "monitored", "recorded", "calculated", "evaluated", "tested", "analyzed data",
        "reviewed", "produced", "submitted"
    ]

    text_lower = text.lower()
    phrase_counter = Counter()

    for phrase in generic_phrases:
        count = text_lower.count(phrase)
        if count > 2:
            phrase_counter[phrase] = count

    if phrase_counter:
        findings = [
            ("warning", f"Cụm từ chung chung được dùng: '{phrase}' — {count} lần")
            for phrase, count in phrase_counter.items()
        ]
    else:
        findings = [("success", "Không phát hiện cụm từ chung chung bị lạm dụng")]

    sections.append({
        "step": 6,
        "title": "Câu thông dụng/chung chung",
        "findings": findings
    })

    # Step 7: Passive Voice
    passive_indicators = [
        "was", "were", "is", "are", "been", "being", "be",
        "has been", "have been", "had been",
        "will be", "would be", "shall be", "should be", "can be", "could be", "may be", "might be", "must be"
    ]
    passive_patterns = [
    re.compile(rf"\b{aux}\b\s+\b\w+(ed|en)\b", re.IGNORECASE) for aux in passive_indicators
    ]

    passive_sentences = []
    for sent in doc.sents:
        for pattern in passive_patterns:
            if pattern.search(sent.text):
                passive_sentences.append(sent.text.strip())
                break

    sections.append({
        "step": 7,
        "title": "Câu bị động",
        "findings": [("warning", f"Bị động: {p[:80]}...") for p in passive_sentences] if passive_sentences else [("success", "Không phát hiện câu bị động")]
    })

    # Step 8: Quantified Achievements
    metrics = re.findall(r"\d+%|\d{2,}", text)
    sections.append({
        "step": 8,
        "title": "Điểm số định lượng",
        "findings": [("success", f"Tìm thấy {len(metrics)} kết quả định lượng")] if metrics else [("warning", "Không tìm thấy thành tựu định lượng (%, con số)")]
    })

    # Step 9: Essential Resume Sections
    required_sections = ["summary", "education", "experience", "skills"]
    missing_sections = [s for s in required_sections if s not in text.lower()]
    sections.append({
        "step": 9,
        "title": "Các phần thiết yếu của CV",
        "findings": [("warning", f"Thiếu phần: {', '.join(missing_sections)}")] if missing_sections else [("success", "Tìm thấy đầy đủ các phần thiết yếu")]
    })

    # Step 10: Repeated Action Verbs
    action_verb_list = [
        "achieved", "administered", "analyzed", "arranged", "built", "calculated", "collaborated", "communicated",
        "completed", "conducted", "created", "debugged", "designed", "developed", "directed", "documented", "enhanced",
        "engineered", "executed", "facilitated", "formulated", "generated", "handled", "implemented", "improved",
        "initiated", "inspired", "integrated", "led", "managed", "monitored", "negotiated", "organized", "oversaw",
        "performed", "planned", "presented", "programmed", "provided", "redesigned", "researched", "resolved", "reviewed",
        "scheduled", "solved", "streamlined", "supervised", "supported", "tested", "trained", "translated", "upgraded",
        "utilized", "validated", "wrote"
    ]

    action_verb_counter = Counter()
    text_tokens = re.findall(r"\b\w+\b", text.lower())

    for token in text_tokens:
        if token in action_verb_list:
            action_verb_counter[token] += 1

    overused_verbs = {verb: count for verb, count in action_verb_counter.items() if count > 2}

    if overused_verbs:
        findings = [
            ("warning", f"Động từ hành động bị lặp lại: '{verb}' được sử dụng {count} lần")
            for verb, count in overused_verbs.items()
        ]
    else:
        findings = [("success", "Không lặp lại động từ hành động")]

    sections.append({
        "step": 10,
        "title": "Động từ hành động lặp lại",
        "findings": findings
    })

    # Step 11: Document Properties
    findings = []

    # Word Count Check
    word_count = len(text.split())
    if word_count <= 350:
        findings.append(("warning", f"CV quá ngắn: {word_count} từ. Nên đạt từ 350–600 từ."))
    elif word_count > 900:
        findings.append(("warning", f"CV quá dài: {word_count} từ. Hãy thử rút ngắn lại."))
    else:
        findings.append(("success", f"Độ dài CV hợp lý: {word_count} từ."))

    # File Type Check
    if not uploaded_file.name.lower().endswith(".pdf"):
        findings.append(("warning", "CV không ở định dạng PDF. Hãy sử dụng PDF để tương thích tốt hơn với ATS."))
    else:
        findings.append(("success", "Đã phát hiện định dạng PDF. Thân thiện với ATS!"))

    # File Size Check
    if uploaded_file.size > 2 * 1024 * 1024:  # 2MB = 2 * 1024 * 1024 bytes
        findings.append(("warning", f"Kích thước tệp quá lớn: {round(uploaded_file.size / (1024*1024), 2)} MB. Hãy giảm xuống dưới 2MB."))
    else:
        findings.append(("success", f"Kích thước tệp tốt: {round(uploaded_file.size / 1024, 1)} KB."))

    sections.append({
        "step": 11,
        "title": "Thuộc tính tài liệu",
        "findings": findings
    })

    # Step 12: Formatting Consistency
    inconsistent_bullets = re.findall(r"\n[^\n•\-–●\*]", text)
    findings = [("warning", "Định dạng dấu đầu dòng có thể không nhất quán. Vui lòng xác minh lại")] if len(inconsistent_bullets) > 5 else [("success", "Định dạng có vẻ nhất quán")]
    sections.append({
        "step": 12,
        "title": "Sự nhất quán trong định dạng",
        "findings": findings
    })

    return sections

def calculate_ats_category_scores(local_results):
    """Calculate the 5 standard categories scores (0-100) based on local analysis results."""
    scores = {
        "Ngữ pháp & Phong cách": 100,
        "Thông tin Liên hệ": 100,
        "Mật độ Từ khóa Kỹ năng": 100,
        "Sự đa dạng Động từ": 100,
        "Định dạng": 100
    }
    
    steps = {step["step"]: step for step in local_results}
    
    # 1. Contact Details (Step 1)
    if 1 in steps:
        findings = steps[1]["findings"]
        success_count = sum(1 for f in findings if f[0] == "success")
        scores["Thông tin Liên hệ"] = round((success_count / max(1, len(findings))) * 100)
        
    # 2. Grammar & Style (Steps 2, 3, 5, 7)
    grammar_subscores = []
    if 2 in steps:
        findings = steps[2]["findings"]
        grammar_subscores.append(100 if any(f[0] == "success" for f in findings) else 50)
    if 3 in steps:
        findings = steps[3]["findings"]
        if any(f[0] == "success" for f in findings):
            grammar_subscores.append(100)
        else:
            msg = next((f[1] for f in findings if f[0] == "warning"), "")
            match = re.search(r"(\d+)", msg)
            count = int(match.group(1)) if match else 1
            grammar_subscores.append(max(30, 100 - count * 10))
    if 5 in steps:
        findings = steps[5]["findings"]
        if any(f[0] == "success" for f in findings):
            grammar_subscores.append(100)
        else:
            count = len([f for f in findings if f[0] == "warning"])
            grammar_subscores.append(max(30, 100 - count * 15))
    if 7 in steps:
        findings = steps[7]["findings"]
        if any(f[0] == "success" for f in findings):
            grammar_subscores.append(100)
        else:
            count = len([f for f in findings if f[0] == "warning"])
            grammar_subscores.append(max(30, 100 - count * 5))
            
    if grammar_subscores:
        scores["Ngữ pháp & Phong cách"] = round(sum(grammar_subscores) / len(grammar_subscores))
        
    # 3. Skill Keyword Density (Steps 4, 8)
    skills_subscores = []
    if 4 in steps:
        findings = steps[4]["findings"]
        success_count = sum(1 for f in findings if f[0] == "success")
        if success_count == 2:
            skills_subscores.append(100)
        elif success_count == 1:
            skills_subscores.append(60)
        else:
            skills_subscores.append(20)
    if 8 in steps:
        findings = steps[8]["findings"]
        skills_subscores.append(100 if any(f[0] == "success" for f in findings) else 40)
        
    if skills_subscores:
        scores["Mật độ Từ khóa Kỹ năng"] = round(sum(skills_subscores) / len(skills_subscores))
        
    # 4. Action Verb Variety (Steps 6, 10)
    verb_subscores = []
    if 6 in steps:
        findings = steps[6]["findings"]
        if any(f[0] == "success" for f in findings):
            verb_subscores.append(100)
        else:
            count = len([f for f in findings if f[0] == "warning"])
            verb_subscores.append(max(30, 100 - count * 8))
    if 10 in steps:
        findings = steps[10]["findings"]
        if any(f[0] == "success" for f in findings):
            verb_subscores.append(100)
        else:
            count = len([f for f in findings if f[0] == "warning"])
            verb_subscores.append(max(40, 100 - count * 10))
            
    if verb_subscores:
        scores["Sự đa dạng Động từ"] = round(sum(verb_subscores) / len(verb_subscores))
        
    # 5. Formatting (Steps 9, 11, 12)
    format_subscores = []
    if 9 in steps:
        findings = steps[9]["findings"]
        if any(f[0] == "success" for f in findings):
            format_subscores.append(100)
        else:
            msg = next((f[1] for f in findings if f[0] == "warning"), "")
            count = len(msg.replace("Thiếu phần:", "").split(","))
            format_subscores.append(max(25, 100 - count * 25))
    if 11 in steps:
        findings = steps[11]["findings"]
        success_count = sum(1 for f in findings if f[0] == "success")
        format_subscores.append(round((success_count / max(1, len(findings))) * 100))
    if 12 in steps:
        findings = steps[12]["findings"]
        format_subscores.append(100 if any(f[0] == "success" for f in findings) else 50)
        
    if format_subscores:
        scores["Định dạng"] = round(sum(format_subscores) / len(format_subscores))
        
    return scores

def calculate_ai_ats_category_scores(ai_results):
    """Calculate the 5 standard categories scores (0-100) based on AI analysis results."""
    scores = {
        "Ngữ pháp & Phong cách": 100,
        "Thông tin Liên hệ": 100,
        "Mật độ Từ khóa Kỹ năng": 100,
        "Sự đa dạng Động từ": 100,
        "Định dạng": 100
    }
    
    def get_score_for_keys(keys, default_score=85):
        total_pos = 0
        total_neg = 0
        found = False
        for key in keys:
            if key in ai_results:
                found = True
                pos = len(ai_results[key].get("Positives", []))
                neg = len(ai_results[key].get("Negatives", []))
                total_pos += pos
                total_neg += neg
        if not found:
            return default_score
        if total_pos + total_neg == 0:
            return 100
        return max(30, min(100, 100 - total_neg * 15 + total_pos * 5))

    scores["Thông tin Liên hệ"] = get_score_for_keys(["Contact Information"])
    scores["Ngữ pháp & Phong cách"] = get_score_for_keys([
        "Spelling & Grammar", "Personal Pronoun Usage", 
        "Complex or Long Sentences", "Passive Voice Usage", 
        "AI-generated Language", "Personal Information / Bias Triggers"
    ])
    scores["Mật độ Từ khóa Kỹ năng"] = get_score_for_keys(["Skills & Keyword Targeting", "Quantified Achievements"])
    scores["Sự đa dạng Động từ"] = get_score_for_keys(["Generic or Weak Phrases", "Repeated Action Verbs"])
    scores["Định dạng"] = get_score_for_keys(["Required Resume Sections", "Visual Formatting or Readability"])
    
    return scores