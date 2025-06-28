import flet as ft
import subprocess
import sys

def feedback(e, page):
    page.window.close()
    subprocess.Popen([sys.executable, "other_code/feedback.py"])

def main(page: ft.Page):
    page.title = "Logicraft - Credits"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.scroll = "adaptive"
    page.bgcolor = "#0F1115"  # Dark background matching quiz app
    page.window_width = 600
    page.window_height = 700
    page.padding = 20

    # Create styled button function matching quiz app
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

    # Header with app icon
    header = ft.Container(
        content=ft.Image(src="./assest/icon.png", height=100),
        alignment=ft.alignment.center
    )

    # Title matching quiz app style
    title = ft.Text("LOGICRAFT", size=32, weight="bold", color="white")
    subtitle = ft.Text("Một ứng dụng trả lời câu hỏi từ Lớp 1 ====> Lớp 6", 
                      size=16, color="#6C757D", text_align="center")

    # Credits section with dark theme containers
    credits_title = ft.Text("THÔNG TIN / CREDITS", size=24, weight="bold", color="white")

    # Development team section in a dark container
    team_container = ft.Container(
        content=ft.Column([
            ft.Text("BỘ PHẬN PHÁT TRIỂN", size=18, weight="bold", color="#3B71CA"),
            ft.Container(height=10),
            ft.Text("Người tạo ra:", size=14, color="#6C757D"),
            ft.Text("10th01 (Henry Khuong)", size=16, weight="bold", color="white"),
            ft.Text("(Khương Hữu Minh Quân)", size=16, weight="bold", color="white"),
            ft.Container(height=5),
            ft.Text("Email: 10th01_main_account@proton.me", size=14, color="#6C757D"),
            ft.Text("Số điện thoại: +84 876 039 564", size=14, color="#6C757D"),
            ft.Text("Thông tin: henryyt13.github.io", size=14, color="#6C757D"),
            ft.Container(height=5),
            ft.Text("Vai trò: Phát triển", size=14, color="#17A2B8"),
        ], 
        spacing=8,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=ft.padding.all(20),
        bgcolor="#161920",
        border_radius=10,
        width=500
    )

    # Features section in a dark container
    features_container = ft.Container(
        content=ft.Column([
            ft.Text("TÍNH NĂNG", size=18, weight="bold", color="#3B71CA"),
            ft.Container(height=10),
            ft.Text("• Nhiều chủ đề môn học", size=14, color="white"),
            ft.Text("• Giao diện trả lời câu hỏi", size=14, color="white"),
            ft.Text("• Hệ thống đếm giờ", size=14, color="white"),
            ft.Text("• Theo dõi điểm số", size=14, color="white"),
            ft.Text("• Âm thanh nền và hiệu ứng", size=14, color="white"),
            ft.Text("• Lưu trữ dữ liệu người dùng", size=14, color="white"),
        ], 
        spacing=8,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=ft.padding.all(20),
        bgcolor="#161920",
        border_radius=10,
        width=500
    )

    # Action buttons
    button_row = ft.Row([
        create_button(
            "Trở về trang chính",
            lambda e: [page.window.close(), subprocess.Popen([sys.executable, "other_code/main_windows.py"])],
            width=200,
            height=50,
            bgcolor="#6C757D"
        ),
        create_button(
            "Gửi feedback",
            lambda e: feedback(e, page),
            width=200,
            height=50,
            bgcolor="#17A2B8"
        )
    ],
    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    width=450)

    # Main content
    main_content = ft.Column(
        [
            header,
            ft.Container(height=10),
            title,
            subtitle,
            ft.Container(height=20),
            credits_title,
            ft.Container(height=15),
            team_container,
            ft.Container(height=15),
            features_container,
            ft.Container(height=20),
            button_row
        ],
        spacing=10,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    # Scrollable container
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