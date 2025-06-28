import os
import sys
import subprocess
import flet as ft
from dotenv import load_dotenv
from supabase import create_client, Client

# Load env
load_dotenv("./.secret/.env")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client | None = None

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    print("Supabase credentials missing – student_score page will not work.")

def get_students():
    if not supabase:
        return []
    res = supabase.table("users").select("id, username, email").eq("is_student", True).execute()
    return res.data if res.data else []

def get_subjects():
    if not supabase:
        return []
    res = supabase.table("subjects").select("id, name").execute()
    return res.data if res.data else []

def get_question_count_for_subject(subject_id: int):
    """Get total number of questions for a subject"""
    if not supabase:
        return 0
    res = supabase.table("questions").select("id").eq("subject_id", subject_id).execute()
    return len(res.data) if res.data else 0

def get_scores_for_student(user_id: str):
    """Return list of dict {subject_id, name, score, total_questions, completed}"""
    subjects = get_subjects()
    if not supabase:
        return []
    
    score_rows = supabase.table("scores").select("subject_id, score").eq("user_id", user_id).execute()
    score_map = {row["subject_id"]: row["score"] for row in (score_rows.data or [])}
    
    out = []
    for subj in subjects:
        total_questions = get_question_count_for_subject(subj["id"])
        user_score = score_map.get(subj["id"], None)
        completed = user_score is not None
        
        out.append({
            "subject_id": subj["id"],
            "name": subj["name"],
            "score": user_score if completed else 0,
            "total_questions": total_questions,
            "completed": completed
        })
    return out

def reset_score(user_id: str, subject_id: int):
    """Delete the score record to allow retaking"""
    if not supabase:
        return
    supabase.table("scores").delete().eq("user_id", user_id).eq("subject_id", subject_id).execute()

def create_button(text, on_click, width=300, height=50, bgcolor="#3B71CA", color="white"):
    """Create styled button matching the quiz app"""
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

