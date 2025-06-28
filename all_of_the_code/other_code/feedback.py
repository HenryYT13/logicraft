import flet as ft
import requests
import subprocess
import sys

class FeedbackDialog(ft.AlertDialog):
    def __init__(self):
        super().__init__()
        self.modal = True
        self.title = ft.Text("Thông báo", color="white")
        self.content = ft.Text("Đã gửi feedback thành công!", color="white")
        self.actions = [
            ft.TextButton(
                "OK", 
                on_click=self.close_dlg,
                style=ft.ButtonStyle(color="#3B71CA")
            )
        ]
        self.actions_alignment = ft.MainAxisAlignment.END
        self.bgcolor = "#161920"
        self.open = False

    def close_dlg(self, e):
        self.open = False
        self.update()

def main(page: ft.Page):
    page.title = "Gửi feedback"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.scroll = "adaptive"
    page.bgcolor = "#0F1115"  # Dark background matching quiz app
    page.window_width = 600
    page.window_height = 700
    page.padding = 20

    webhook_url = "https://discord.com/api/webhooks/1356146309488316587/Tfy4sT7HAhcXypv01fpWTXlP0o-5tIVfTS0Nc1HWjmFVvupiv5FC1l7t7pfdo8BLqf1j"

    feedback_dialog = FeedbackDialog()

    # Initialize current_rating at the module level
    current_rating = 0

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

    # Input field with dark theme
    input_box = ft.TextField(
        hint_text="Nhập feedback của bạn vào đây",
        visible=False,
        width=450,
        multiline=True,
        min_lines=3,
        max_lines=5,
        bgcolor="#161920",
        color="white",
        hint_style=ft.TextStyle(color="#6C757D"),
        border_color="#3B71CA",
        focused_border_color="#17A2B8"
    )

    rating = ft.Ref[ft.Row]()
    selected_type = ft.Text("", color="white")

    def back_code(e):
        page.window.close()
        subprocess.run([sys.executable, "main.py"])

    # Styled checkboxes matching the quiz app theme
    checkboxes = [
        ft.Checkbox(
            label="Game bị lỗi (Vui lòng giải thích thêm bên dưới)",
            on_change=None,
            active_color="#3B71CA",
            check_color="white",
            label_style=ft.TextStyle(color="white", size=14)
        ),
        ft.Checkbox(
            label="Game có vấn đề (Vui lòng giải thích thêm bên dưới)",
            on_change=None,
            active_color="#3B71CA",
            check_color="white",
            label_style=ft.TextStyle(color="white", size=14)
        ),
        ft.Checkbox(
            label="Khác (Vui lòng giải thích thêm bên dưới)",
            on_change=None,
            active_color="#3B71CA",
            check_color="white",
            label_style=ft.TextStyle(color="white", size=14)
        ),
        ft.Checkbox(
            label="Độ hài lòng",
            on_change=None,
            active_color="#3B71CA",
            check_color="white",
            label_style=ft.TextStyle(color="white", size=14)
        ),
    ]

    def update_ui_based_on_selection(e):
        clicked_checkbox = e.control
        selected_label = clicked_checkbox.label

        # Uncheck all other checkboxes
        for cb in checkboxes:
            if cb != clicked_checkbox:
                cb.value = False

        selected_type.value = selected_label
        input_box.visible = False
        rating.current.visible = False
        star_container.visible = False

        if clicked_checkbox.value:  # Only react when being selected
            if selected_label in ["Game bị lỗi (Vui lòng giải thích thêm bên dưới)",
                                  "Game có vấn đề (Vui lòng giải thích thêm bên dưới)",
                                  "Khác (Vui lòng giải thích thêm bên dưới)"]:
                input_box.visible = True
            elif selected_label == "Độ hài lòng":
                rating.current.visible = True
                star_container.visible = True

        page.update()

    # Attach handler to checkboxes
    for cb in checkboxes:
        cb.on_change = update_ui_based_on_selection

    # Feedback options in a dark container
    feedback_options_container = ft.Container(
        content=ft.Column(checkboxes, spacing=15),
        padding=ft.padding.all(20),
        bgcolor="#161920",
        border_radius=10,
        width=500
    )

    def send_feedback(e):
        nonlocal current_rating
        msg = ""
        if selected_type.value in ["Game bị lỗi (Vui lòng giải thích thêm bên dưới)",
                                   "Game có vấn đề (Vui lòng giải thích thêm bên dưới)",
                                   "Khác (Vui lòng giải thích thêm bên dưới)"]:
            if input_box.value.strip() == "":
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Vui lòng nhập mô tả chi tiết!", color="white"),
                    bgcolor="#DC3545"
                )
                page.snack_bar.open = True
                page.update()
                return
            msg = f"Vấn đề được chọn :```{selected_type.value}```Giải thích:```{input_box.value.strip()}```"
        elif selected_type.value == "Độ hài lòng":
            if current_rating == 0:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Vui lòng chọn số sao đánh giá!", color="white"),
                    bgcolor="#DC3545"
                )
                page.snack_bar.open = True
                page.update()
                return
            msg = f"Bạn đã được đánh giá: `{current_rating}` sao!"
        else:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Vui lòng chọn loại feedback!", color="white"),
                bgcolor="#DC3545"
            )
            page.snack_bar.open = True
            page.update()
            return

        try:
            response = requests.post(webhook_url, json={"content": msg})
            if response.status_code == 204:
                print("Feedback sent successfully")
                # Reset form
                input_box.value = ""
                for cb in checkboxes:
                    cb.value = False
                selected_type.value = ""
                input_box.visible = False
                rating.current.visible = False
                star_container.visible = False
                current_rating = 0
                for star in rating.current.controls:
                    star.icon = ft.Icons.STAR_BORDER
                    star.icon_color = "#6C757D"
                
                feedback_dialog.open = True
                page.update()
            else:
                print("Failed to send feedback:", response.text)
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Lỗi gửi feedback. Vui lòng thử lại!", color="white"),
                    bgcolor="#DC3545"
                )
                page.snack_bar.open = True
                page.update()
        except Exception as ex:
            print(f"Error sending feedback: {ex}")
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Lỗi kết nối. Vui lòng thử lại!", color="white"),
                bgcolor="#DC3545"
            )
            page.snack_bar.open = True
            page.update()

    def on_star_click(e):
        nonlocal current_rating
        clicked_index = int(e.control.data)
        current_rating = clicked_index + 1
        for i, star in enumerate(rating.current.controls):
            if i <= clicked_index:
                star.icon = ft.Icons.STAR
                star.icon_color = "#FFC107"  # Gold color for filled stars
            else:
                star.icon = ft.Icons.STAR_BORDER
                star.icon_color = "#6C757D"  # Gray for empty stars
        page.update()

    # Star rating row
    star_row = ft.Row(
        [
            ft.IconButton(
                ft.Icons.STAR_BORDER,
                data=str(i),
                on_click=on_star_click,
                icon_color="#6C757D",
                icon_size=30
            )
            for i in range(5)
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        visible=False,
        ref=rating
    )

    # Star rating container
    star_container = ft.Container(
        content=ft.Column([
            ft.Text("Đánh giá độ hài lòng:", size=16, color="white", weight="bold"),
            star_row
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=ft.padding.all(20),
        bgcolor="#161920",
        border_radius=10,
        width=500,
        visible=False
    )

    # Action buttons
    button_row = ft.Row([
        create_button(
            "Trở về",
            back_code,
            width=150,
            height=50,
            bgcolor="#6C757D"
        ),
        create_button(
            "Gửi",
            send_feedback,
            width=150,
            height=50,
            bgcolor="#28A745"
        )
    ],
    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    width=350)

    # Main content
    main_content = ft.Column([
        ft.Container(
            content=ft.Image(src="./assest/icon.png", height=100),
            alignment=ft.alignment.center
        ),
        ft.Text("GỬI FEEDBACK", size=32, weight="bold", color="white"),
        ft.Text("Hãy cho chúng tôi biết ý kiến của bạn!", size=16, color="#6C757D", text_align="center"),
        ft.Container(height=20),
        ft.Text("Chọn loại feedback:", size=18, weight="bold", color="white"),
        feedback_options_container,
        ft.Container(height=15),
        input_box,
        star_container,
        ft.Container(height=20),
        button_row
    ],
    alignment=ft.MainAxisAlignment.CENTER,
    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    spacing=15)

    # Add everything to page
    page.add(
        ft.ListView(
            controls=[main_content],
            expand=True,
            spacing=10,
            padding=ft.padding.all(20)
        ),
        feedback_dialog
    )

ft.app(target=main)