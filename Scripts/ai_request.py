import os
import google.generativeai as gen_ai
from decouple import config
import json
from datetime import datetime


API_KEY = config("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("API key not found. Please set GOOGLE_API_KEY in your .env file.")
gen_ai.configure(api_key=API_KEY)


def process_file_with_gemini(
    file_path: str,
    prompt_text: str,
    mime_type: str = "application/pdf",
    model_name: str = "gemini-2.5-flash-preview-04-17",
):
    try:
        model = gen_ai.GenerativeModel(model_name)
        if not os.path.exists(file_path):
            return None

        uploaded_file = gen_ai.upload_file(path=file_path, mime_type=mime_type)
        prompt_parts = [prompt_text, uploaded_file]
        response = model.generate_content(prompt_parts)

        gen_ai.delete_file(uploaded_file.name)
        return response.text

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def parse_json_block(raw_text: str) -> dict | None:
    """
    Cleans the given markdown formatted JSON block and converts it to a Python dict object.
    Returns None if there is erroneous JSON.
    """
    try:
        if raw_text.strip().startswith("```json"):
            raw_text = raw_text.strip().lstrip("```json").rstrip("```").strip()
        return json.loads(raw_text)
    except json.JSONDecodeError as e:
        print(f"[HATA] JSON ayrıştırılamadı: {e}\n {raw_text}")
        return None


def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception as e:
        print(f"[HATA] Tarih ayrıştırılamadı: {e}\n {date_str}")
        return None



def generate_interview_question_gemini(
    prompt_text: str,
    model_name: str = "gemini-2.5-flash-preview-04-17",
):
    try:
        model = gen_ai.GenerativeModel(model_name)
        response = model.generate_content(prompt_text)

        return response.text

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

