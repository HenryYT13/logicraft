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
                "is_admin": False,
                "is_teacher": False,
                "is_student": True
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
            "is_admin": False,
            "is_teacher": False,
            "is_student": True
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

# Create styled button function to match quiz app
def create_button(text, on_click, width=400, height=60, bgcolor="#3B71CA", color="white"):
    return ft.ElevatedButton(
        text,
        on_click=on_click,
        width=width,
        height=height,
        style=ft.ButtonStyle(
            bgcolor=bgcolor,
            color=color,
            text_style=ft.TextStyle(weight="bold")
        )
    )

def main(page: ft.Page):
    page.title = "Logicraft Đăng nhập"
    page.window_width = 600
    page.window_height = 700
    page.window_resizable = False
    page.bgcolor = "#0F1115"  # Match quiz app background
    page.padding = 0
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.scroll = "adaptive"

    # UI Elements with matching styling
    email_field = ft.TextField(
        label="E-mail / Username",
        width=400,
        height=60,
        bgcolor="#161920",
        color="white",
        border_color="#161920",
        focused_border_color="#3B71CA",
        label_style=ft.TextStyle(color="#6C757D"),
        text_style=ft.TextStyle(size=16)
    )

    password_field = ft.TextField(
        label="Mật khẩu",
        password=True,
        width=400,
        height=60,
        bgcolor="#161920",
        color="white",
        border_color="#161920",
        focused_border_color="#3B71CA",
        label_style=ft.TextStyle(color="#6C757D"),
        text_style=ft.TextStyle(size=16)
    )

    def toggle_password_visibility(e):
        password_field.password = not password_field.password
        password_field.update()
        show_password_button.text = "Ẩn mật khẩu" if not password_field.password else "Hiển thị mật khẩu"
        show_password_button.update()

    show_password_button = ft.TextButton(
        "Hiển thị mật khẩu",
        on_click=toggle_password_visibility,
        style=ft.ButtonStyle(
            color="#3B71CA",
            text_style=ft.TextStyle(size=14)
        )
    )

    login_status = ft.Text(
        "",
        color="#DC3545",
        size=16,
        weight="bold",
        text_align="center"
    )

    def login(e):
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
            login_status.color = "#DC3545"
            login_status.update()

    def register(e):
        email = email_field.value.strip()
        password = password_field.value.strip()
        
        if register_user(email, password):
            login_status.value = "Tài khoản đã được tạo thành công! Bạn có thể đăng nhập ngay bây giờ."
            login_status.color = "#28A745"
        else:
            login_status.value = "Email / Username đã tồn tại!"
            login_status.color = "#DC3545"
        login_status.update()

    def feedback(e):
        page.window.close()
        subprocess.run([sys.executable, "other_code/feedback.py"])

    # Main login content with matching layout
    login_content = ft.Column(
        [
            # Logo section
            ft.Container(
                content=ft.Image(src="./assest/icon.png", height=120),
                alignment=ft.alignment.center
            ),
            ft.Container(height=20),
            
            # Title
            ft.Text(
                "ĐĂNG NHẬP VÀO LOGICRAFT",
                size=32,
                weight="bold",
                color="white",
                text_align="center"
            ),
            ft.Container(height=30),
            
            # Input fields container
            ft.Container(
                content=ft.Column([
                    email_field,
                    ft.Container(height=15),
                    password_field,
                    show_password_button,
                ], 
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.all(20),
                bgcolor="#161920",
                border_radius=15,
                width=500
            ),
            
            ft.Container(height=20),
            
            # Status message
            login_status,
            ft.Container(height=10),
            
            # Action buttons
            create_button(
                "ĐĂNG NHẬP",
                login,
                width=400,
                height=60,
                bgcolor="#3B71CA"
            ),
            
            ft.Container(height=10),
            
            create_button(
                "ĐĂNG KÝ TÀI KHOẢN",
                register,
                width=400,
                height=60,
                bgcolor="#28A745"
            ),
            
            ft.Container(height=20),
            
            # Feedback button
            create_button(
                "GỬI FEEDBACK",
                feedback,
                width=300,
                height=50,
                bgcolor="#17A2B8"
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10
    )

    # Scrollable container to match quiz app
    login_view = ft.ListView(
        controls=[login_content],
        expand=True,
        spacing=10,
        padding=ft.padding.all(20)
    )

    page.add(login_view)

ft.app(target=main)