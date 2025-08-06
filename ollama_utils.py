import requests
import ast
from ast import literal_eval
import re
from semantic_matcher import is_valid_answer

OLLAMA_API_URL = "http://localhost:11434/api/generate"


def generate_cover_letter_ollama(cv_text: str, job_desc: str, language: str = "en") -> str:
    """
    Generate a professional and tailored cover letter using Ollama and Mistral.
    """
    prompt = f"""
You are a professional career advisor and expert in writing compelling cover letters.

Using ONLY the information extracted from the following resume and job description, write a well-formatted, tailored, and impactful cover letter in {language.upper()}:

Resume:
{cv_text}

Job Description:
{job_desc}

Instructions:
- Extract the candidate's name, email, phone number, education, skills, projects, and certifications from the resume (DO NOT make up anything).
- Start with 'Dear [Hiring Manager's Name],' if the name is available in the job description.
  Otherwise, use 'Dear Hiring Manager,'
- Use a **creative and varied introduction**. You may begin with:
  - A thought-provoking question
  - A bold statement about the candidate’s mission or achievement
  - A connection to the company's mission or current AI work
  - A short anecdote about an academic or professional moment
- Avoid repeating generic templates or common phrases across multiple letters.
- Organize the letter into clear paragraphs, separated by extra line breaks for better readability.
- Include a short paragraph (optional but recommended) that connects the company's AI mission with the applicant’s personal vision for AI in real-world impact.
- Highlight relevant technical experience and academic projects aligned with the job.
- Use a professional and enthusiastic tone.
- End with a polite closing, including the applicant's name and contact information (as found in the resume).
- Do NOT use any placeholders like [Your Name] or [Email].
- Vary the phrasing and structure slightly each time to avoid repetitive tone across generated letters.

The final output must look like a complete, high-quality cover letter suitable for submission.
"""

    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={"model": "mistral", "prompt": prompt, "stream": False},
        )
        response.raise_for_status()
        return response.json()["response"].strip()
    except requests.exceptions.RequestException as e:
        print("⚠️ Request failed:", e)
        return "⚠️ Failed to generate cover letter."
    except Exception as e:
        print("⚠️ Unexpected error:", e)
        return "⚠️ Unexpected error occurred."





def extract_skills_ollama(cv_text: str, job_desc: str = None) -> list:
    prompt = f"""
You are an expert NLP assistant and HR analyst.

Your task is to extract a **clean list of professional skills** from the resume text provided below.

Instructions:
- Focus ONLY on hard/technical and domain-specific skills (e.g., "Python", "Data Analysis", "Project Management", "TensorFlow", "AutoCAD", "SEO").
- Ignore soft skills (like communication, leadership, teamwork) and generic words (like motivated, dedicated).
- Do NOT invent or infer skills — extract only those explicitly mentioned.
- Return results as a valid Python list of strings (e.g., ["Python", "Pandas", "AWS"]).
- Do NOT include duplicates or explanations.
- If a skill exists in the resume **but is written differently than it appears in the job description**, you must **return it using the exact name/format used in the job description**.
- Example: If the CV says "Jupyter Notebooks" and the job says "Jupyter", return "Jupyter".
- Be as precise and concise as possible.
- IMPORTANT: Return the result as a valid Python list in **one line only**.
- Do not add any explanation or introduction. Just output the list directly.

Resume Text:
{cv_text}
"""

    if job_desc:
       prompt += f"""

Optional Context — Job Description:
{job_desc}

Use this job description to:
- Prioritize skills that are most relevant to the role.
- Map and standardize skill names from the resume to match how they appear in the job description.
"""


    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={"model": "mistral", "prompt": prompt, "stream": False},
        )
        response.raise_for_status()
        output = response.json()["response"].strip()

        # Try to isolate the list using regex if it's embedded
        match = re.search(r"\[.*?\]", output, re.DOTALL)
        if match:
            output = match.group(0)

        skills = literal_eval(output)
        if isinstance(skills, list):
            return list(set(map(str.strip, skills)))

        return []

    except Exception as e:
        print("⚠️ Failed to extract skills:", e)
        return []








