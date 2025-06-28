import flet as ft
import os
import sys
import subprocess
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv("./.secret/.env")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def create_user(email, username, password, user_type="student"):
    """Create new user with specified role using Supabase"""
    try:
        # Check if email already exists
        existing_email = supabase.table("users").select("*").eq("email", email).execute()
        if existing_email.data:
            print("Email đã tồn tại!")
            return False, "Email đã tồn tại!"
            
        # Check if username already exists (only if username is provided)
        if username and username.strip():
            existing_username = supabase.table("users").select("*").eq("username", username).execute()
            if existing_username.data:
                print("Username đã tồn tại!")
                return False, "Username đã tồn tại!"
        else:
            # If no username provided, use email as username
            username = email
            
        # Set user roles based on type
        is_admin = user_type == "admin"
        is_teacher = user_type == "teacher"
        is_student = user_type == "student"
            
        # Create new user
        new_user = {
            "email": email,
            "username": username,
            "password": password,
            "is_admin": is_admin,
            "is_teacher": is_teacher,
            "is_student": is_student
        }
        
        insert_res = supabase.table("users").insert(new_user).execute()
        
        # Initialize score rows for the new user (if subjects table exists and user is a student)
        if is_student:
            user_id = None
            if insert_res.data:
                user_id = insert_res.data[0].get("id")
            else:
                # Fallback: get user ID by email
                res = supabase.table("users").select("id").eq("email", email).single().execute()
                if res.data:
                    user_id = res.data.get("id")
                    
            if user_id:
                try:
                    # Initialize scores for all subjects
                    subjects_res = supabase.table("subjects").select("id").execute()
                    if subjects_res.data:
                        score_rows = [
                            {"user_id": user_id, "subject_id": subj["id"], "score": 0} 
                            for subj in subjects_res.data
                        ]
                        supabase.table("scores").upsert(score_rows).execute()
                except Exception as e:
                    print(f"Error initializing scores: {e}")
                
        return True, "Tạo user thành công!"
        
    except Exception as e:
        print(f"User creation error: {e}")
        return False, f"Lỗi tạo user: {str(e)}"

def main(page: ft.Page):
    page.title = "Đăng ký người dùng"
    page.window_width = 500
    page.window_height = 400
    page.window_resizable = False
    page.bgcolor = "#0F1115"
    page.padding = 40
    
    # UI Elements with consistent styling
    email_input = ft.TextField(
        label="Nhập email", 
        width=300,
        bgcolor="#161920",
        color="white",
        border_color="#161920",
        focused_border_color="#3B71CA",
        label_style=ft.TextStyle(color="#6C757D")
    )
    
    username_input = ft.TextField(
        label="Nhập username (tùy chọn)", 
        width=300,
        bgcolor="#161920",
        color="white",
        border_color="#161920",
        focused_border_color="#3B71CA",
        label_style=ft.TextStyle(color="#6C757D"),
        hint_text="Để trống sẽ dùng email làm username"
    )
    
    password_input = ft.TextField(
        label="Nhập mật khẩu", 
        width=300, 
        password=True,
        bgcolor="#161920",
        color="white",
        border_color="#161920",
        focused_border_color="#3B71CA",
        label_style=ft.TextStyle(color="#6C757D")
    )
    
    # User role selection dropdown
    role_dropdown = ft.Dropdown(
        label="Chọn vai trò",
        width=300,
        bgcolor="#161920",
        color="white",
        border_color="#161920",
        focused_border_color="#3B71CA",
        label_style=ft.TextStyle(color="#6C757D"),
        value="student",
        options=[
            ft.dropdown.Option("student", "Học sinh"),
            ft.dropdown.Option("teacher", "Giáo viên"),
            ft.dropdown.Option("admin", "Quản trị viên")
        ]
    )
    
    status_text = ft.Text("", color="red", size=14)

    def create_new_user(e):
        email = email_input.value.strip()
        username = username_input.value.strip()
        password = password_input.value.strip()
        user_role = role_dropdown.value
        
        if not email or not password:
            status_text.value = "Email và mật khẩu không được để trống!"
            status_text.color = "red"
            page.update()
            return
            
        success, message = create_user(email, username, password, user_role)
        if success:
            role_text = {
                "student": "học sinh",
                "teacher": "giáo viên", 
                "admin": "quản trị viên"
            }.get(user_role, "người dùng")
            
            used_username = username if username else email
            status_text.value = f"Tạo tài khoản {role_text} thành công! Username: {used_username}"
            status_text.color = "green"
            email_input.value = ""
            username_input.value = ""
            password_input.value = ""
            role_dropdown.value = "student"
        else:
            status_text.value = message
            status_text.color = "red"
            
        page.update()

    def back_code(e):
        page.window.close()
        subprocess.run([sys.executable, "administrator/administrator_main.py"])

    create_button = ft.ElevatedButton(
        "Tạo User", 
        on_click=create_new_user,
        width=300,
        style=ft.ButtonStyle(
            bgcolor="#3B71CA",
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

    # Main layout
    main_content = ft.Column(
        [
            ft.Text("Tạo User", size=24, weight="bold", color="white"),
            ft.Container(height=20),
            email_input,
            ft.Container(height=15),
            username_input,
            ft.Container(height=15),
            password_input,
            ft.Container(height=15),
            role_dropdown,
            ft.Container(height=20),
            create_button,
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