import flet as ft
import json
import os
import subprocess
import sys

QUESTION_FILE = "json/questions.json"

def load_questions():
    try:
        with open(QUESTION_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_questions(data):
    try:
        with open(QUESTION_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving questions: {e}")

def delete_question(subject, question_text):
    data = load_questions()
    if subject in data and "questions" in data[subject]:
        data[subject]["questions"] = [q for q in data[subject]["questions"] if q["question"] != question_text]
        save_questions(data)
        return True
    return False

def main(page: ft.Page):
    page.title = "Xóa câu hỏi"
    page.padding = 20

    data = load_questions()
    subjects = list(data.keys())

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
        subject = subject_dropdown.value
        question_dropdown.options = []
        if subject and subject in data:
            questions = data[subject]["questions"]
            question_dropdown.options = [ft.dropdown.Option(q["question"]) for q in questions]
        question_dropdown.update()

    def back_code(e):
        page.window.close()
        subprocess.run([sys.executable, "administrator/administrator_main.py"])

    def delete_selected_question(e):
        subject = subject_dropdown.value
        question_text = question_dropdown.value
        
        if subject and question_text and delete_question(subject, question_text):
            status_text.value = f"Câu hỏi đã được xóa thành công!"
            status_text.color = "green"
            update_questions(None)
        else:
            status_text.value = "Xóa thất bại!"
            status_text.color = "red"
        status_text.update()

    subject_dropdown.on_change = update_questions
    delete_button = ft.ElevatedButton("Xóa Câu Hỏi", on_click=delete_selected_question)
    back_button = ft.ElevatedButton("Quay lại", on_click=lambda e: back_code(e))

    page.add(ft.Text("Xoá câu hỏi", size=20, color="white"), subject_dropdown, question_dropdown, delete_button, status_text, back_button)

ft.app(target=main)
