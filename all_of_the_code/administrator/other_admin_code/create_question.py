# add_question.py
import flet as ft
import os
import subprocess
import sys
from .secret import db_interaction  # Import the database interaction module

def main(page: ft.Page):
    page.title = "Adding Question"
    page.padding = 40  # Adding padding around the content
    
    # Load subjects from database
    subjects_data = db_interaction.get_all_subjects()
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

    def add_question_to_db(e):
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
        
        # Add to database
        success = db_interaction.add_question(
            subject_id,
            question_input.value,
            answers,
            correct_index
        )
        
        if success:
            question_entry = ft.Text(
                f"{subject_dropdown.value}: {question_input.value} \n"
                f"Đáp án: {', '.join(answers)} \nĐáp án đúng: {answers[correct_index]}"
            )
            
            question_list.controls.append(question_entry)
            page.update()
            
            question_input.value = ""
            for inp in answer_inputs:
                inp.value = ""
            correct_answer_dropdown.value = None
            page.update()
        else:
            print("Lỗi khi thêm câu hỏi vào cơ sở dữ liệu!")
    
    submit_button = ft.ElevatedButton("Thêm câu hỏi", on_click=add_question_to_db)
    back_button = ft.ElevatedButton("Quay lại", on_click=lambda e: back_code(e))
    
    page.add(  # Thêm nút quay lại
        ft.Text("Tạo câu hỏi", size=20, color="white"),
        subject_dropdown,
        question_input,
        *answer_inputs,
        correct_answer_dropdown,
        submit_button,
        question_list,
        back_button
    )

ft.app(target=main)
