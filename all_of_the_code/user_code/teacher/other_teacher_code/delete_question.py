# delete_question.py
import flet as ft
import os
import subprocess
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv("./.secret/.env")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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
    page.window_width = 500
    page.window_height = 450
    page.window_resizable = False
    page.bgcolor = "#0F1115"
    page.padding = 40
    
    # Load subjects from database
    subjects_data = get_all_subjects()
    
    subject_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option(subj["name"]) for subj in subjects_data],
        label="Chọn môn học",
        width=300,
        bgcolor="#161920",
        color="white",
        border_color="#161920",
        focused_border_color="#3B71CA",
        label_style=ft.TextStyle(color="#6C757D")
    )
    
    question_dropdown = ft.Dropdown(
        label="Chọn câu hỏi để xóa",
        width=300,
        bgcolor="#161920",
        color="white",
        border_color="#161920",
        focused_border_color="#3B71CA",
        label_style=ft.TextStyle(color="#6C757D")
    )
   
    status_text = ft.Text("", color="red", size=14)
    
    def update_questions(e):
        subject_name = subject_dropdown.value
        question_dropdown.options = []
        question_dropdown.value = None
        
        if subject_name:
            # Find subject ID
            subject_id = next(
                (subj["id"] for subj in subjects_data if subj["name"] == subject_name),
                None
            )
            
            if subject_id:
                questions = get_questions_by_subject(subject_id)
                question_dropdown.options = [
                    ft.dropdown.Option(
                        key=str(q["id"]),
                        text=q["question_text"][:50] + "..." if len(q["question_text"]) > 50 else q["question_text"]
                    ) 
                    for q in questions
                ]
                
                if questions:
                    status_text.value = f"Đã tải {len(questions)} câu hỏi"
                    status_text.color = "blue"
                else:
                    status_text.value = "Không có câu hỏi nào trong môn học này"
                    status_text.color = "orange"
            else:
                status_text.value = "Không tìm thấy môn học"
                status_text.color = "red"
        else:
            status_text.value = ""
        
        page.update()
    
    def back_code(e):
        page.window.close()
        subprocess.run([sys.executable, "user_code/teacher/teacher_main.py"])
    
    def delete_selected_question(e):
        if not subject_dropdown.value:
            status_text.value = "Vui lòng chọn môn học trước!"
            status_text.color = "red"
            page.update()
            return
            
        if not question_dropdown.value:
            status_text.value = "Vui lòng chọn câu hỏi để xóa!"
            status_text.color = "red"
            page.update()
            return
        
        # Get question ID from the selected value
        question_id = int(question_dropdown.value)
        
        if delete_question_from_db(question_id):
            status_text.value = "Câu hỏi đã được xóa thành công!"
            status_text.color = "green"
            # Refresh the questions list
            update_questions(None)
        else:
            status_text.value = "Xóa thất bại!"
            status_text.color = "red"
        
        page.update()
    
    def refresh_data(e):
        """Refresh subjects and questions from database"""
        nonlocal subjects_data
        subjects_data = get_all_subjects()
        subject_dropdown.options = [ft.dropdown.Option(subj["name"]) for subj in subjects_data]
        subject_dropdown.value = None
        question_dropdown.options = []
        question_dropdown.value = None
        status_text.value = "Đã làm mới dữ liệu"
        status_text.color = "blue"
        page.update()
    
    # Set the on_change event for subject dropdown
    subject_dropdown.on_change = update_questions
    
    delete_button = ft.ElevatedButton(
        "Xóa Câu Hỏi", 
        on_click=delete_selected_question,
        width=300,
        style=ft.ButtonStyle(
            bgcolor="#DC3545",  # Red color for delete action
            color="white"
        )
    )
    
    refresh_button = ft.ElevatedButton(
        "Làm mới dữ liệu",
        on_click=refresh_data,
        width=300,
        style=ft.ButtonStyle(
            bgcolor="#17A2B8",  # Blue color for refresh
            color="white"
        )
    )
    
    back_button = ft.ElevatedButton(
        "Quay lại", 
        on_click=back_code,
        width=300,
        style=ft.ButtonStyle(
            bgcolor="#6C757D",  # Gray color for back
            color="white"
        )
    )

    # Main layout - matching the other pages structure
    main_content = ft.Column(
        [
            ft.Text("Xóa Câu Hỏi", size=24, weight="bold", color="white"),
            ft.Container(height=20),
            subject_dropdown,
            ft.Container(height=15),
            question_dropdown,
            ft.Container(height=15),
            delete_button,
            ft.Container(height=10),
            refresh_button,
            ft.Container(height=10),
            status_text,
            ft.Container(height=20),
            back_button
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=5
    )

    # Center the content
    centered_container = ft.Container(
        content=main_content,
        alignment=ft.alignment.center,
        expand=True
    )

    page.add(centered_container)

if __name__ == "__main__":
    ft.app(target=main)