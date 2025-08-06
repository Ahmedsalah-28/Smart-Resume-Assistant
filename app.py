import streamlit as st
from cv_parser import extract_text_from_pdf, extract_text_from_docx
from ollama_utils import generate_cover_letter_ollama, analyze_cv_advanced, generate_mock_interview_questions_ollama, evaluate_mock_answers_ollama,extract_skills_ollama, extract_skills_from_job_ollama,compare_cv_to_job
from comparison_utils import get_skills_summary, format_skill_comparison_output, get_skill_match_score
from hybrid_skill_matcher import hybrid_skill_comparison, get_hybrid_score
import re
import time
st.set_page_config(page_title="Smart Resume Assistant", layout="centered")
st.title("\U0001F9E0 Smart Resume Assistant")

# --- Sidebar CV Upload ---
st.sidebar.header("\U0001F4E4 Upload Your Resume")
uploaded_cv = st.sidebar.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])
if uploaded_cv and "cv_text" not in st.session_state:
    ext = uploaded_cv.name.split(".")[-1]
    path = f"temp_cv.{ext}"
    with open(path, "wb") as f:
        f.write(uploaded_cv.read())
    st.session_state.cv_text = extract_text_from_pdf(path) if ext == "pdf" else extract_text_from_docx(path)
    st.sidebar.success("Resume uploaded and processed!")

# --- Task Tabs ---
tab1, tab2, tab3 = st.tabs(["\U0001F4CA Resume Evaluation", "\U0001F680 Cover Letter & Match", "\U0001F9EA Mock Interview"])

# ---------------------- TAB 1: Resume Evaluation ----------------------
with tab1:
    st.markdown("""
    Upload your **resume** and we'll:
    - \U0001F4CA Provide in-depth, structured feedback on your CV quality.
    - ✅ Highlight strengths and weaknesses.
    - \U0001F6E0️ Suggest improvements to boost your job chances.
    """)

    job_title_input = st.text_input("\U0001F3AF Enter the Job Title (Optional)", placeholder="e.g. Machine Learning Engineer")

    if "cv_text" in st.session_state:
        if st.button("\U0001F4CA Run Smart Resume Evaluation"):
            with st.spinner("\U0001F50D Analyzing resume..."):
                result = analyze_cv_advanced(st.session_state.cv_text, job_title_input.strip())

            if "error" in result:
                st.error(result["error"])
            else:
                st.success(f"✅ Overall Rating: {result['overall_rating']} / 10")
                st.markdown(f"**\U0001F4DD Summary:** {result['summary']}")
                st.markdown(f"**\U0001F3AF Fit for Role:** {result['fit_for_role']}")
                st.subheader("\U0001F50D Overall Evaluation:")
                for k, v in result["evaluation"].items():
                    st.markdown(f"- **{k.capitalize()}**: {v}")
                st.subheader("\U0001F9E9 Section-wise Feedback:")
                for section, feedback in result["section_feedback"].items():
                    st.markdown(f"- **{section}**: {feedback}")
                st.subheader("✅ Strengths:")
                for s in result["strengths"]:
                    st.markdown(f"\U0001F539 {s}")
                st.subheader("⚠️ Weaknesses:")
                for w in result["weaknesses"]:
                    st.markdown(f"\U0001F538 {w}")
                st.subheader("\U0001F6E0️ Recommendations:")
                for r in result["recommendations"]:
                    st.markdown(f"✔️ {r}")
    else:
        st.warning("Please upload your resume from the sidebar first.")

