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

def initialize_database():
    """Create users table if it doesn't exist and add sample users"""
    try:
        # Create users table if not exists
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            admin BOOLEAN NOT NULL DEFAULT false,
            teacher BOOLEAN NOT NULL DEFAULT false,
            student BOOLEAN NOT NULL DEFAULT true
        );
        """
        supabase.raw(create_table_sql).execute()
        
        # Create sample users
        sample_users = [
            {
                "email": "administrator@example.com",
                "username": "administrator",
                "password": "administrator",
                "admin": True,
                "teacher": False,
                "student": False
            },
            {
                "email": "example@example.com",
                "username": "example",
                "password": "1234",
                "admin": False,
                "teacher": False,
                "student": True
            },
            {
                "email": "teacher@example.com",
                "username": "teacher",
                "password": "teacher",
                "admin": False,
                "teacher": True,
                "student": False
            }
        ]
        
        for user in sample_users:
            # Upsert users (insert if not exists)
            supabase.table("users").upsert(user).execute()
            
    except Exception as e:
        print(f"Database initialization error: {e}")

# Initialize database on startup
initialize_database()

def authenticate(identifier, password):
    """Authenticate user using email or username"""
    try:
        # Query for email match
        email_res = supabase.table("users").select("*").eq("email", identifier).eq("password", password).execute()
        if email_res.data:
            return email_res.data[0]
        
        # Query for username match
        username_res = supabase.table("users").select("*").eq("username", identifier).eq("password", password).execute()
        if username_res.data:
            return username_res.data[0]
            
        return None
    except Exception as e:
        print(f"Authentication error: {e}")
        return None

def register_user(email, password):
    """Register new user with student role by default"""
    try:
        # Check if email or username exists
        existing = supabase.table("users").select("*").or_(f"email.eq.{email},username.eq.{email}").execute()
        if existing.data:
            return False
            
        new_user = {
            "email": email,
            "username": email,  # Use email as username
            "password": password,
            "admin": False,
            "teacher": False,
            "student": True
        }
        supabase.table("users").insert(new_user).execute()
        return True
    except Exception as e:
        print(f"Registration error: {e}")
        return False

def toggle_password_visibility(e):
    password_field.password = not password_field.password
    password_field.update()
    show_password_button.text = "Ẩn mật khẩu" if not password_field.password else "Hiển thị mật khẩu"
    show_password_button.update()

def login(e, page):
    identifier = email_field.value.strip()
    password = password_field.value.strip()
    
    user = authenticate(identifier, password)
    if user:
        if user.get("admin"):
            subprocess.Popen([sys.executable, "administrator/administrator_main.py"])
        elif user.get("teacher"):
            subprocess.Popen([sys.executable, "teacher/teacher_main.py"])
        else:
            subprocess.Popen([sys.executable, "student/student_main.py"])
        page.window.close()
    else:
        login_status.value = "Tài khoản hoặc mật khẩu không chính xác!"
        login_status.update()

def register(e, page):
    email = email_field.value.strip()
    password = password_field.value.strip()
    
    if register_user(email, password):
        login_status.value = "Tài khoản đã được tạo thành công! Bạn có thể đăng nhập ngay bây giờ."
        login_status.color = "green"
    else:
        login_status.value = "Email / Username đã tồn tại!"
        login_status.color = "red"
    login_status.update()

# UI Elements
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
        "Đăng ký tài khoản (nhập vào trên)",
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