
# 🧠 Smart Resume Assistant

**Smart Resume Assistant** is an AI-powered Streamlit web app that helps job seekers optimize their resumes, generate customized cover letters, and prepare for interviews — all in one place.

It uses **Ollama** with the **Mistral model** for local LLM tasks and **BERT-based semantic similarity** for advanced evaluation.

---

## 🚀 Features

### 📄 1. Resume Evaluation
- Upload a resume (PDF or DOCX).
- Automatically analyze structure, clarity, consistency, and job-fit.
- Highlight strengths and weaknesses.
- Get improvement recommendations.

### ✉️ 2. Cover Letter & Skill Match
- Paste a job description.
- Generate a customized, professional cover letter.
- Extract and compare skills between the resume and job.
- View **literal** and **semantic (hybrid)** match scores.

### 🎤 3. Mock Interview
- Get realistic, role-specific interview questions.
- Answer each question interactively.
- Get AI-powered evaluation, scoring, and improvement suggestions.

---

## 📁 Project Structure

```
.
├── app.py                       # Main Streamlit app
├── cv_parser.py                # Resume parsing (PDF/DOCX)
├── ollama_utils.py             # Ollama prompts, LLM evaluation
├── comparison_utils.py         # Skill matching + scoring
├── hybrid_skill_matcher.py     # Semantic + literal comparison
├── semantic_matcher.py         # BERT-based similarity checker
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

---

## 📦 Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/smart-resume-assistant.git
cd smart-resume-assistant
```

### 2. (Optional) Create a virtual environment using `conda`

```bash
conda create -n smart-resume python=3.10
conda activate smart-resume
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Ollama locally

Make sure you have [Ollama](https://ollama.com) installed and the **Mistral** model is available:

```bash
ollama run mistral
```

> ✅ This app assumes the Ollama API is running at: `http://localhost:11434/api/generate`  
> 🌐 Once the models are downloaded, it works **offline**.

### 5. Launch the Streamlit app

```bash
streamlit run app.py
```

---

## ⚙️ Customization

- Modify similarity thresholds in `semantic_matcher.py` and `hybrid_skill_matcher.py` to control skill match strictness.
- Replace the `mistral` model in Ollama with another LLM if needed.

---

## 📌 Example Use Case

1. Upload your resume (PDF or DOCX)
2. Paste a job description
3. Choose a task:
   - ✅ Generate a custom cover letter  
   - 📊 Analyze skill match  
   - 🎤 Practice interview questions
4. Get instant feedback and improvement suggestions powered by LLMs

---

## 🧠 Future Enhancements

- 🌍 Support for multiple languages (e.g., Arabic cover letters)
- ☁️ Cloud deployment (Docker, Hugging Face Spaces)
- 🛠 Resume builder + LinkedIn integration
- 📤 Export results to PDF

---

## 👤 Author

**Ahmed Salah**  
Faculty of Engineering, Helwan University  
Computers and Systems Department

---

## 📄 License

This project is licensed under the MIT License – feel free to use, modify, and share.
