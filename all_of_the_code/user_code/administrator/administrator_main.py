import flet as ft
import subprocess
import sys

def open_script(script_name):
    subprocess.Popen([sys.executable, script_name])

def main(page: ft.Page):
    page.title = "Admin Menu"
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
        subprocess.run([sys.executable, "administrator/other_admin_code/create_question.py"])
        
    def delete_question(e):
        page.window.close()
        subprocess.run([sys.executable, "administrator/other_admin_code/delete_question.py"])    
        
    def promote_user(e):
        page.window.close()
        subprocess.run([sys.executable, "administrator/other_admin_code/promote.py"])
        
    def delete_user(e):
        page.window.close()
        subprocess.run([sys.executable, "administrator/other_admin_code/delete_user.py"])
        
    def create_user(e):
        page.window.close()
        subprocess.run([sys.executable, "administrator/other_admin_code/create_user.py"])
        
    def feedback(e):
        page.window.close()
        subprocess.run([sys.executable, "other_code/feedback.py"])

    # Create buttons with consistent styling
    create_question_btn = ft.ElevatedButton(
        "Tạo câu hỏi", 
        on_click=create_question,
        width=300,
        style=ft.ButtonStyle(
            bgcolor="#3B71CA",
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
    
    promote_admin_btn = ft.ElevatedButton(
        "Làm Admin cho User", 
        on_click=promote_user,
        width=300,
        style=ft.ButtonStyle(
            bgcolor="#28A745",
            color="white"
        )
    )
    
    demote_admin_btn = ft.ElevatedButton(
        "Xóa Admin cho User", 
        on_click=promote_user,
        width=300,
        style=ft.ButtonStyle(
            bgcolor="#FD7E14",
            color="white"
        )
    )
    
    delete_user_btn = ft.ElevatedButton(
        "Xóa User", 
        on_click=delete_user,
        width=300,
        style=ft.ButtonStyle(
            bgcolor="#DC3545",
            color="white"
        )
    )
    
    create_user_btn = ft.ElevatedButton(
        "Tạo User", 
        on_click=create_user,
        width=300,
        style=ft.ButtonStyle(
            bgcolor="#3B71CA",
            color="white"
        )
    )
    
    feedback_btn = ft.ElevatedButton(
        "Feedback", 
        on_click=feedback,
        width=300,
        style=ft.ButtonStyle(
            bgcolor="#17A2B8",
            color="white"
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

    # Main layout matching the add/delete user structure
    main_content = ft.Column(
        [
            ft.Image(src="./assest/icon.png", height=100),
            ft.Container(height=10),
            ft.Text("Menu dành cho Admin", size=24, weight="bold", color="white"),
            ft.Container(height=20),
            create_question_btn,
            ft.Container(height=10),
            delete_question_btn,
            ft.Container(height=10),
            promote_admin_btn,
            ft.Container(height=10),
            demote_admin_btn,
            ft.Container(height=10),
            delete_user_btn,
            ft.Container(height=10),
            create_user_btn,
            ft.Container(height=10),
            feedback_btn,
            ft.Container(height=10),
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