# ---------------------- TAB 2: Cover Letter & Match ----------------------
with tab2:
    st.markdown("""
    Paste the **job description**, and choose the task:
    - ✨ Generate a tailored, professional cover letter.
    - \U0001F9E0 Analyze how well your skills match the job.
    """)

    job_desc = st.text_area("\U0001F4CC Paste the job description here")
    selected_task = st.radio("Choose what you want to do:", ["Generate Cover Letter", "Skill Match Analysis"])

    if "cv_text" in st.session_state and job_desc:
        if selected_task == "Generate Cover Letter":
            if st.button("✨ Generate Cover Letter"):
                with st.spinner("\U0001F9E0 Generating..."):
                    cover_letter = generate_cover_letter_ollama(st.session_state.cv_text, job_desc)
                st.subheader("📄 Generated Cover Letter")
                st.text_area("Cover Letter", cover_letter.strip(), height=400)

        elif selected_task == "Skill Match Analysis":
            if st.button("🔍 Analyze Skills"):
                with st.spinner("\U0001F9E0 Analyzing skill match..."):
                    cv_skills = extract_skills_ollama(st.session_state.cv_text, job_desc)
                    job_skills = extract_skills_from_job_ollama(job_desc)

                    summary_literal = get_skills_summary(cv_skills, job_skills)
                    formatted_literal = format_skill_comparison_output(summary_literal)
                    literal_score = get_skill_match_score(summary_literal)

                    hybrid_result = hybrid_skill_comparison(cv_skills, job_skills)
                    formatted_hybrid = hybrid_result["formatted_comparison"]
                    hybrid_score = get_hybrid_score(hybrid_result)

                st.success("✅ Analysis Complete!")
                st.subheader("\U0001F9E0 Skill Match Analysis")

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("📌 Literal Match Score", f"{literal_score * 100:.0f}%")
                    st.text_area("📄 Literal Comparison", formatted_literal, height=250)

                with col2:
                    st.metric("🔀 Hybrid Match Score", f"{hybrid_score:.0f}%", help="This is the most accurate score as it combines semantic similarity with skill extraction.")
                    st.text_area("📄 Hybrid Comparison", formatted_hybrid, height=250)
    else:
        st.warning("Please upload your resume from the sidebar first.")

# ---------------------- TAB 3: Mock Interview ----------------------
with tab3:
    st.markdown("### \U0001F9EA Mock Interview Preparation")
    job_title_mock = st.text_input("\U0001F3AF Enter the Job Title for the Interview")

    if "questions" not in st.session_state:
        st.session_state.questions = []
        st.session_state.answers = []
        st.session_state.index = 0

    if "cv_text" in st.session_state and job_title_mock and st.button("\U0001F3A7 Start Mock Interview"):
        with st.spinner("\U0001F4E1 Generating interview questions..."):
            raw_questions = generate_mock_interview_questions_ollama(st.session_state.cv_text, job_title_mock, language="en")
            questions_cleaned = [q.strip() for q in raw_questions.strip().split("\n") if q.strip()]
            st.session_state.questions = questions_cleaned
            st.session_state.index = 0
            st.session_state.answers = []

    if st.session_state.questions:
        idx = st.session_state.index
        if idx < len(st.session_state.questions):
            st.markdown(f"**\U0001F9E0 Question {idx + 1}:** {st.session_state.questions[idx]}")
            answer = st.text_area("✍️ Your Answer", key=f"answer_{idx}")
            if st.button("➡️ Next"):
                if answer.strip() == "":
                    st.warning("⚠️ Please enter an answer before proceeding.")
                else:
                    st.session_state.answers.append(answer)
                    st.session_state.index += 1
                    st.rerun()
        else:
            st.success("✅ Interview Completed!")
            st.subheader("\U0001F4DD Your Responses with Feedback:")
            for i, (q, a) in enumerate(zip(st.session_state.questions, st.session_state.answers)):
                st.markdown(f"**Q{i+1}.** {q}")
                st.markdown(f"**Your Answer:** {a}")

            with st.spinner("\U0001F9E0 Evaluating your answers..."):
                feedback = evaluate_mock_answers_ollama(
                    st.session_state.cv_text,
                    job_title_mock,
                    st.session_state.questions,
                    st.session_state.answers
                )

            st.subheader("\U0001F50E Evaluation Feedback:")
            st.markdown(feedback)
            st.markdown("---")


