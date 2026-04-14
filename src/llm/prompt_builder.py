# src/llm/prompt_builder.py

def build_resume_scoring_prompt(resume_text: str, job_description: str) -> str:
    """
    Build a structured prompt for resume-to-job fit scoring.
    Returns a prompt string that instructs the LLM to respond in JSON.
    """
    prompt = f"""
You are an expert technical recruiter and career coach with 15+ years of experience 
evaluating resumes for data science, engineering, and technology roles.

Analyze the following resume against the job description and provide a detailed fit assessment.

---
RESUME:
{resume_text.strip()}

---
JOB DESCRIPTION:
{job_description.strip()}

---
INSTRUCTIONS:
Respond ONLY with a valid JSON object. No preamble, no explanation, no markdown.
Use exactly this structure:

{{
  "fit_score": <integer 0-100>,
  "matched_skills": [<list of skills found in both resume and job description>],
  "missing_skills": [<list of important skills in job description but missing from resume>],
  "strengths": "<2-3 sentence summary of the candidate's strongest points for this role>",
  "suggestions": "<2-3 specific, actionable suggestions to improve fit for this role>",
  "experience_match": "<one of: 'Under-qualified', 'Partially qualified', 'Well qualified', 'Over-qualified'>",
  "recommendation": "<one of: 'Strong Match', 'Good Match', 'Partial Match', 'Poor Match'>"
}}

Scoring guide:
- 90-100: Near perfect match, apply immediately
- 75-89:  Strong match, minor gaps
- 60-74:  Good match, some upskilling needed
- 40-59:  Partial match, significant gaps
- 0-39:   Poor match, major skill/experience mismatch

Be honest, specific, and actionable. Focus on technical skills, experience level, and role alignment.
"""
    return prompt.strip()
