import string
import numpy as np
import faiss
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer

MODEL = SentenceTransformer("paraphrase-MiniLM-L6-v2", device="cpu")
MODEL = torch.quantization.quantize_dynamic(MODEL, {torch.nn.Linear}, dtype=torch.qint8)


import os

class JobRecommendationSystem:
    def __init__(self, jobs_csv):
        self.jobs_df = pd.read_csv(jobs_csv)
        self.jobs_df["job_text"] = (
            self.jobs_df["workplace"].astype(str) + " " +
            self.jobs_df["working_mode"].astype(str) + " " +
            self.jobs_df["position"].astype(str) + " " +
            self.jobs_df["job_role_and_duties"].astype(str) + " " +
            self.jobs_df["requisite_skill"].astype(str)
        )

        self.jobs_texts = self.jobs_df["job_text"].tolist()
        self.job_info = self.jobs_df.copy()
        
        embed_path = "data/dataset/job_embeddings.npy"
        if os.path.exists(embed_path):
            self.job_embeddings = np.load(embed_path)
        else:
            print("Computing embeddings for the first time... This may take a while.")
            self.job_embeddings = MODEL.encode(
                self.jobs_texts, convert_to_numpy=True
            ).astype(np.float32)
            np.save(embed_path, self.job_embeddings)

        self.dim = self.job_embeddings.shape[1]
        self.index = faiss.IndexFlatIP(self.dim)
        self.index.add(self.job_embeddings)

    def clean_text(self, text):
        
        return text.lower().translate(str.maketrans("", "", string.punctuation)).strip()

    def filter_top_jobs(self, resume_text, top_n=100):
        
        vectorizer = TfidfVectorizer()
        job_vectors = vectorizer.fit_transform(self.jobs_texts)
        resume_vector = vectorizer.transform([resume_text])
        similarity_scores = (job_vectors @ resume_vector.T).toarray().flatten()
        top_indices = np.argsort(similarity_scores)[-top_n:]
        return (
            [self.jobs_texts[i] for i in top_indices],
            self.job_info.iloc[top_indices].reset_index(drop=True),
            self.job_embeddings[top_indices],
        )

    def recommend_jobs(self, resume_text, top_n=20):
        
        resume_text = self.clean_text(resume_text)
        
        resume_embedding = MODEL.encode([resume_text], convert_to_numpy=True).astype(
            np.float16
        )
        
        distances, indices = self.index.search(resume_embedding.astype(np.float16), top_n)
        
        recommended_jobs = self.job_info.iloc[indices[0]].to_dict(orient="records")
        return {"recommended_jobs": recommended_jobs}

    def recommend_jobs_tfidf(self, resume_text, top_n=20):
        
        resume_text = self.clean_text(resume_text)
        
        vectorizer = TfidfVectorizer()
        job_vectors = vectorizer.fit_transform(self.jobs_texts)
        resume_vector = vectorizer.transform([resume_text])
        similarity_scores = (job_vectors @ resume_vector.T).toarray().flatten()
        
        top_indices = np.argsort(similarity_scores)[-top_n:][::-1]
        
        recommended_jobs = self.job_info.iloc[top_indices].to_dict(orient="records")
        return {"recommended_jobs": recommended_jobs}

    def recommend_jobs_hybrid(self, resume_text, top_n=20, alpha=0.5):
        """
        KẾT HỢP Ngữ nghĩa (FAISS) và Từ khóa (TF-IDF).
        alpha: Tỉ lệ trọng số của FAISS (Semantic). 1.0 = Chỉ Semantic, 0.0 = Chỉ Keyword.
        """
        resume_text_clean = self.clean_text(resume_text)
        
        # 1. TF-IDF Scores
        vectorizer = TfidfVectorizer()
        job_vectors = vectorizer.fit_transform(self.jobs_texts)
        resume_vector = vectorizer.transform([resume_text_clean])
        tfidf_scores = (job_vectors @ resume_vector.T).toarray().flatten()
        
        if tfidf_scores.max() - tfidf_scores.min() > 0:
            tfidf_scores = (tfidf_scores - tfidf_scores.min()) / (tfidf_scores.max() - tfidf_scores.min())
        else:
            tfidf_scores = np.zeros_like(tfidf_scores)
            
        # 2. FAISS Scores
        resume_embedding = MODEL.encode([resume_text_clean], convert_to_numpy=True).astype(np.float16)
        n_jobs = self.job_embeddings.shape[0]
        distances, indices = self.index.search(resume_embedding.astype(np.float16), n_jobs)
        
        faiss_scores = np.zeros(n_jobs)
        for score, idx in zip(distances[0], indices[0]):
            faiss_scores[idx] = score
            
        if faiss_scores.max() - faiss_scores.min() > 0:
            faiss_scores = (faiss_scores - faiss_scores.min()) / (faiss_scores.max() - faiss_scores.min())
        else:
            faiss_scores = np.zeros_like(faiss_scores)
            
        # 3. Hybrid Scoring
        hybrid_scores = alpha * faiss_scores + (1 - alpha) * tfidf_scores
        top_indices = np.argsort(hybrid_scores)[-top_n:][::-1]
        
        recommended_jobs = self.job_info.iloc[top_indices].copy()
        # Ta có thể thêm điểm số vào kết quả nếu muốn hiển thị
        recommended_jobs['match_score'] = hybrid_scores[top_indices]
        
        return {"recommended_jobs": recommended_jobs.to_dict(orient="records")}
