# add_question.py
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

def add_question_to_db(subject_id, question, options, correct_option_number):
    """Add a question to the database"""
    try:
        response = supabase.table("questions").insert({
            "subject_id": subject_id,
            "question_text": question,
            "option_1": options[0],
            "option_2": options[1], 
            "option_3": options[2],
            "option_4": options[3],
            "correct_option": str(correct_option_number)
        }).execute()
        return True
    except Exception as e:
        print(f"Error adding question: {e}")
        return False

def main(page: ft.Page):
    page.title = "Thêm câu hỏi"
    page.window_width = 600
    page.window_height = 700
    page.window_resizable = False
    page.bgcolor = "#0F1115"
    page.padding = 40
   
    # Load subjects from database
    subjects_data = get_all_subjects()
    subjects = [subj["name"] for subj in subjects_data]
   
    subject_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option(subj) for subj in subjects],
        label="Chọn môn học",
        width=400,
        bgcolor="#161920",
        color="white",
        border_color="#161920",
        focused_border_color="#3B71CA",
        label_style=ft.TextStyle(color="#6C757D")
    )
   
    question_input = ft.TextField(
        label="Nhập câu hỏi", 
        width=400,
        multiline=True,
        min_lines=2,
        max_lines=4,
        bgcolor="#161920",
        color="white",
        border_color="#161920",
        focused_border_color="#3B71CA",
        label_style=ft.TextStyle(color="#6C757D")
    )
    
    answer_inputs = []
    for i in range(4):
        answer_input = ft.TextField(
            label=f"Đáp án {i+1}", 
            width=400,
            bgcolor="#161920",
            color="white",
            border_color="#161920",
            focused_border_color="#3B71CA",
            label_style=ft.TextStyle(color="#6C757D")
        )
        answer_inputs.append(answer_input)
    
    correct_answer_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option(str(i+1)) for i in range(4)],
        label="Chọn đáp án đúng",
        width=400,
        bgcolor="#161920",
        color="white",
        border_color="#161920",
        focused_border_color="#3B71CA",
        label_style=ft.TextStyle(color="#6C757D")
    )
   
    status_text = ft.Text("", color="green", size=14)
    
    def back_code(e):
        page.window.close()
        subprocess.run([sys.executable, "user_code/teacher/teacher_main.py"])
        
    def add_question_handler(e):
        if not subject_dropdown.value or not question_input.value.strip():
            status_text.value = "Môn học hoặc câu hỏi không được để trống!"
            status_text.color = "red"
            page.update()
            return
       
        answers = [inp.value.strip() for inp in answer_inputs]
        if not all(answers):
            status_text.value = "Tất cả các câu hỏi không được để trống!"
            status_text.color = "red"
            page.update()
            return
       
        if not correct_answer_dropdown.value:
            status_text.value = "Vui lòng chọn đáp án đúng!"
            status_text.color = "red"
            page.update()
            return
       
        try:
            correct_index = int(correct_answer_dropdown.value) - 1
            if correct_index < 0 or correct_index >= len(answers):
                status_text.value = "Chọn đáp án đúng không hợp lệ!"
                status_text.color = "red"
                page.update()
                return
            # Convert to 1-based numbering for database (1, 2, 3, 4)
            correct_option_number = correct_index + 1
        except (ValueError, TypeError):
            status_text.value = "Chọn đáp án đúng không hợp lệ!"
            status_text.color = "red"
            page.update()
            return
       
        # Find subject ID
        subject_id = next(
            (subj["id"] for subj in subjects_data if subj["name"] == subject_dropdown.value),
            None
        )
       
        if subject_id is None:
            status_text.value = "Môn học không tồn tại!"
            status_text.color = "red"
            page.update()
            return
       
        # Add to database using Supabase
        success = add_question_to_db(
            subject_id,
            question_input.value,
            answers,
            correct_option_number
        )
       
        if success:
            status_text.value = "Câu hỏi đã được thêm thành công!"
            status_text.color = "green"
           
            # Clear form
            question_input.value = ""
            for inp in answer_inputs:
                inp.value = ""
            correct_answer_dropdown.value = None
            subject_dropdown.value = None
            page.update()
        else:
            status_text.value = "Lỗi khi thêm câu hỏi vào cơ sở dữ liệu!"
            status_text.color = "red"
            page.update()
   
    submit_button = ft.ElevatedButton(
        "Thêm câu hỏi", 
        on_click=add_question_handler,
        width=400,
        style=ft.ButtonStyle(
            bgcolor="#28A745",  # Green color for add action
            color="white"
        )
    )
    
    back_button = ft.ElevatedButton(
        "Quay lại", 
        on_click=back_code,
        width=400,
        style=ft.ButtonStyle(
            bgcolor="#6C757D",  # Gray color for back
            color="white"
        )
    )

    # Main layout - matching the delete question page structure
    main_content = ft.Column(
        [
            ft.Text("Thêm Câu Hỏi", size=24, weight="bold", color="white"),
            ft.Container(height=20),
            subject_dropdown,
            ft.Container(height=15),
            question_input,
            ft.Container(height=15),
            *[ft.Container(content=inp, margin=ft.margin.only(bottom=10)) for inp in answer_inputs],
            ft.Container(height=5),
            correct_answer_dropdown,
            ft.Container(height=15),
            submit_button,
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