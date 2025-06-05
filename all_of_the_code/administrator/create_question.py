import flet as ft
import json
import os
import subprocess
import sys

def save_question_to_file(subject, question, answers, correct_index):
    print(f"Saving - Subject: {subject}, Question: {question}, Answers: {answers}, Correct Index: {correct_index}")  # Debugging

    if not question.strip() or not all(answers) or correct_index is None or correct_index < 0 or correct_index >= len(answers):
        print("Invalid question data! Skipping save.")
        return

    file_path = "json/questions.json"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    question_data = {
        "question": question,
        "options": answers,
        "correct_answer": correct_index
    }

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}

    if subject not in data:
        data[subject] = {"questions": []}

    data[subject]["questions"].append(question_data)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print(f"Added question: {question_data}")  # Final Debugging

def main(page: ft.Page):
    page.title = "Administrator Screen"
    page.padding = 40  # Adding padding around the content
    
    subjects = ["Toán", "Khoa học", "Lịch sử", "Địa lý", "Tiếng Anh", "Tiếng Việt / Ngữ Văn"]
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

    def add_question(e):
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
        
        save_question_to_file(subject_dropdown.value, question_input.value, answers, correct_index)
        
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
    
    submit_button = ft.ElevatedButton("Thêm câu hỏi", on_click=add_question)
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
