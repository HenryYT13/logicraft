import flet as ft
import json
import os
import sys
import subprocess

def save_user(email, password):
    file_path = "json/login_info.json"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    user_data = {"email": email, "password": password, "admin": False}
    
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
                if not isinstance(data, dict) or "users" not in data:
                    data = {"users": []}
            except json.JSONDecodeError:
                data = {"users": []}
    else:
        data = {"users": []}
    
    if not any(user["email"] == email for user in data["users"]):
        data["users"].append(user_data)
    else:
        print("User đã tồn tại!")
    
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
   
def main(page: ft.Page):
    page.title = "Đăng ký người dùng"
    page.padding = 40
    
    email_input = ft.TextField(label="Nhập email", width=300)
    password_input = ft.TextField(label="Nhập mật khẩu", width=300, password=True)
    status_text = ft.Text("", color="red")
    
    def register_user(e):
        email = email_input.value.strip()
        password = password_input.value.strip()
        
        if not email or not password:
            status_text.value = "Email và mật khẩu không được để trống!"
            page.update()
            return
        
        save_user(email, password)
        status_text.value = "Đăng ký thành công!"
        status_text.color = "green"
        email_input.value = ""
        password_input.value = ""
        page.update()
    
    def back_code(e):
        page.window_close()
        subprocess.run([sys.executable, "administrator/administrator_main.py"])
    
    register_button = ft.ElevatedButton("Đăng ký", on_click=register_user)
    back_button = ft.ElevatedButton("Quay lại", on_click=back_code)

    page.add(ft.Text("Tạo User", size=20, color="white"), email_input, password_input, register_button, status_text, back_button)

ft.app(target=main)
