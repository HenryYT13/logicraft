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

users = load_users()

def authenticate(email, password):
    for user in users:
        if user.get("email") == email and user.get("password") == password:
            return user.get("admin", False)  # Default to False if 'admin' is not present
    return None

def register_user(email, password, admin=False):
    if any(user.get("email") == email for user in users):
        return False  # Email already exists
    users.append({"email": email, "password": password, "admin": admin})
    save_users(users)
    return True

def toggle_password_visibility(e):
    password_field.password = not password_field.password
    password_field.update()
    show_password_button.text = "Ẩn mật khẩu" if not password_field.password else "Hiển thị mật khẩu"
    show_password_button.update()

def login(e, page):
    email = email_field.value.strip()
    password = password_field.value.strip()
    
    admin_status = authenticate(email, password)
    if admin_status is not None:
        if admin_status == True:
            subprocess.Popen([sys.executable, "administrator/administrator_main.py"])
        else:
            subprocess.Popen([sys.executable, "other_code/main_windows.py"])
        page.window.close()
    else:
        login_status.value = "Tài khoản hoặc mật khẩu không chính xác!"
        login_status.update()

def register(e, page):
    email = email_field.value.strip()
    password = password_field.value.strip()
    
    if register_user(email, password):
        login_status.value = "Tài khoản đã được tạo thành công! Bạn có thể đăng nhập bây giờ."
        login_status.color = "green"
    else:
        login_status.value = "Email / Username đã tồn tại!"
        login_status.color = "red"
    login_status.update()

# UI Elements with dark theme styling
email_field = ft.TextField(
    label="E-mail / Username",
    width=300,
    bgcolor="#161920",
    color="white",
    border_color="#161920",
    focused_border_color="#3B71CA",
    label_style=ft.TextStyle(color="#6C757D")
)

password_field = ft.TextField(
    label="Mật khẩu",
    password=True,
    width=300,
    bgcolor="#161920",
    color="white",
    border_color="#161920",
    focused_border_color="#3B71CA",
    label_style=ft.TextStyle(color="#6C757D")
)

show_password_button = ft.TextButton(
    "Hiển thị mật khẩu",
    on_click=toggle_password_visibility,
    style=ft.ButtonStyle(color="#3B71CA")
)

login_status = ft.Text(color="red", size=14)

def main(page: ft.Page):
    page.title = "Logicraft Đăng nhập"
    page.window_width = 500
    page.window_height = 600
    page.window_resizable = False
    page.bgcolor = "#0F1115"
    page.padding = 0
    
    login_button = ft.ElevatedButton(
        "Đăng nhập",
        width=300,
        on_click=lambda e: login(e, page),
        style=ft.ButtonStyle(
            bgcolor="#3B71CA",
            color="white"
        )
    )
    
    register_button = ft.TextButton(
        "Đăng ký tài khoản (nhập vào ô trên)",
        on_click=lambda e: register(e, page),
        style=ft.ButtonStyle(color="#3B71CA")
    )

    def feedback(e):
        page.window.close()
        subprocess.run([sys.executable, "other_code/feedback.py"])

    feedback_button = ft.ElevatedButton("Gửi feedback", on_click=lambda e: feedback(e))
    
    login_view = ft.Column(
        [
            ft.Image(src="./assest/icon.png", height=100),
            ft.Text(
                "Đăng nhập vào Logicraft",
                size=24,
                weight="bold",
                color="white"
            ),
            ft.Container(height=40),
            email_field,
            ft.Container(height=15),
            password_field,
            show_password_button,
            ft.Container(height=5),
            login_button,
            register_button,
            login_status,
            feedback_button
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=5
    )

    centered_container = ft.Container(
        content=login_view,
        alignment=ft.alignment.center,
        expand=True
    )

    page.add(centered_container)

ft.app(target=main)
