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

def change_user_role(email, new_role):
    """Change a user's role in Supabase database"""
    try:
        # Reset all role flags
        role_data = {
            "is_admin": False,
            "is_teacher": False,
            "is_student": False
        }
        
        # Set the new role
        if new_role == "admin":
            role_data["is_admin"] = True
        elif new_role == "teacher":
            role_data["is_teacher"] = True
        elif new_role == "student":
            role_data["is_student"] = True
        
        # Update user role
        response = supabase.table("users").update(role_data).eq("email", email).execute()
        return True
    except Exception as e:
        print(f"Error changing user role: {e}")
        return False

def get_user_role_text(user):
    """Get user role display text"""
    if user.get("is_admin", False):
        return "Quản trị viên"
    elif user.get("is_teacher", False):
        return "Giáo viên"
    elif user.get("is_student", False):
        return "Học sinh"
    else:
        return "Không xác định"

def get_user_role_value(user):
    """Get user role value"""
    if user.get("is_admin", False):
        return "admin"
    elif user.get("is_teacher", False):
        return "teacher"
    elif user.get("is_student", False):
        return "student"
    else:
        return "student"

def main(page: ft.Page):
    page.title = "Thay đổi vai trò người dùng"
    page.window_width = 500
    page.window_height = 450
    page.window_resizable = False
    page.bgcolor = "#0F1115"
    page.padding = 40
    
    users = load_users()
    
    # Create dropdown options with role information
    def create_user_dropdown_options():
        return [
            ft.dropdown.Option(
                user["email"], 
                f"{user['email']} ({get_user_role_text(user)})"
            ) 
            for user in users
        ]
    
    user_dropdown = ft.Dropdown(
        label="Chọn người dùng",
        options=create_user_dropdown_options(),
        width=300,
        bgcolor="#161920",
        color="white",
        border_color="#161920",
        focused_border_color="#3B71CA",
        label_style=ft.TextStyle(color="#6C757D")
    )
    
    # Role selection dropdown
    role_dropdown = ft.Dropdown(
        label="Chọn vai trò mới",
        width=300,
        bgcolor="#161920",
        color="white",
        border_color="#161920",
        focused_border_color="#3B71CA",
        label_style=ft.TextStyle(color="#6C757D"),
        options=[
            ft.dropdown.Option("student", "Học sinh"),
            ft.dropdown.Option("teacher", "Giáo viên"),
            ft.dropdown.Option("admin", "Quản trị viên")
        ]
    )
    
    status_text = ft.Text("", color="red", size=14)
    
    def back_code(e):
        page.window.close()
        subprocess.run([sys.executable, "user_code/administrator/administrator_main.py"])
    
    def on_user_selected(e):
        """Update role dropdown when user is selected"""
        selected_email = user_dropdown.value
        if selected_email:
            # Find the selected user and set their current role
            selected_user = next((user for user in users if user["email"] == selected_email), None)
            if selected_user:
                current_role = get_user_role_value(selected_user)
                role_dropdown.value = current_role
                page.update()
    
    # Set the on_change event for user dropdown
    user_dropdown.on_change = on_user_selected
    
    def change_role(e):
        nonlocal users
        selected_email = user_dropdown.value
        selected_role = role_dropdown.value
        
        if not selected_email:
            status_text.value = "Vui lòng chọn một người dùng!"
            status_text.color = "red"
            page.update()
            return
        
        if not selected_role:
            status_text.value = "Vui lòng chọn vai trò mới!"
            status_text.color = "red"
            page.update()
            return
        
        # Get current user role for comparison
        selected_user = next((user for user in users if user["email"] == selected_email), None)
        if selected_user:
            current_role = get_user_role_value(selected_user)
            if current_role == selected_role:
                status_text.value = "Người dùng đã có vai trò này rồi!"
                status_text.color = "orange"
                page.update()
                return
        
        # Change user role
        if change_user_role(selected_email, selected_role):
            role_text = {
                "student": "học sinh",
                "teacher": "giáo viên", 
                "admin": "quản trị viên"
            }.get(selected_role, "người dùng")
            
            status_text.value = f"Đã thay đổi vai trò của {selected_email} thành {role_text}!"
            status_text.color = "green"
            
            # Refresh the dropdown with updated user list
            users = load_users()
            user_dropdown.options = create_user_dropdown_options()
            user_dropdown.value = None
            role_dropdown.value = None
        else:
            status_text.value = "Không thể thay đổi vai trò người dùng!"
            status_text.color = "red"
        
        page.update()
    
    def refresh_users(e):
        """Refresh the user list from database"""
        nonlocal users
        users = load_users()
        user_dropdown.options = create_user_dropdown_options()
        user_dropdown.value = None
        role_dropdown.value = None
        status_text.value = "Đã làm mới danh sách người dùng"
        status_text.color = "blue"
        page.update()
    
    change_button = ft.ElevatedButton(
        "Thay đổi vai trò", 
        on_click=change_role,
        width=300,
        style=ft.ButtonStyle(
            bgcolor="#3B71CA",  # Blue color for change action
            color="white"
        )
    )
    
    refresh_button = ft.ElevatedButton(
        "Làm mới danh sách",
        on_click=refresh_users,
        width=300,
        style=ft.ButtonStyle(
            bgcolor="#17A2B8",  # Blue color for refresh
            color="white"
        )
    )
    
    back_button = ft.ElevatedButton(
        "Quay lại", 
        on_click=back_code,
        width=300,
        style=ft.ButtonStyle(
            bgcolor="#6C757D",  # Gray color for back
            color="white"
        )
    )

    # Main layout - matching the other pages structure
    main_content = ft.Column(
        [
            ft.Text("Thay đổi vai trò User", size=24, weight="bold", color="white"),
            ft.Container(height=20),
            user_dropdown,
            ft.Container(height=15),
            role_dropdown,
            ft.Container(height=15),
            change_button,
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