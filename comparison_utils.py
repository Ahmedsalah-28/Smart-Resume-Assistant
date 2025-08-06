import re
from ollama_utils import compare_cv_to_job


def normalize_skill(skill: str) -> str:
    """
    Normalize skill strings for better matching.
    """
    return re.sub(r'[\s_\-\.]', '', skill.lower())

def get_skills_summary(cv_skills: list, job_skills: list) -> dict:
    comparison = compare_cv_to_job(cv_skills, job_skills)

    # Normalize skills
    normalized_cv_skills = {normalize_skill(skill): skill for skill in comparison["cv_skills_raw"]}
    normalized_job_skills = {normalize_skill(skill): skill for skill in comparison["job_skills_raw"]}

    matched_skills = []
    missing_skills = []
    for norm_job_skill, original_job_skill in normalized_job_skills.items():
        if norm_job_skill in normalized_cv_skills:
            matched_skills.append(original_job_skill)
        else:
            missing_skills.append(original_job_skill)

    extra_skills = [
        original_cv_skill for norm_cv_skill, original_cv_skill in normalized_cv_skills.items()
        if norm_cv_skill not in normalized_job_skills
    ]

    return {
        "cv_skills": list(normalized_cv_skills.values()),
        "job_skills": list(normalized_job_skills.values()),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "extra_skills_in_cv": extra_skills
    }




def get_skill_match_score(summary: dict) -> float:
    total_required = len(summary["matched_skills"]) + len(summary["missing_skills"])
    if total_required == 0:
        return 0.0
    return round(len(summary["matched_skills"]) / total_required, 2)




def format_skill_comparison_output(summary: dict) -> str:
    output = []

    matched = summary.get("matched_skills", [])
    missing = summary.get("missing_skills", [])
    extra = summary.get("extra_skills_in_cv", [])

    output.append(f"✅ Matched Skills ({len(matched)}):")
    output.append(", ".join(matched) or "None")

    output.append(f"\n❌ Missing Skills from CV ({len(missing)}):")
    output.append(", ".join(missing) or "None")

    output.append(f"\n📎 Extra Skills in CV ({len(extra)}):")
    output.append(", ".join(extra) or "None")

    return "\n".join(output)