def extract_skills_from_job_ollama(job_desc: str) -> list:
    """
    Extract hard/technical skills from a job description using Ollama.
    """
    prompt = f"""
You are an expert in Natural Language Processing and recruitment analysis.

Your task is to extract a list of **hard or technical skills** mentioned in the following job description.

Instructions:
- Only include specific tools, technologies, programming languages, frameworks, platforms, and professional domain skills.
- Do NOT include soft skills (like leadership, communication, time management).
- Do NOT invent or infer skills — only extract those explicitly mentioned.
- Return the output as a valid Python list of strings (e.g., ["Java", "Spring Boot", "REST APIs"]).
- Avoid duplicates, be precise.
- IMPORTANT: Return the result as a valid Python list in **one line only**.
- Do not add any explanation or introduction. Just output the list directly.
- When extracting skills, assume they will be used as the **reference naming format** for comparison against resumes.
- Avoid variations or synonyms — use the exact wording from the job description.

Job Description:
{job_desc}
"""

    
    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={"model": "mistral", "prompt": prompt, "stream": False},
        )
        response.raise_for_status()
        output = response.json()["response"].strip()

        # Try to isolate the list using regex if it's embedded
        match = re.search(r"\[.*?\]", output, re.DOTALL)
        if match:
            output = match.group(0)

        skills = literal_eval(output)
        if isinstance(skills, list):
            return list(set(map(str.strip, skills)))

        return []

    except Exception as e:
        print("⚠️ Failed to extract skills:", e)
        return []



def compare_cv_to_job(cv_skills, job_skills) -> dict:
    """
    Compares CV skills with job description skills using Ollama-extracted data.
    Returns:
        - matched_skills: List of skills found in both
        - missing_skills: Skills required by job but not found in CV
        - cv_skills_only: Skills present in CV but not mentioned in job
    """

    cv_skills_set = set(map(str.lower, cv_skills))
    job_skills_set = set(map(str.lower, job_skills))

    matched = cv_skills_set & job_skills_set
    missing = job_skills_set - cv_skills_set
    extra = cv_skills_set - job_skills_set

    return {
        "matched_skills": sorted(matched),
        "missing_skills": sorted(missing),
        "cv_skills_only": sorted(extra),
        "cv_skills_raw": cv_skills,
        "job_skills_raw": job_skills
    }









def analyze_cv_advanced(cv_text: str, job_title: str = None) -> dict:
    prompt = f"""
You are a professional career coach and hiring manager with 15+ years of experience.

Analyze the following resume in depth and return a complete structured evaluation.

Your response MUST be a valid Python dictionary with the following keys:

{{
  "overall_rating": float (score between 0.0 and 10.0),
  "summary": str (brief summary of the resume's effectiveness),
  "fit_for_role": str (assessment of how well this CV aligns with the job role{' for: ' + job_title if job_title else ''}),
  "evaluation": {{
    "structure": str (comment on formatting, logical flow, and sections),
    "clarity": str (comment on how clearly the candidate communicates ideas and experience),
    "language_quality": str (comment on grammar, tone, and vocabulary),
    "length": str (too long/short or appropriate),
    "consistency": str (comment on how consistent formatting and content are)
  }},
  "section_feedback": {{
    "Header": str (name, contact info, layout),
    "Summary": str (if present — quality, relevance),
    "Education": str (relevance, structure, detail),
    "Experience": str (impact, clarity, action verbs, metrics),
    "Skills": str (relevance, specificity),
    "Projects": str (if present — quality, connection to role),
    "Certifications": str (if any — strength and relevance),
    "Extras": str (languages, hobbies, volunteering — if relevant)
  }},
  "strengths": list of str (bullet points),
  "weaknesses": list of str (bullet points),
  "recommendations": list of str (concrete suggestions for improvement)
}}

Resume Text:
{cv_text}
"""
    if job_title:
        prompt = f"Target Job Title: {job_title}\n\n" + prompt

    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={"model": "mistral", "prompt": prompt, "stream": False},
        )
        response.raise_for_status()
        output = response.json()["response"]

        match = re.search(r"\{.*\}", output, re.DOTALL)
        if match:
            parsed = literal_eval(match.group(0))
            return parsed
        return {"error": "⚠️ Failed to parse structured response."}

    except Exception as e:
        return {"error": str(e)}




