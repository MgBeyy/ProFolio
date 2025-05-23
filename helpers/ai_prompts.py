ANALYZE_CV_PROMPT = """You are given a resume below. Analyze it and return the data in the following structured JSON format. Do not include any explanation or extra commentary. Return only valid JSON. The json tags must be in English and match the template. The information in it must match the language of your CV. Dates must be in YYYY-MM-DD format. If there is no day, you can type 01. However, if there is no year or month, it returns an empty string.

{
  "summary": "A short general summary (if there is no summary in the pdf file, write one in the language of CV).",
  "experience": [
    {
      "company": "Company name",
      "position": "Job title",
      "start_date": "YYYY-MM-DD",
      "end_date": "YYYY-MM-DD",
      "description": "Description of the work"
    }
  ],
  "education": [
    {
      "school": "School name",
      "degree": "Degree or major",
      "department": "Department name",
      "start_date": "YYYY-MM-DD",
      "end_date": "YYYY-MM-DD",
      "description": "Optional details about education"
    }
  ],
  "certifications": [
    {
      "name": "Certificate title",
      "organization": "Issuing organization",
      "start_date": "YYYY-MM-DD",
      "end_date": "YYYY-MM-DD",
      "description": "Optional description"
    }
  ],
  "languages": [
    {
      "language": "Language name",
      "level": "Proficiency level (e.g., Beginner, Intermediate, Advanced, Native)"
    }
  ],
  "skills": [
    {
      "name": "Skill name",
      "level": "Proficiency level"
    }
  ],
  "projects": [
    {
      "title": "Project title",
      "description": "Project description",
      "technologies": "Comma-separated list of technologies",
      "project_url": "Link to the project if available"
    }
  ]
}
"""


def get_interview_prompt(skills, language):
    INTERVIEW_PROMPT = """
    You are a career counselor conducting a mock interview with a candidate. The candidate possesses the skills listed below. Please generate one interview question related to one of these skills. Focus on the technical skills. Return the output strictly in the following JSON format. Do not include any additional text, comments, or explanations. Use only valid JSON. The keys in the JSON must be in English and match the structure exactly. The question must be in the language specified in the language field. If the language is not specified, return the question in English.
    JSON Output Format:

    {{
      "skill": "<The selected skill>",
      "question": "<The interview question in the specified language>"
    }}

    Use the skills provided below:

    {skills}

    Language: {language}"""
    return INTERVIEW_PROMPT.format(skills=skills, language=language if language else "")


def get_answer_analysis_prompt(question, answer, language):
    ANALYSIS_PROMPT = """
    You are an expert career counselor. An interviewer asks the following question to a candidate, and the candidate provides the following answer. Analyze the candidate’s response and return the output strictly in the JSON format specified below. Do not add any additional text, comments, or annotations. Use only valid JSON. The keys in the JSON must be in English and must exactly match the structure below. The analysis must be written in the language specified in the `language` field. If no language is specified, return the analysis in English. You can call the candidate “you” directly in your response. 

    JSON Output Format:
    {{
      "correct_part": "<The part of the answer that is correct. If the answer is completely wrong, return an empty string.>",
      "wrong_part": "<The part of the answer that is incorrect and why it is incorrect and what the candidate should have said. If the answer is completely correct, return an empty string.>",
      "degree": "<A score between 0 and 10 that reflects the quality of the candidate's answer.>"
    }}

    Question: {question}
    Answer: {answer}
    Language: {language}
"""

    return ANALYSIS_PROMPT.format(
        question=question, answer=answer, language=language if language else ""
    )


def get_interview_feedback_prompt(interview_questions, language=None):
    PROMPT = """
    You are an expert career counselor. An interviewer asks several questions to a candidate, and the candidate provides answers. Analyze all of the answers and provide general feedback about the candidate's performance. Return the output strictly in the JSON format specified below. Do not add any additional text, comments, or explanations. Use only valid JSON. The keys in the JSON must be in English and match the structure exactly. The analysis must be written in the language specified in the `language` field. If no language is specified, return the feedback in English. Address the candidate directly in your response.

    JSON Output Format:
    {{
      "positive_points": "<The strengths in the candidate's answers.>",
      "negative_points": "<The weaknesses or areas for improvement.>",
      "score": "<A number between 0 and 10 representing the overall performance.>"
    }}

    Interview Questions:
    {interview_questions}

    Language: {language}
"""
    return PROMPT.format(
        interview_questions=interview_questions, language=language if language else ""
    )
