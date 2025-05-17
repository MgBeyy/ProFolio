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