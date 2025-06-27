import os
import sys
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
    res = supabase.table("users").select("id, username, email").eq("student", True).execute()
    return res.data if res.data else []


def get_subjects():
    if not supabase:
        return []
    res = supabase.table("subjects").select("id, name").execute()
    return res.data if res.data else []


def get_scores_for_student(user_id: str):
    """Return list of dict {subject_id,name,score}"""
    subjects = get_subjects()
    if not supabase:
        return []
    score_rows = supabase.table("scores").select("subject_id, score").eq("user_id", user_id).execute()
    score_map = {row["subject_id"]: row["score"] for row in (score_rows.data or [])}
    out = []
    for subj in subjects:
        out.append({
            "subject_id": subj["id"],
            "name": subj["name"],
            "score": score_map.get(subj["id"], 0)
        })
    return out


def reset_score(user_id: str, subject_id: int):
    if not supabase:
        return
    supabase.table("scores").upsert({
        "user_id": user_id,
        "subject_id": subject_id,
        "score": 0
    }).execute()


def main(page: ft.Page):
    page.title = "Điểm Học Sinh"
    page.padding = 20
    page.bgcolor = "#0F1115"

    # UI controls defined later so handler can access
    student_dropdown = ft.Dropdown(width=400, label="Chọn học sinh")
    table_container = ft.Column(spacing=10)
    status_text = ft.Text(color="red")

    def load_students():
        students = get_students()
        student_dropdown.options = [ft.dropdown.Option(stu["id"], f"{stu['username']} ({stu['email']})") for stu in students]
        page.update()

    def refresh_scores(e=None):
        table_container.controls.clear()
        if not student_dropdown.value:
            page.update()
            return
        rows = get_scores_for_student(student_dropdown.value)
        for row in rows:
            score_text = ft.Text(str(row["score"]), width=50, color="white")
            reset_btn = ft.ElevatedButton("Reset", width=80, on_click=lambda ev, uid=student_dropdown.value, sid=row["subject_id"]: handle_reset(uid, sid))
            tbl_row = ft.Row([
                ft.Text(row["name"], width=200, color="white"),
                score_text,
                reset_btn
            ], spacing=20)
            table_container.controls.append(tbl_row)
        page.update()

    def handle_reset(user_id: str, subject_id: int):
        reset_score(user_id, subject_id)
        refresh_scores()
        status_text.value = "Đã đặt lại điểm."
        status_text.color = "green"
        page.update()

    def back(e):
        page.window.close()
        subprocess.run([sys.executable, "teacher/teacher_main.py"])

    student_dropdown.on_change = refresh_scores

    load_students()

    page.add(
        ft.Column([
            ft.Row([ft.Image(src="./assest/icon.png", height=80)], alignment=ft.MainAxisAlignment.CENTER),
            student_dropdown,
            ft.Container(height=10),
            table_container,
            status_text,
            ft.ElevatedButton("Quay lại", on_click=back)
        ], alignment=ft.MainAxisAlignment.START, spacing=15)
    )


if __name__ == "__main__":
    ft.app(target=main)
