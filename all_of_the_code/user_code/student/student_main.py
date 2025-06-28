import asyncio
import threading
import time
import pygame
import json
import subprocess
import sys
import os
import tempfile
from supabase import create_client, Client
from dotenv import load_dotenv
import flet as ft

# Load environment variables
load_dotenv("./.secret/.env")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

def read_current_user_id():
    """Read the current user's UUID from the temp file created by login process."""
    try:
        temp_path = os.path.join(tempfile.gettempdir(), "logicraft_current_user_id")
        if os.path.exists(temp_path):
            with open(temp_path, "r", encoding="utf-8") as f:
                user_id = f.read().strip()
                return user_id if user_id else None
        return None
    except Exception as e:
        print(f"Error reading current user ID: {e}")
        return None

async def main(page: ft.Page):
    page.title = "Logicraft"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.scroll = "adaptive"
    page.bgcolor = "#0F1115"  # Dark background
    page.data = {}  # Initialize page.data dictionary
    
    # Initialize sound variables
    page.data["correct_sound"] = "audio/right.mp3"
    page.data["wrong_sound"] = "audio/wrong.mp3"
    page.data["background_music"] = "audio/background.mp3"
    page.data["is_playing"] = False
    page.data["music_thread"] = None
    page.data["sound_effects"] = {}
    page.data["mixer_initialized"] = False
    page.data["is_muted"] = False  # Initialize mute state
    
    # Get user ID from temp file (set during login)
    page.data["user_id"] = read_current_user_id()
    print(f"Current user ID from temp file: {page.data['user_id']}")
    
    # Fallback to environment variable if temp file doesn't exist
    if not page.data["user_id"]:
        page.data["user_id"] = os.getenv("CURRENT_USER_ID")
        print(f"Fallback to environment variable: {page.data['user_id']}")

    def open_info(e):
        page.window.close()
        subprocess.run([sys.executable, "./other_code/credit.py"])
    
    def initialize_mixer():
        if not page.data["mixer_initialized"]:
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
                page.data["mixer_initialized"] = True
            except Exception as e:
                print(f"Error initializing mixer: {e}")

    def toggle_music(e):
        page.data["is_muted"] = not page.data["is_muted"]
        if page.data["is_muted"]:
            stop_background_music()
            e.control.text = "Bật âm thanh nền"
        else:
            start_background_music()
            e.control.text = "Tắt âm thanh nền"
        page.update()

    def load_sound_effects():
        try:
            initialize_mixer()
            # Pre-load sounds for mobile
            correct_sound = pygame.mixer.Sound(page.data["correct_sound"])
            wrong_sound = pygame.mixer.Sound(page.data["wrong_sound"])
            # Set volume for sound effects
            correct_sound.set_volume(1.0)
            wrong_sound.set_volume(1.0)
            page.data["sound_effects"]["correct"] = correct_sound
            page.data["sound_effects"]["wrong"] = wrong_sound
        except Exception as e:
            print(f"Error loading sound effects: {e}")

    def play_sound(sound_name):
        try:
            if sound_name in page.data["sound_effects"]:
                initialize_mixer()
                # Stop any currently playing sound before playing new one
                pygame.mixer.stop()
                page.data["sound_effects"][sound_name].play()
        except Exception as e:
            print(f"Error playing sound effect: {e}")

    def play_background_music():
        try:
            initialize_mixer()
            pygame.mixer.music.load(page.data["background_music"])
            pygame.mixer.music.set_volume(0.3)  # Set volume to 30%
            pygame.mixer.music.play(-1)  # -1 means loop indefinitely
            while page.data["is_playing"]:
                time.sleep(0.1)
        except Exception as e:
            print(f"Error playing background music: {e}")

    def start_background_music():
        if not page.data["is_playing"]:
            try:
                page.data["is_playing"] = True
                page.data["music_thread"] = threading.Thread(target=play_background_music, daemon=True)
                page.data["music_thread"].start()
            except Exception as e:
                print(f"Error starting background music: {e}")

    def stop_background_music():
        try:
            page.data["is_playing"] = False
            if page.data["music_thread"]:
                page.data["music_thread"].join(timeout=1.0)
                page.data["music_thread"] = None
            
            if page.data["mixer_initialized"]:
                pygame.mixer.music.stop()
                pygame.mixer.quit()
                page.data["mixer_initialized"] = False
        except Exception as e:
            print(f"Error stopping background music: {e}")
    
    def feedback(e):
        page.window.close()
        subprocess.run([sys.executable, "./other_code/feedback.py"])

    # Load sound effects when the app starts
    load_sound_effects()

    # Fixed subjects as fallback
    DEFAULT_SUBJECTS = ["Toán", "Ngữ Văn / Tiếng Việt", "Tiếng Anh", "Lịch sử", "Địa lý", "Khoa học"]
    
    # Fetch subjects from Supabase with fallback
    def fetch_subjects():
        try:
            if supabase:
                response = supabase.table("subjects").select("*").execute()
                if response.data:
                    return response.data  # Return full subject data including id and name
            return [{"id": i+1, "name": subject} for i, subject in enumerate(DEFAULT_SUBJECTS)]
        except Exception as e:
            print(f"Error fetching subjects: {e}")
            return [{"id": i+1, "name": subject} for i, subject in enumerate(DEFAULT_SUBJECTS)]

    # Fixed questions as fallback
    DEFAULT_QUESTIONS = {
        "Toán": [
            {
                "question": "2 + 2 = ?",
                "options": ["3", "4", "5", "6"],
                "correct_answer": 1
            },
            {
                "question": "5 × 3 = ?",
                "options": ["8", "10", "15", "20"],
                "correct_answer": 2
            }
        ],
        "Ngữ Văn / Tiếng Việt": [
            {
                "question": "Từ nào viết đúng chính tả?",
                "options": ["giàn dụa", "dàn giụa", "giàn giụa", "dàn dụa"],
                "correct_answer": 2
            }
        ],
        "Tiếng Anh": [
            {
                "question": "Apple nghĩa là gì?",
                "options": ["Quả cam", "Quả táo", "Quả chuối", "Quả lê"],
                "correct_answer": 1
            }
        ]
    }
    
    # Fetch questions for a subject from Supabase with fallback
    async def fetch_questions(subject_name, subject_id=None):
        try:
            if supabase and subject_id:
                # Query by subject_id instead of subject name
                response = supabase.table("questions").select("*").eq("subject_id", subject_id).execute()
                if response.data:
                    return [{
                        "question": q["question_text"],
                        "options": [q[f"option_{i+1}"] for i in range(4)],
                        "correct_answer": int(q["correct_option"]) - 1  # Convert to 0-based index
                    } for q in response.data]
            
            # Return default questions if no database connection or no questions
            return DEFAULT_QUESTIONS.get(subject_name, [])
        except Exception as e:
            print(f"Error fetching questions: {e}")
            return DEFAULT_QUESTIONS.get(subject_name, [])

    # Create styled button function
    def create_button(text, on_click, width=300, height=50, bgcolor="#3B71CA", color="white"):
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

    # Tạo view chọn môn học
    def main_view():
        start_background_music()  # Start background music when main view is shown
        subjects = fetch_subjects()
        
        # Header buttons with dark theme styling
        header_buttons = ft.Row(
            [
                create_button(
                    "Tắt âm thanh nền",
                    toggle_music,
                    width=150,
                    height=40,
                    bgcolor="#DC3545"
                ),
                create_button(
                    "Thông tin / Credit",
                    open_info,
                    width=150,
                    height=40,
                    bgcolor="#007BFF"
                ),
                create_button(
                    "Gửi feedback",
                    feedback,
                    width=150,
                    height=40,
                    bgcolor="#17A2B8"
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            width=500
        )

        # Subject buttons with consistent styling
        subject_buttons = ft.Column(
            [create_button(
                subject["name"],
                lambda e, s=subject: page.run_task(start_quiz, e, s),
                width=400,
                height=60,
                bgcolor="#161920"
            ) for subject in subjects],
            spacing=15,
            alignment=ft.MainAxisAlignment.CENTER
        )

        # Display current user info if available
        user_info = ft.Text("", size=14, color="#6C757D")
        if page.data["user_id"]:
            user_info.value = f"User ID: {page.data['user_id']}"

        main_content = ft.Column(
            [
                ft.Container(
                    content=ft.Image(src="./assest/icon.png", height=100),
                    alignment=ft.alignment.center
                ),
                user_info,  # Add user info display
                ft.Container(height=20),
                header_buttons,
                ft.Container(height=30),
                ft.Text("CHỌN MÔN HỌC", size=32, weight="bold", color="white"),
                ft.Container(height=20),
                subject_buttons
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        )

        # Scrollable container
        return ft.ListView(
            controls=[main_content],
            expand=True,
            spacing=10,
            padding=ft.padding.all(20)
        )

    # Bắt đầu làm bài
    async def start_quiz(e, subject):
        page.data["current_subject"] = subject["name"]
        page.data["current_subject_id"] = subject["id"]  # Store subject ID
        page.data["current_question_index"] = 0
        page.data["score"] = 0
        page.data["questions"] = await fetch_questions(subject["name"], subject["id"])
        
        # Handle case where no questions are available
        if not page.data["questions"]:
            page.snack_bar = ft.SnackBar(
                ft.Text(f"Không tìm thấy câu hỏi cho môn {subject['name']}!", color="white"),
                bgcolor="#DC3545"
            )
            page.snack_bar.open = True
            page.update()
            return
            
        await show_question()

    def logout(e):
        page.window.close()
        subprocess.run([sys.executable, "main.py"])
    
    # Hiển thị câu hỏi
    async def show_question():
        current_index = page.data["current_question_index"]
        questions = page.data["questions"]
        
        if current_index >= len(questions):
            stop_background_music()  # Stop background music when quiz ends
            await show_result()
            return

        question = questions[current_index]
        options = []

        for i, option in enumerate(question["options"]):
            async def option_click(e, idx=i):
                try:
                    # Disable all option buttons
                    for btn in options:
                        btn.disabled = True
                        if question["correct_answer"] == options.index(btn):
                            btn.style = ft.ButtonStyle(
                                color="white",
                                bgcolor="#28A745",  # Green for correct
                                text_style=ft.TextStyle(weight="bold")
                            )
                        elif btn == e.control:
                            btn.style = ft.ButtonStyle(
                                color="white",
                                bgcolor="#DC3545",  # Red for wrong
                                text_style=ft.TextStyle(weight="bold")
                            )
                        btn.update()

                    if idx == question["correct_answer"]:
                        page.data["score"] += 1
                        play_sound("correct")  # Play correct sound
                        page.snack_bar = ft.SnackBar(
                            content=ft.Text("Chính xác! 🎉", color="white"),
                            bgcolor="#28A745",
                            duration=1000
                        )
                        page.snack_bar.open = True
                    else:
                        play_sound("wrong")  # Play wrong sound
                        page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"Sai rồi! Đáp án đúng: {question['options'][question['correct_answer']]}", color="white"),
                            bgcolor="#DC3545",
                            duration=1000
                        )
                        page.snack_bar.open = True
                    page.update()

                    # Wait for the snack bar to be visible and show correct/wrong state
                    await asyncio.sleep(1)
                    
                    # Move to next question
                    page.data["current_question_index"] += 1
                    await show_question()
                except Exception as e:
                    print(f"Error in option_click: {e}")
                    # Continue to next question even if there's an error
                    page.data["current_question_index"] += 1
                    await show_question()

            options.append(
                create_button(
                    option,
                    option_click,
                    width=400,
                    height=60,
                    bgcolor="#161920"
                )
            )

        # Header buttons for quiz view
        quiz_header = ft.Row(
            [
                create_button(
                    "Tắt âm thanh nền" if not page.data["is_muted"] else "Bật âm thanh nền",
                    toggle_music,
                    width=150,
                    height=40,
                    bgcolor="#DC3545"
                ),
                create_button(
                    "Về màn hình chính",
                    return_to_main,
                    width=150,
                    height=40,
                    bgcolor="#6C757D"
                ),
                create_button(
                    "Đăng xuất",
                    logout,
                    width=150,
                    height=40,
                    bgcolor="#6C757D"
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            width=500
        )

        quiz_content = ft.Column(
            [
                quiz_header,
                ft.Container(height=20),
                ft.Text(f"Môn: {page.data['current_subject']}", size=20, weight="bold", color="white"),
                ft.Text(f"Câu {current_index + 1}/{len(questions)}", size=16, italic=True, color="#6C757D"),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Text(question["question"], size=24, weight="bold", color="white", text_align="center"),
                    padding=ft.padding.all(20),
                    bgcolor="#161920",
                    border_radius=10,
                    width=500
                ),
                ft.Container(height=10),
                ft.Text(f"Điểm: {page.data['score']}", size=18, weight="bold", color="#3B71CA"),
                ft.Container(height=20),
                ft.Column(
                    options,
                    spacing=15,
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

        # Scrollable quiz view
        quiz_view = ft.ListView(
            controls=[quiz_content],
            expand=True,
            spacing=10,
            padding=ft.padding.all(20)
        )

        page.clean()
        page.add(quiz_view)
    
    # Hiển thị kết quả
    async def show_result():
        score = page.data["score"]
        total = len(page.data["questions"])

        # Save score to database with improved error handling
        try:
            if supabase and page.data.get("user_id") and page.data.get("current_subject_id"):
                print(f"Saving score: user_id={page.data['user_id']}, subject_id={page.data['current_subject_id']}, score={score}")
                
                # Use the stored subject_id directly instead of querying by name
                subject_id = page.data["current_subject_id"]
                
                # Upsert the score (insert or update if exists)
                result = supabase.table("scores").upsert({
                    "user_id": page.data["user_id"],
                    "subject_id": subject_id,
                    "score": score
                }, on_conflict="user_id,subject_id").execute()
                
                print(f"Score saved successfully: {result.data}")
        except Exception as e:
            print(f"Error saving score: {e}")
            # Show error message to user
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Lỗi lưu điểm: {str(e)}", color="white"),
                bgcolor="#DC3545",
                duration=3000
            )
            page.snack_bar.open = True

        # Handle division by zero
        progress_value = score / total if total > 0 else 0
        percentage = int(progress_value * 100)

        # Determine result color based on performance
        if percentage >= 80:
            result_color = "#28A745"  # Green
            result_text = "Xuất sắc! 🏆"
        elif percentage >= 60:
            result_color = "#FFC107"  # Yellow
            result_text = "Tốt! 👍"
        else:
            result_color = "#DC3545"  # Red
            result_text = "Cần cố gắng thêm! 💪"

        result_content = ft.Column(
            [
                ft.Text("KẾT THÚC BÀI THI", size=32, weight="bold", color="white"),
                ft.Container(height=20),
                ft.Container(
                    content=ft.Column([
                        ft.Text(result_text, size=24, weight="bold", color=result_color),
                        ft.Text(f"Bạn đã đúng {score}/{total} câu!", size=20, color="white"),
                        ft.Text(f"Điểm số: {percentage}%", size=18, color="#3B71CA")
                    ], 
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.all(30),
                    bgcolor="#161920",
                    border_radius=15,
                    width=400
                ),
                ft.Container(height=20),
                ft.ProgressRing(
                    width=120, 
                    height=120, 
                    value=progress_value,
                    color=result_color,
                    stroke_width=8
                ),
                ft.Container(height=30),
                create_button(
                    "Về màn hình chính",
                    return_to_main,
                    width=300,
                    height=60,
                    bgcolor="#6C757D"
                )
            ],
            spacing=15,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

        # Scrollable result view
        result_view = ft.ListView(
            controls=[result_content],
            expand=True,
            spacing=10,
            padding=ft.padding.all(20)
        )
    
        page.clean()
        page.add(result_view)

    # Trở về màn hình chính
    async def return_to_main(e=None):
        stop_background_music()  # Stop background music when returning to main
        page.clean()
        page.add(main_view())

    # Khởi chạy ứng dụng
    await return_to_main()

ft.app(target=main)