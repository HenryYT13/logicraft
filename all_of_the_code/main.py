import flet as ft
import subprocess
import sys
import os
import tempfile
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
            is_admin BOOLEAN NOT NULL DEFAULT false,
            is_teacher BOOLEAN NOT NULL DEFAULT false,
            is_student BOOLEAN NOT NULL DEFAULT true
        );
        """
        if hasattr(supabase, "raw"):
            try:
                supabase.raw(create_table_sql).execute()
            except Exception as err:
                print(f"Table creation failed via raw(): {err}")
        else:
            print("supabase.raw() not available in this client version – ensure tables are created manually.")
        # Create scores table if not exists
        create_scores_sql = """
        CREATE TABLE IF NOT EXISTS scores (
            id SERIAL PRIMARY KEY,
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            subject_id INT,
            score INT DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (user_id, subject_id)
        );
        """
        if hasattr(supabase, "raw"):
            try:
                supabase.raw(create_scores_sql).execute()
            except Exception as err:
                print(f"Scores table creation failed via raw(): {err}")
        else:
            print("supabase.raw() not available – skipping scores table creation.")
        
        # Create sample users
        sample_users = [
            {
                "email": "administrator@logicraft.vn",
                "username": "administrator",
                "password": "administrator",
                "is_admin": True,
                "is_teacher": False,
                "is_student": False
            },
            {
                "email": "example@elogicraft.vn",
                "username": "example",
                "password": "1234",
                "is_admin": False,
                "is_teacher": False,
                "is_student": True
            },
            {
                "email": "teacher@logicraft.vn",
                "username": "teacher",
                "password": "teacher",
                "is_admin": False,
                "is_teacher": True,
                "is_student": False
            },
            {
                "email": "student@logicraft.vn",
                "username": "student",
                "password": "student_password",
                "admin": False,
                "teacher": False,
                "student": True
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
        insert_res = supabase.table("users").insert(new_user).execute()
        # Initialize score rows for the new user
        user_id = None
        if insert_res.data:
            user_id = insert_res.data[0].get("id")
        else:
            res = supabase.table("users").select("id").eq("email", email).single().execute()
            if res.data:
                user_id = res.data.get("id")
        if user_id:
            try:
                subjects_res = supabase.table("subjects").select("id").execute()
                if subjects_res.data:
                    score_rows = [{"user_id": user_id, "subject_id": subj["id"], "score": 0} for subj in subjects_res.data]
                    supabase.table("scores").upsert(score_rows).execute()
            except Exception as e:
                print(f"Error initializing scores: {e}")
        return True
    except Exception as e:
        print(f"Registration error: {e}")
        return False

def save_current_user_id(user_id: str):
    """Write the current user's UUID to a temp file so that other processes can read it."""
    try:
        temp_path = os.path.join(tempfile.gettempdir(), "logicraft_current_user_id")
        with open(temp_path, "w", encoding="utf-8") as f:

            f.write(user_id)
    except Exception as e:
        print(f"Error saving current user ID: {e}")


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
        # Save current user ID for downstream processes
        env = os.environ.copy()
        env["CURRENT_USER_ID"] = str(user.get("id"))
        save_current_user_id(env["CURRENT_USER_ID"])

        if user.get("is_admin"):
            subprocess.Popen([sys.executable, os.path.join("user_code", "administrator", "administrator_main.py")], env=env)
        elif user.get("is_teacher"):
            subprocess.Popen([sys.executable, os.path.join("user_code", "teacher", "teacher_main.py")], env=env)
        else:
            subprocess.Popen([sys.executable, os.path.join("user_code", "student", "student_main.py")], env=env)
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