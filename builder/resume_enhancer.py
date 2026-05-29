import google.generativeai as genai
import os

def list_available_gemini_models(api_key):
    if not api_key:
        return []
    try:
        genai.configure(api_key=api_key)
        return [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    except Exception:
        return []

def get_suitable_gemini_model(api_key):
    available_models = list_available_gemini_models(api_key)
    if not available_models:
        return "gemini-1.5-flash"
    preferred = ["gemini-2.5-flash", "gemini-1.5-flash-8b", "gemini-2.0-flash", "gemini-1.5-flash"]
    for p in preferred:
        for m in available_models:
            if m.name == p or m.name == f"models/{p}": return m.name
    return available_models[0].name

def generate_prompt(section_name, text_content, tone="Professional"):
    base_prompt = f"As an expert resume writer, rewrite the following {section_name} to be highly impactful, concise, and ATS-friendly, using a {tone} tone. Focus on achievements and strong action verbs. IMPORTANT: Output must be written in Vietnamese."
    if section_name == "professional summary":
        return f"{base_prompt} Ensure it is between 30 to 70 words.\n\nHere is the summary:\n{text_content}\n\nEnhanced Summary:"
    elif section_name == "job responsibility" or section_name == "project description":
        return f"Rewrite the following into a max of 3 concise bullet points in Vietnamese. Start with action verbs. Provide ONLY the bullet points, one per line. Do not output any intro or outro text.\n\nContent:\n{text_content}\n\nEnhanced:"
    elif section_name == "skills section":
        return f"Extract technical and soft skills. List 'Kỹ năng chuyên môn: ...' on one line, and 'Kỹ năng mềm: ...' on the next. Output in Vietnamese.\n\nText:\n{text_content}\n\nEnhanced Skills:"
    elif section_name == "achievements":
        return f"Rewrite achievements into comma-separated impactful sentences in Vietnamese.\n\nAchievements:\n{text_content}\n\nEnhanced:"
    return f"{base_prompt}\n\nHere is the content:\n{text_content}\n\nEnhanced Content:"

def enhance_content_with_gemini(section_name, text_content, tone, api_key):
    if not api_key: return text_content
    model_name = get_suitable_gemini_model(api_key)
    if not model_name: raise Exception("No suitable Gemini model found.")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    prompt = generate_prompt(section_name, text_content, tone)
    
    response = model.generate_content(prompt)
    if response and response.text:
        return response.text.strip()
    return text_content