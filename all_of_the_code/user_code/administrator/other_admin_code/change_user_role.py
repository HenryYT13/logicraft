import flet as ft
import json
import subprocess
import sys

LOGIN_FILE = "json/login_info.json"

def load_users():
    try:
        with open(LOGIN_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("users", [])
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Error loading users: {e}")
        return []

def save_users(users):
    try:
        with open(LOGIN_FILE, "w", encoding="utf-8") as f:
            json.dump({"users": users}, f, indent=4)
    except Exception as e:
        print(f"Error saving users: {e}")

def make_admin(email):
    users = load_users()
    for user in users:
        if user.get("email") == email:
            user["admin"] = True
            save_users(users)
            return True
    return False

def main(page: ft.Page):
    page.title = "Làm user thành Admin"
    page.window_width = 400
    page.window_height = 300
    page.window_resizable = False
    page.bgcolor = "#0F1115"

    users = load_users()
    non_admin_users = [user["email"] for user in users if not user.get("admin", False)]
    
    user_dropdown = ft.Dropdown(
        label="Chọn người dùng",
        options=[ft.dropdown.Option(email) for email in non_admin_users],
        width=300
    )
    
    status_text = ft.Text("", color="white")
    
    def back_code(e):
        page.window.close()
        subprocess.run([sys.executable, "administrator/administrator_main.py"])

    def promote_user(e):
        if user_dropdown.value:
            success = make_admin(user_dropdown.value)
            if success:
                status_text.value = f"{user_dropdown.value} bây giờ là Admin!"
                status_text.color = "green"
                user_dropdown.options = [ft.dropdown.Option(email) for email in load_users() if not email.get("admin", False)]
                user_dropdown.update()
            else:
                status_text.value = "Không thể cho user làm Admin."
                status_text.color = "red"
            status_text.update()
    
    promote_button = ft.ElevatedButton("Làm Admin", on_click=promote_user, width=300)
    back_button = ft.ElevatedButton("Quay lại", on_click=lambda e: back_code(e))

    page.add(
        ft.Column(
            [
                ft.Text("Cho một user làm Admin", size=20, color="white"),
                user_dropdown,
                promote_button,
                status_text
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        )
    )

ft.app(target=main)