def generate_mock_interview_questions_ollama(cv_text: str, job_title: str, language: str = "en") -> str:
    """
    Generate realistic and tailored mock interview questions using Ollama and Mistral.
    """

    prompt = f"""
You are a professional career coach and technical interviewer with expertise in assessing candidates based on their resumes and job roles.

Your task is to generate a set of **realistic, innovative, challenging, and role-specific** mock interview questions in {language.upper()} based ONLY on the following:

1. The job title: "{job_title}"
2. The resume content below.

Resume:
{cv_text}

=== GUIDELINES ===
- Provide a mix of **technical**, **situational**, and **behavioral** questions.
- Tailor the questions to:
  - The job title itself (e.g., core technologies, system design, algorithms, role-specific deep technical skills)
  - The skills, projects, and experiences found in the resume.
- Include **at least 2 strong technical questions** that are based purely on the job title, even if not mentioned in the resume. These should test deep domain expertise and role-critical knowledge.
- Prioritize:
  - Core technical concepts (e.g. ML, software design, data pipelines, etc.)
  - Real-world problem solving
  - Communication and teamwork
  - Project impact and decision-making
- **Think creatively. Ask unique and thought-provoking questions.**
- **Avoid repeating question themes or rewording the same concept.**
- Each question should be concise but meaningful.
- Ask 10 to 12 questions max.

=== FORMAT ===
Output a numbered list like the following:
1. ...
2. ...
3. ...

Do NOT use any placeholders like [Candidate Name] or [Company Name].
Only return the final list of questions in plain text.
"""

    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={"model": "mistral", "prompt": prompt, "stream": False},
        )
        response.raise_for_status()
        return response.json()["response"].strip()
    except requests.exceptions.RequestException as e:
        print("⚠️ Request failed:", e)
        return "⚠️ Failed to generate interview questions."
    except Exception as e:
        print("⚠️ Unexpected error:", e)
        return "⚠️ Unexpected error occurred."








def evaluate_mock_answers_ollama(cv_text: str, job_title: str, questions: list[str], answers: list[str], language: str = "en") -> str:
    """
    Powerful mock interview evaluator using Ollama + Mistral.
    Returns detailed feedback per answer, scores, and final assessment.
    """


    qa_block = ""
    for i, (q, a) in enumerate(zip(questions, answers)):
        is_valid, score = is_valid_answer(q, a)
        formatted_answer = a if is_valid else "No valid answer was provided."
        qa_block += f"Q{i+1}: {q}\nA{i+1}: {formatted_answer}\n"


    prompt = f"""
You are a senior technical recruiter and interview coach.

Your task is to rigorously evaluate a candidate's mock interview performance based on:
- Their resume
- The job title
- Their answers to common interview questions

🔍 For each question-answer pair, follow this strict process:

1. **First**, verify if the answer is **relevant to the specific question asked**.
   - If the answer does not directly address the question, is off-topic, or contains generic/meaningless content, respond with: **"No valid answer was provided."**
   - Do NOT try to guess or interpret what the candidate "meant."
   - Do NOT evaluate unrelated content.

2. **If the answer is relevant**, evaluate it based on the following criteria:
   - Technical relevance (30%)
   - Communication and clarity (25%)
   - Confidence and structure (20%)
   - Fit for the role (25%)

Then, for each question:
- Provide a score out of 10 **only if the answer is relevant and meaningful (more than 15 words)**
- Give a brief explanation of strengths and weaknesses
- Suggest specific improvements if applicable

⚠️ Additional Rules:
- If the answer is too short (less than 10 words), off-topic, irrelevant, blank, or nonsensical (e.g. "hiuhb", "k", "...."), respond only with: **"No valid answer was provided."** Do not analyze it.
- Do NOT hallucinate or infer missing meaning.
- Do NOT provide a score unless the answer meets the criteria.

- If the answer is No valid answer, irrelevant, off-topic, too short (less than 10 words), blank, or nonsensical (e.g. "hiuhb", "k", "..."), then return the following:

---
**Q{i}: [The question]**  
**A{i}: [The answer]**  
❌ **Invalid Answer**  
🛑 **Score: 0/10**  
💬 **Reason:** No valid answer was provided. The response was either too short, irrelevant, or nonsensical.
---


**If the answer is valid**, return the following format:

---
**Q{i}: [The question]**  
**A{i}: [The answer]**  
✅ **Score: x/10**  
📝 **Evaluation:** [Brief evaluation – strengths and weaknesses]  
💡 **Suggested Improvements:** [Specific, practical advice if applicable]  
---

** for each question **


Finally, include:
- A total average score (excluding invalid answers)
- A concise, professional summary of the candidate’s overall performance
- A final hiring recommendation: **Strong Candidate**, **Needs Improvement**, or **Not Ready**

Resume:
{cv_text}

Job Title:
{job_title}

Interview Responses:
{qa_block}

Your response should be in {language.upper()}, clear, objective, and professional.
"""




    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={"model": "mistral", "prompt": prompt, "stream": False},
        )
        response.raise_for_status()
        return response.json()["response"].strip()
    except requests.exceptions.RequestException as e:
        return f"⚠️ Request failed: {str(e)}"
    except Exception as e:
        return f"⚠️ Unexpected error: {str(e)}"




