import flet as ft
import json
import os
import subprocess
import sys

def load_users():
    file_path = "json/login_info.json"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
                return data.get("users", [])
            except json.JSONDecodeError:
                return []
    return []

def save_users(users):
    file_path = "json/login_info.json"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump({"users": users}, file, indent=4, ensure_ascii=False)

def main(page: ft.Page):
    page.title = "Xóa người dùng"
    page.padding = 40
    
    users = load_users()
    user_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option(user["email"]) for user in users],
        label="Chọn người dùng để xóa",
        width=300,
    )
    status_text = ft.Text("", color="red")
    
    def back_code(e):
        page.window.close()
        subprocess.run([sys.executable, "administrator/administrator_main.py"])

    def delete_user(e):
        selected_email = user_dropdown.value
        if not selected_email:
            status_text.value = "Vui lòng chọn một người dùng!"
            page.update()
            return
        
        updated_users = [user for user in users if user["email"] != selected_email]
        save_users(updated_users)
        status_text.value = f"Đã xóa người dùng: {selected_email}"
        status_text.color = "green"
        
        user_dropdown.options = [ft.dropdown.Option(user["email"]) for user in updated_users]
        user_dropdown.value = None
        page.update()
    
    delete_button = ft.ElevatedButton("Xóa người dùng", on_click=delete_user)
    back_button = ft.ElevatedButton("Quay lại", on_click=back_code)

    page.add(ft.Text("Xoá User", size=20, color="white"), user_dropdown, delete_button, status_text, back_button)

ft.app(target=main)
