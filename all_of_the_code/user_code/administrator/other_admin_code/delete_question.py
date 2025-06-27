# delete_question.py
import flet as ft
import os
import subprocess
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
dotenv_path = "./.secret/.env"
print(f"Looking for .env file at: {dotenv_path}")
print(f".env file exists: {os.path.exists(dotenv_path)}")

load_dotenv(dotenv_path)

# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

print(f"SUPABASE_URL: {url}")
print(f"SUPABASE_KEY: {'*' * len(key) if key else 'None'}")

if not url or not key:
    print("Error: SUPABASE_URL and SUPABASE_KEY must be set in the .env file")
    print("Please check your .env file contains:")
    print("SUPABASE_URL=your_supabase_url")
    print("SUPABASE_KEY=your_supabase_key")
    sys.exit(1)

supabase: Client = create_client(url, key)

def get_all_subjects():
    """Get all subjects from the database"""
    try:
        response = supabase.table("subjects").select("*").execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error fetching subjects: {e}")
        return []

def get_questions_by_subject(subject_id):
    """Get all questions for a specific subject"""
    try:
        response = supabase.table("questions").select("*").eq("subject_id", subject_id).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error fetching questions: {e}")
        return []

def delete_question_from_db(question_id):
    """Delete a question from the database"""
    try:
        response = supabase.table("questions").delete().eq("id", question_id).execute()
        return True
    except Exception as e:
        print(f"Error deleting question: {e}")
        return False

def main(page: ft.Page):
    page.title = "Xóa câu hỏi"
    page.padding = 40  # Adding padding around the content
    
    # Load subjects from database
    subjects_data = get_all_subjects()
    subjects = [subj["name"] for subj in subjects_data]
    
    subject_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option(subj) for subj in subjects],
        label="Chọn môn học",
        width=300,
    )
    
    question_dropdown = ft.Dropdown(
        label="Chọn câu hỏi để xóa",
        width=300,
    )
   
    status_text = ft.Text("", color="red")
    
    def update_questions(e):
        subject_name = subject_dropdown.value
        question_dropdown.options = []
        
        if subject_name:
            # Find subject ID
            subject_id = next(
                (subj["id"] for subj in subjects_data if subj["name"] == subject_name),
                None
            )
            
            if subject_id:
                questions = get_questions_by_subject(subject_id)
                question_dropdown.options = [
                    ft.dropdown.Option(q["question_text"], data=q["id"]) 
                    for q in questions
                ]
        question_dropdown.update()
    
    def back_code(e):
        page.window.close()
        subprocess.run([sys.executable, "administrator/administrator_main.py"])
    
    def delete_selected_question(e):
        if not question_dropdown.value:
            status_text.value = "Vui lòng chọn câu hỏi để xóa!"
            status_text.color = "red"
            status_text.update()
            return
            
        # Find the question ID from the selected option
        question_id = None
        for option in question_dropdown.options:
            if option.key == question_dropdown.value:
                question_id = option.data
                break
        
        if question_id and delete_question_from_db(question_id):
            status_text.value = "Câu hỏi đã được xóa thành công!"
            status_text.color = "green"
            # Refresh the questions list
            update_questions(None)
            question_dropdown.value = None
            question_dropdown.update()
        else:
            status_text.value = "Xóa thất bại!"
            status_text.color = "red"
        status_text.update()
    
    subject_dropdown.on_change = update_questions
    
    delete_button = ft.ElevatedButton("Xóa Câu Hỏi", on_click=delete_selected_question)
    back_button = ft.ElevatedButton("Quay lại", on_click=lambda e: back_code(e))
    
    page.add(
        ft.Text("Xoá câu hỏi", size=20, color="white"), 
        subject_dropdown, 
        question_dropdown, 
        delete_button, 
        status_text, 
        back_button
    )

if __name__ == "__main__":
    ft.app(target=main)