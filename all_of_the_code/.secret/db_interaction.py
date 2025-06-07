# supabase_utils.py
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '.secret', '.env')
load_dotenv(dotenv_path)

# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def get_all_subjects():
    response = supabase.table("subjects").select("*").execute()
    return response.data if response.data else []

def get_questions_by_subject(subject_id):
    response = supabase.table("questions").select("*").eq("subject_id", subject_id).execute()
    return response.data if response.data else []

def add_question(subject_id, question, options, correct_answer):
    supabase.table("questions").insert({
        "subject_id": subject_id,
        "question": question,
        "options": options,
        "correct_answer": correct_answer
    }).execute()

def delete_question(question_id):
    supabase.table("questions").delete().eq("id", question_id).execute()

def add_subject(name):
    supabase.table("subjects").insert({"name": name}).execute()
