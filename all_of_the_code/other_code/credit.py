import flet as ft 
import subprocess 
import sys

def feedback(e, page):
    page.window.close()
    subprocess.Popen([sys.executable, "other_code/feedback.py"])

def main(page: ft.Page):
    page.title = "Logicraft - Credits"
    # Title
    title = ft.Text("Logicraft", size=32, weight="bold", color="#4CAF50")
    subtitle = ft.Text("Một ứng dụng trả lời câu hỏi từ Lớp 1 ====> Lớp 6", size=18, color="#666666")

    # Credits Section
    credits_title = ft.Text("Credits / Thông tin", size=24, weight="bold", color="#2196F3")

    # Development Team
    team_section = ft.Column([
        ft.Text("Bộ phận phát triển", size=20, weight="bold", color="#FF5722"),
        ft.Text("Người tạo ra:", size=16),
        ft.Text("10th01 (Henry Khuong) (Khương Hữu Minh Quân)", size=18, weight="bold", color="#4CAF50"),
        ft.Text("Email: 10th01_main_account@proton.me", size=18, weight="bold", color="#4CAF50"),
        ft.Text("Số điện thoại: +84 876 039 564", size=18, weight="bold", color="#4CAF50"),
        ft.Text("Thông tin: henryyt13.github.io", size=18, weight="bold", color="#4CAF50"),
        ft.Text("Vai trò: Phát triển", size=14, color="#666666"),
    ], spacing=10)

    # Features Section
    features_section = ft.Column([
        ft.Text("Tính năng", size=20, weight="bold", color="#FF5722"),
        ft.Text("• Nhiều chủ đề môn học", size=16),
        ft.Text("• Giao diện trả lời câu hỏi", size=16),
        ft.Text("• Hệ thống đếm giờ", size=16),
        ft.Text("• Theo dõi điểm số", size=16),
        ft.Text("• Âm thanh", size=16),
    ], spacing=10)

    # Back Button
    back_button = ft.ElevatedButton(
        "Trở về trang chính",
        on_click=lambda e: [page.window.close(), subprocess.Popen([sys.executable, "other_code/main_windows.py"])],
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE,
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=10)
        )
    )   

    # Feedback Button
    feedback_button = ft.ElevatedButton(
        "Gửi feedback",
        on_click=lambda e: feedback(e, page),
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE,
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=10)
        )
    )

    # Main Content
    content = ft.Column(
        [
            ft.Image(src="./assest/icon.png", height=100),
            title,
            subtitle,
            ft.Divider(color="#E0E0E0", thickness=2),
            credits_title,
            ft.Divider(color="#E0E0E0", thickness=1),
            team_section,
            ft.Divider(color="#E0E0E0", thickness=1),
            features_section,
            ft.Divider(color="#E0E0E0", thickness=1),
            back_button,
            feedback_button
        ],
        spacing=20,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    page.add(content)

if __name__ == "__main__":
    ft.app(target=main)
