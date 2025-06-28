import flet as ft
import subprocess
import sys

def open_script(script_name):
    subprocess.Popen([sys.executable, script_name])

def main(page: ft.Page):
    page.title = "Teacher Menu"
    page.window_width = 500
    page.window_height = 600
    page.window_resizable = False
    page.bgcolor = "#0F1115"
    page.padding = 40
    
    def logout(e):
        page.window.close()
        subprocess.run([sys.executable, "main.py"])
    
    def create_question(e):
        page.window.close()
        subprocess.run([sys.executable, "user_code/teacher/other_teacher_code/create_question.py"])
    
    def delete_question(e):
        page.window.close()
        subprocess.run([sys.executable, "user_code/teacher/other_teacher_code/delete_question.py"])    
    
    def feedback(e):
        page.window.close()
        subprocess.run([sys.executable, "other_code/feedback.py"])
    
    def student_score(e):
        page.window.close()
        subprocess.run([sys.executable, "./user_code/teacher/other_teacher_code/student_score.py"])

    # Create buttons with consistent styling
    create_question_btn = ft.ElevatedButton(
        "Tạo câu hỏi", 
        on_click=create_question,
        width=300,
        style=ft.ButtonStyle(
            bgcolor="#28A745",
            color="white"
        )
    )
    
    delete_question_btn = ft.ElevatedButton(
        "Xóa câu hỏi", 
        on_click=delete_question,
        width=300,
        style=ft.ButtonStyle(
            bgcolor="#DC3545",
            color="white"
        )
    )
    
    student_score_btn = ft.ElevatedButton(
        "Xem điểm học sinh", 
        on_click=student_score,
        width=300,
        style=ft.ButtonStyle(
            bgcolor="#17A2B8",
            color="white"
        )
    )
    
    feedback_btn = ft.ElevatedButton(
        "Gửi Feedback", 
        on_click=feedback,
        width=300,
        style=ft.ButtonStyle(
            bgcolor="#FFC107",
            color="black"
        )
    )
    
    logout_btn = ft.ElevatedButton(
        "Đăng xuất", 
        on_click=logout,
        width=300,
        style=ft.ButtonStyle(
            bgcolor="#6C757D",
            color="white"
        )
    )

    # Main layout matching the admin menu structure
    main_content = ft.Column(
        [
            ft.Image(src="./assest/icon.png", height=100),
            ft.Container(height=10),
            ft.Text("Menu dành cho Giáo viên", size=24, weight="bold", color="white"),
            ft.Container(height=20),
            create_question_btn,
            ft.Container(height=10),
            delete_question_btn,
            ft.Container(height=10),
            student_score_btn,
            ft.Container(height=10),
            feedback_btn,
            ft.Container(height=20),
            logout_btn
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

ft.app(target=main)