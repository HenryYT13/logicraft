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
    page.padding = 20

    title = ft.Text("Menu dành cho Admin", size=24, weight="bold", color="white")
    
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

    buttons = ft.Column(
        [
            ft.ElevatedButton("Tạo câu hỏi", on_click=lambda e: create_question(e)),
            ft.ElevatedButton("Xóa câu hỏi", on_click=lambda e: delete_question(e)),
            ft.ElevatedButton("Làm Admin cho User", on_click=lambda e: promote_user(e)),
            ft.ElevatedButton("Xoá Admin cho User", on_click=lambda e: promote_user(e)),
            ft.ElevatedButton("Xóa User", on_click=lambda e: delete_user(e)),
            ft.ElevatedButton("Tạo User", on_click=lambda e: create_user(e)),
            ft.ElevatedButton("Feedback", on_click=lambda e: feedback(e)),
            ft.ElevatedButton("Đăng xuất", on_click=lambda e: logout(e)),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=15
    )

    container = ft.Container(
        content=ft.Column([
            ft.Image(src="./assest/icon.png", height=100),
            title,
            ft.Container(height=20),
            buttons
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        alignment=ft.alignment.center,
        expand=True
    )

    page.add(container)

ft.app(target=main)
