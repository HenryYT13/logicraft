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
    page.title = "Adding Question"
    page.padding = 40  # Adding padding around the content
   
    # Load subjects from database
    subjects_data = get_all_subjects()
    subjects = [subj["name"] for subj in subjects_data]
   
    subject_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option(subj) for subj in subjects],
        label="Chọn môn học",
        width=300,
    )
   
    question_input = ft.TextField(label="Nhập câu hỏi", width=400)
    answer_inputs = [ft.TextField(label=f"Đáp án {i+1}", width=200) for i in range(4)]
    correct_answer_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option(str(i+1)) for i in range(4)],
        label="Chọn đáp án đúng",
        width=300,
    )
   
    question_list = ft.Column()
   
    def back_code(e):
        page.window.close()
        subprocess.run([sys.executable, "administrator/administrator_main.py"])
        
    def add_question_handler(e):
        if not subject_dropdown.value or not question_input.value.strip():
            print("Môn học hoặc câu hỏi không được để trống!")
            return
       
        answers = [inp.value.strip() for inp in answer_inputs]
        if not all(answers):
            print("Tất cả các câu hỏi không được để trống!")
            return
       
        try:
            correct_index = int(correct_answer_dropdown.value) - 1
            if correct_index < 0 or correct_index >= len(answers):
                print("Chọn đáp án đúng không hợp lệ!")
                return
            # Convert to 1-based numbering for database (1, 2, 3, 4)
            correct_option_number = correct_index + 1
        except (ValueError, TypeError):
            print("Chọn đáp án đúng không hợp lệ!")
            return
       
        # Find subject ID
        subject_id = next(
            (subj["id"] for subj in subjects_data if subj["name"] == subject_dropdown.value),
            None
        )
       
        if subject_id is None:
            print("Môn học không tồn tại!")
            return
       
        # Add to database using Supabase
        success = add_question_to_db(
            subject_id,
            question_input.value,
            answers,
            correct_option_number
        )
       
        if success:
            question_entry = ft.Text(
                f"{subject_dropdown.value}: {question_input.value} \n"
                f"Đáp án: {', '.join(answers)} \nĐáp án đúng: {answers[correct_index]}"
            )
           
            question_list.controls.append(question_entry)
            page.update()
           
            # Clear form
            question_input.value = ""
            for inp in answer_inputs:
                inp.value = ""
            correct_answer_dropdown.value = None
            page.update()
            print("Câu hỏi đã được thêm thành công!")
        else:
            print("Lỗi khi thêm câu hỏi vào cơ sở dữ liệu!")
   
    submit_button = ft.ElevatedButton("Thêm câu hỏi", on_click=add_question_handler)
    back_button = ft.ElevatedButton("Quay lại", on_click=lambda e: back_code(e))
   
    page.add(
        ft.Text("Tạo câu hỏi", size=20, color="white"),
        subject_dropdown,
        question_input,
        *answer_inputs,
        correct_answer_dropdown,
        submit_button,
        question_list,
        back_button
    )

if __name__ == "__main__":
    ft.app(target=main)