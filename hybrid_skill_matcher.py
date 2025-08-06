from semantic_matcher import get_semantic_matches

def hybrid_skill_comparison(cv_skills, jd_skills, threshold=0.5) -> dict:
    matches = get_semantic_matches(cv_skills, jd_skills, threshold=threshold)

    matched_jd_skills = set()
    partial_matches = []
    exact_matches = []

    for cv_skill, jd_skill, score in matches:
        if score >= threshold:
            matched_jd_skills.add(jd_skill)
            if score >= 0.9:
                exact_matches.append((cv_skill, jd_skill, score))
            else:
                partial_matches.append((cv_skill, jd_skill, score))

    missing_skills = [skill for skill in jd_skills if skill not in matched_jd_skills]
    extra_skills = [skill for skill in cv_skills if all(skill != m[0] for m in matches)]

    formatted = "### ✅ Matched Skills:\n"
    for cv_skill, jd_skill, score in exact_matches + partial_matches:
        percent = round(score * 100, 1)
        formatted += f"- **{cv_skill}** matched with **{jd_skill}** ({percent}%)\n"

    if missing_skills:
        formatted += "\n### ❌ Missing Skills from CV:\n"
        for skill in missing_skills:
            formatted += f"- {skill}\n"

    if extra_skills:
        formatted += "\n### 🧠 Extra Skills in CV:\n"
        for skill in extra_skills:
            formatted += f"- {skill}\n"

    return {
        "exact_matches": exact_matches,
        "partial_matches": partial_matches,
        "missing_skills": missing_skills,
        "extra_skills": extra_skills,
        "cv_skills_raw": cv_skills,
        "job_skills_raw": jd_skills,
        "formatted_comparison": formatted
    }





def get_hybrid_score(hybrid_result: dict) -> float:
    total_required = (
        len(hybrid_result["exact_matches"]) +
        len(hybrid_result["partial_matches"]) +
        len(hybrid_result["missing_skills"])
    )
    if total_required == 0:
        return 0.0
    matched = len(hybrid_result["exact_matches"]) + len(hybrid_result["partial_matches"])
    return round((matched / total_required) * 100, 2)
