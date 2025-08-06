from sentence_transformers import SentenceTransformer, util
import torch


# Load model once
model = SentenceTransformer("all-MiniLM-L6-v2")

def get_semantic_matches(cv_skills, jd_skills, threshold=0.5):
    """
    Returns a list of semantically matched skill pairs (cv_skill, jd_skill, similarity_score)
    """
    if not cv_skills or not jd_skills:
        return []

    # Ensure inputs are lists (not single strings)
    if isinstance(cv_skills, str):
        cv_skills = [cv_skills]
    if isinstance(jd_skills, str):
        jd_skills = [jd_skills]

    cv_embeddings = model.encode(cv_skills, convert_to_tensor=True)
    jd_embeddings = model.encode(jd_skills, convert_to_tensor=True)

    similarity_matrix = util.pytorch_cos_sim(cv_embeddings, jd_embeddings)

    matched = []
    for i, cv_skill in enumerate(cv_skills):
        for j, jd_skill in enumerate(jd_skills):
            try:
                sim_score = similarity_matrix[i][j].item()
                if sim_score >= threshold:
                    matched.append((cv_skill, jd_skill, round(sim_score, 2)))
            except IndexError:
                # Skip invalid index pair (in case of malformed input)
                continue

    return matched





def is_valid_answer(question: str, answer: str, threshold: float = 0.3) -> tuple[bool, float]:
    """
    Measures the similarity between the answer and the question using BERT.
    If the score is below the threshold: the answer is considered invalid.
    """
    if not answer.strip() or len(answer.split()) < 5:
        return False, 0.0  

    embeddings = model.encode([question, answer], convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()

    return similarity >= threshold, similarity
