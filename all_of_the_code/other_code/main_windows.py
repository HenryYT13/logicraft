import flet as ft
import asyncio
import threading
import time
import pygame
import json
import subprocess
import sys

def load_questions():
    try:
        with open('json/questions.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading questions: {e}")
        return {}

# Load questions from JSON file
quizzes = load_questions()

async def main(page: ft.Page):
    page.title = "Logicraft"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.scroll = "adaptive"
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

    feedback_button = ft.ElevatedButton("Gửi feedback", on_click=lambda e: feedback(e))

    # Load sound effects when the app starts
    load_sound_effects()

    # Tạo view chọn môn học
    def main_view():
        start_background_music()  # Start background music when main view is shown
        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Image(src="./assest/icon.png", height=100),
                        ft.ElevatedButton(
                            "Tắt âm thanh nền",
                            on_click=toggle_music,
                            width=150,
                            height=40,
                            bgcolor="red",
                            color="white"
                        ),
                        ft.ElevatedButton(
                            "Thông tin / Credit",
                            on_click=open_info,
                            width=150,
                            height=40,
                            bgcolor="blue",
                            color="white"
                        ),
                        ft.ElevatedButton(
                            "Gửi feedback",
                            on_click=feedback,
                            width=150,
                            height=40,
                            bgcolor="cyan",
                            color="black"
                        ),
                        
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    width=400
                ),
                ft.Text("CHỌN MÔN HỌC", size=30, weight="bold"),
                ft.Column(
                    [ft.ElevatedButton(
                        subject,
                        on_click=lambda e, s=subject: page.run_task(start_quiz, e, s),
                        width=300,
                        height=50
                    ) for subject in quizzes.keys()],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=30
        )

    # Bắt đầu làm bài
    async def start_quiz(e, subject):
        page.data["current_subject"] = subject
        page.data["current_question_index"] = 0
        page.data["score"] = 0
        await show_question()

    def logout(e):
        page.window.close()
        subprocess.run([sys.executable, "main.py"])
    
    # Hiển thị câu hỏi
    async def show_question():
        subject = page.data["current_subject"]
        current_index = page.data["current_question_index"]
        questions = quizzes[subject]["questions"]
        
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
                                bgcolor="green"  # Highlight correct answer
                            )
                        elif btn == e.control:
                            btn.style = ft.ButtonStyle(
                                color="white",
                                bgcolor="red"  # Highlight wrong answer if this was clicked
                            )
                        btn.update()

                    if idx == question["correct_answer"]:
                        page.data["score"] += 1
                        play_sound("correct")  # Play correct sound
                        page.snack_bar = ft.SnackBar(
                            content=ft.Text("Chính xác! 🎉", color="white"),
                            bgcolor="green",
                            duration=1000
                        )
                        page.snack_bar.open = True
                    else:
                        play_sound("wrong")  # Play wrong sound
                        page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"Sai rồi! Đáp án đúng: {question['options'][question['correct_answer']]}", color="white"),
                            bgcolor="red",
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
                ft.ElevatedButton(
                    option,
                    on_click=option_click,
                    width=300,
                    height=50,
                    style=ft.ButtonStyle(
                        color="white",
                        bgcolor="#4a148c"
                    )
                )
            )

        view = ft.Column(
            [
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Tắt âm thanh nền" if not page.data["is_muted"] else "Bật âm thanh nền",
                            on_click=toggle_music,
                            width=150,
                            height=40,
                            bgcolor="red",
                            color="white"
                        ),
                        ft.ElevatedButton(
                            "Về màn hình chính",
                            on_click=return_to_main,
                            width=150,
                            height=40,
                            bgcolor="grey",
                            color="white"
                        ),
                        ft.ElevatedButton(
                            "Đăng xuất",
                            on_click=return_to_main,
                            width=150,
                            height=40,
                            bgcolor="grey",
                            color="white"
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    width=400
                ),
                ft.Text(f"Môn: {subject}", size=20, weight="bold"),
                ft.Text(f"Câu {current_index + 1}/{len(questions)}", italic=True),
                ft.Text(question["question"], size=24, weight="bold"),
                ft.Text(f"Điểm: {page.data['score']}", size=16),
                *options
            ],
            spacing=30,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

        page.clean()
        page.add(view)
    
    # Hiển thị kết quả
    async def show_result():
        score = page.data["score"]
        total = len(quizzes[page.data["current_subject"]]["questions"])
        view = ft.Column(
            [
                ft.Text("KẾT THÚC BÀI THI", size=30, weight="bold"),
                ft.Text(f"Bạn đã đúng {score}/{total} câu!", size=24),
                ft.ProgressRing(width=100, height=100, value=score/total),
                ft.ElevatedButton(
                    "Về màn hình chính",
                    on_click=return_to_main,
                    color="white",
                    bgcolor="grey"
                )
                
            ],
            spacing=30,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    
        page.clean()
        page.add(view)

    # Trở về màn hình chính
    async def return_to_main(e=None):
        stop_background_music()  # Stop background music when returning to main
        page.clean()
        page.add(main_view())

    # Khởi chạy ứng dụng
    await return_to_main()

ft.app(target=main)