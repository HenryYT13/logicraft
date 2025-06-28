import flet as ft
import subprocess
import sys
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv("./.secret/.env")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def load_users():
    """Load all users from Supabase database"""
    try:
        response = supabase.table("users").select("*").execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error loading users: {e}")
        return []

def delete_user_from_db(user_email):
    """Delete user from Supabase database"""
    try:
        # Delete the user with the specified email
        response = supabase.table("users").delete().eq("email", user_email).execute()
        return True
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False

def main(page: ft.Page):
    page.title = "Xóa người dùng"
    page.window_width = 500
    page.window_height = 400
    page.window_resizable = False
    page.bgcolor = "#0F1115"
    page.padding = 40
    
    users = load_users()
    
    # UI Elements with consistent styling matching add user
    user_dropdown = ft.Dropdown(
        label="Chọn người dùng để xóa",
        width=300,
        bgcolor="#161920",
        color="white",
        border_color="#161920",
        focused_border_color="#3B71CA",
        label_style=ft.TextStyle(color="#6C757D"),
        options=[ft.dropdown.Option(user["email"]) for user in users]
    )
    
    status_text = ft.Text("", color="red", size=14)
    
    def back_code(e):
        page.window.close()
        subprocess.run([sys.executable, "administrator/administrator_main.py"])

    def delete_user(e):
        selected_email = user_dropdown.value
        if not selected_email:
            status_text.value = "Vui lòng chọn một người dùng!"
            status_text.color = "red"
            page.update()
            return
        
        # Check if user is admin to prevent deletion
        selected_user = next((user for user in users if user["email"] == selected_email), None)
        if selected_user and selected_user.get("is_admin", False):
            status_text.value = "Không thể xóa tài khoản administrator!"
            status_text.color = "red"
            page.update()
            return
        
        # Delete user from database
        if delete_user_from_db(selected_email):
            status_text.value = f"Đã xóa người dùng: {selected_email}"
            status_text.color = "green"
            
            # Refresh the dropdown with updated user list
            updated_users = load_users()
            user_dropdown.options = [ft.dropdown.Option(user["email"]) for user in updated_users]
            user_dropdown.value = None
        else:
            status_text.value = "Lỗi khi xóa người dùng!"
            status_text.color = "red"
        
        page.update()
    
    def refresh_users(e):
        """Refresh the user list from database"""
        nonlocal users
        users = load_users()
        user_dropdown.options = [ft.dropdown.Option(user["email"]) for user in users]
        user_dropdown.value = None
        status_text.value = "Đã làm mới danh sách người dùng"
        status_text.color = "blue"
        page.update()
    
    delete_button = ft.ElevatedButton(
        "Xóa người dùng", 
        on_click=delete_user,
        width=300,
        style=ft.ButtonStyle(
            bgcolor="#DC3545",
            color="white"
        )
    )
    
    refresh_button = ft.ElevatedButton(
        "Làm mới danh sách",
        on_click=refresh_users,
        width=300,
        style=ft.ButtonStyle(
            bgcolor="#17A2B8",
            color="white"
        )
    )
    
    back_button = ft.ElevatedButton(
        "Quay lại", 
        on_click=back_code,
        width=300,
        style=ft.ButtonStyle(
            bgcolor="#6C757D",
            color="white"
        )
    )

    # Main layout matching add user structure
    main_content = ft.Column(
        [
            ft.Text("Xóa User", size=24, weight="bold", color="white"),
            ft.Container(height=20),
            user_dropdown,
            ft.Container(height=20),
            delete_button,
            ft.Container(height=10),
            refresh_button,
            ft.Container(height=10),
            status_text,
            ft.Container(height=20),
            back_button
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