def create_score_card(subject_data, on_reset_click):
    """Create beautiful score card for each subject"""
    name = subject_data["name"]
    score = subject_data["score"]
    total = subject_data["total_questions"]
    completed = subject_data["completed"]
    
    # Determine card colors based on completion and performance
    if not completed:
        card_color = "#2C3E50"  # Dark gray for not completed
        progress_color = "#6C757D"
        status_text = "Chưa làm"
        status_color = "#FFC107"
    elif total == 0:
        card_color = "#2C3E50"
        progress_color = "#6C757D"
        status_text = "Không có câu hỏi"
        status_color = "#6C757D"
    else:
        percentage = (score / total) * 100
        if percentage >= 80:
            card_color = "#1B5E20"  # Dark green
            progress_color = "#28A745"
            status_text = "Xuất sắc! 🏆"
            status_color = "#28A745"
        elif percentage >= 60:
            card_color = "#E65100"  # Dark orange
            progress_color = "#FFC107"
            status_text = "Tốt! 👍"
            status_color = "#FFC107"
        else:
            card_color = "#B71C1C"  # Dark red
            progress_color = "#DC3545"
            status_text = "Cần cố gắng! 💪"
            status_color = "#DC3545"

    # Score display
    score_display = f"{score}/{total}" if total > 0 else "0/0"
    
    # Progress value
    progress_value = (score / total) if total > 0 else 0
    
    # Reset button (only show if completed)
    reset_button = None
    if completed:
        reset_button = create_button(
            "Cho phép làm lại",
            lambda e: on_reset_click(subject_data["subject_id"]),
            width=120,
            height=35,
            bgcolor="#DC3545"
        )
    
    # Status indicator
    status_container = ft.Container(
        content=ft.Text(
            status_text,
            size=14,
            weight="bold",
            color="white"
        ),
        bgcolor=status_color,
        padding=ft.padding.symmetric(horizontal=12, vertical=6),
        border_radius=15
    )
    
    # Main card content
    card_content = ft.Column([
        # Header with subject name and status
        ft.Row([
            ft.Text(
                name,
                size=18,
                weight="bold",
                color="white"
            ),
            status_container
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        
        ft.Container(height=10),
        
        # Score and progress
        ft.Row([
            ft.Column([
                ft.Text(
                    "Điểm số",
                    size=12,
                    color="#6C757D"
                ),
                ft.Text(
                    score_display,
                    size=24,
                    weight="bold",
                    color="white"
                )
            ], spacing=2),
            
            ft.ProgressRing(
                width=60,
                height=60,
                value=progress_value,
                color=progress_color,
                stroke_width=6
            ) if total > 0 else ft.Container()
            
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        
        ft.Container(height=10),
        
        # Percentage and reset button
        ft.Row([
            ft.Text(
                f"{int(progress_value * 100)}%" if total > 0 else "N/A",
                size=16,
                color="#3B71CA",
                weight="bold"
            ),
            reset_button if reset_button else ft.Container()
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
    ], spacing=5)
    
    return ft.Container(
        content=card_content,
        bgcolor=card_color,
        border_radius=15,
        padding=ft.padding.all(20),
        width=400,
        border=ft.border.all(2, "#161920")
    )

def main(page: ft.Page):
    page.title = "Điểm Học Sinh"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.scroll = "adaptive"
    page.bgcolor = "#0F1115"  # Match quiz app background
    
    # UI controls
    student_dropdown = ft.Dropdown(
        width=400,
        label="Chọn học sinh",
        bgcolor="#161920",
        color="white",
        border_color="#3B71CA",
        text_style=ft.TextStyle(color="white"),
        label_style=ft.TextStyle(color="#6C757D")
    )
    
    scores_container = ft.Column(spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    status_text = ft.Text("", size=14)
    
    def load_students():
        students = get_students()
        student_dropdown.options = [
            ft.dropdown.Option(stu["id"], f"{stu['username']} ({stu['email']})") 
            for stu in students
        ]
        page.update()
    
    def refresh_scores(e=None):
        scores_container.controls.clear()
        status_text.value = ""
        
        if not student_dropdown.value:
            page.update()
            return
        
        # Get student info for header
        students = get_students()
        selected_student = next((s for s in students if s["id"] == student_dropdown.value), None)
        
        if selected_student:
            # Student info header
            student_info = ft.Container(
                content=ft.Column([
                    ft.Text(
                        f"Học sinh: {selected_student['username']}",
                        size=20,
                        weight="bold",
                        color="white"
                    ),
                    ft.Text(
                        selected_student['email'],
                        size=14,
                        color="#6C757D"
                    )
                ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor="#161920",
                border_radius=10,
                padding=ft.padding.all(15),
                width=400
            )
            scores_container.controls.append(student_info)
            scores_container.controls.append(ft.Container(height=20))
        
        # Get and display scores
        score_data = get_scores_for_student(student_dropdown.value)
        
        if not score_data:
            no_data_text = ft.Text(
                "Không có dữ liệu môn học",
                size=16,
                color="#6C757D",
                text_align="center"
            )
            scores_container.controls.append(no_data_text)
        else:
            # Summary stats
            total_subjects = len(score_data)
            completed_subjects = sum(1 for s in score_data if s["completed"])
            
            summary_card = ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text("Tổng môn học", size=12, color="#6C757D"),
                        ft.Text(str(total_subjects), size=20, weight="bold", color="white")
                    ], spacing=2),
                    ft.Column([
                        ft.Text("Đã hoàn thành", size=12, color="#6C757D"),
                        ft.Text(f"{completed_subjects}/{total_subjects}", size=20, weight="bold", color="#28A745")
                    ], spacing=2),
                    ft.Column([
                        ft.Text("Tỷ lệ hoàn thành", size=12, color="#6C757D"),
                        ft.Text(f"{int((completed_subjects/total_subjects)*100)}%" if total_subjects > 0 else "0%", 
                                size=20, weight="bold", color="#3B71CA")
                    ], spacing=2)
                ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                bgcolor="#161920",
                border_radius=10,
                padding=ft.padding.all(15),
                width=400
            )
            scores_container.controls.append(summary_card)
            scores_container.controls.append(ft.Container(height=10))
            
            # Individual subject cards
            for subject in score_data:
                card = create_score_card(
                    subject,
                    lambda sid: handle_reset(student_dropdown.value, sid)
                )
                scores_container.controls.append(card)
        
        page.update()
    
    def handle_reset(user_id: str, subject_id: int):
        try:
            reset_score(user_id, subject_id)
            refresh_scores()
            status_text.value = "✅ Đã cho phép học sinh làm lại bài kiểm tra!"
            status_text.color = "#28A745"
            
            # Show success snackbar
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Đã reset điểm thành công!", color="white"),
                bgcolor="#28A745",
                duration=2000
            )
            page.snack_bar.open = True
            page.update()
        except Exception as e:
            status_text.value = f"❌ Lỗi: {str(e)}"
            status_text.color = "#DC3545"
            page.update()
    
    def back(e):
        page.window.close()
        subprocess.run([sys.executable, "./user_code/teacher/teacher_main.py"])
    
    # Event handlers
    student_dropdown.on_change = refresh_scores
    load_students()
    
    # Header buttons
    header_buttons = ft.Row([
        create_button(
            "🔄 Làm mới",
            refresh_scores,
            width=120,
            height=40,
            bgcolor="#17A2B8"
        ),
        create_button(
            "⬅️ Quay lại",
            back,
            width=120,
            height=40,
            bgcolor="#6C757D"
        )
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=400)
    
    # Main content
    main_content = ft.Column([
        # Header with logo
        ft.Container(
            content=ft.Image(src="./assest/icon.png", height=80),
            alignment=ft.alignment.center
        ),
        ft.Container(height=10),
        
        # Title
        ft.Text(
            "QUẢN LÝ ĐIỂM HỌC SINH",
            size=28,
            weight="bold", 
            color="white",
            text_align="center"
        ),
        ft.Container(height=20),
        
        # Header buttons
        header_buttons,
        ft.Container(height=20),
        
        # Student selection
        student_dropdown,
        ft.Container(height=10),
        
        # Status message
        status_text,
        ft.Container(height=10),
        
        # Scores container
        scores_container
        
    ], alignment=ft.MainAxisAlignment.START, 
       horizontal_alignment=ft.CrossAxisAlignment.CENTER,
       spacing=10)
    
    # Scrollable main view
    page.add(
        ft.ListView(
            controls=[main_content],
            expand=True,
            spacing=10,
            padding=ft.padding.all(20)
        )
    )

if __name__ == "__main__":
    ft.app(target=main)