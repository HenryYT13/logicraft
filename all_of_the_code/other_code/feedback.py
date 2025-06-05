import flet as ft
import requests
import subprocess
import sys


class FeedbackDialog(ft.AlertDialog):
    def __init__(self):
        super().__init__()
        self.modal = True
        self.title = ft.Text("Thông báo")
        self.content = ft.Text("Đã gửi feedback thành công!")
        self.actions = [
            ft.TextButton("OK", on_click=self.close_dlg)
        ]
        self.actions_alignment = ft.MainAxisAlignment.END
        self.open = False

    def close_dlg(self, e):
        self.open = False
        self.update()


def main(page: ft.Page):
    page.title = "Gửi feedback"
    page.padding = 40
    page.window_width = 500
    page.window_height = 500

    webhook_url = "https://discord.com/api/webhooks/1356146309488316587/Tfy4sT7HAhcXypv01fpWTXlP0o-5tIVfTS0Nc1HWjmFVvupiv5FC1l7t7pfdo8BLqf1j"

    feedback_dialog = FeedbackDialog()

    input_box = ft.TextField(hint_text="Nhập feedback của bạn vào đây", visible=False, width=400)
    rating = ft.Ref[ft.Row]()
    selected_type = ft.Text("")
    current_rating = 0

    def back_code(e):
        page.window.close()
        subprocess.run([sys.executable, "main.py"])

    # References to checkboxes to manage selection
    checkboxes = [
        ft.Checkbox(label="Game bị lỗi (Vui lòng giải thích thêm bên dưới)", on_change=None),
        ft.Checkbox(label="Game có vấn đề (Vui lòng giải thích thêm bên dưới)", on_change=None),
        ft.Checkbox(label="Khác (Vui lòng giải thích thêm bên dưới)", on_change=None),
        ft.Checkbox(label="Độ hài lòng", on_change=None),
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

        if clicked_checkbox.value:  # Only react when being selected
            if selected_label in ["Game bị lỗi (Vui lòng giải thích thêm bên dưới)",
                                  "Game có vấn đề (Vui lòng giải thích thêm bên dưới)",
                                  "Khác (Vui lòng giải thích thêm bên dưới)"]:
                input_box.visible = True
            elif selected_label == "Độ hài lòng":
                rating.current.visible = True

        page.update()

    # Attach handler now that it's defined
    for cb in checkboxes:
        cb.on_change = update_ui_based_on_selection

    feedback_options = ft.Column(checkboxes, spacing=5)

    def send_feedback(e):
        msg = ""
        if selected_type.value in ["Game bị lỗi (Vui lòng giải thích thêm bên dưới)",
                                   "Game có vấn đề (Vui lòng giải thích thêm bên dưới)",
                                   "Khác (Vui lòng giải thích thêm bên dưới)"]:
            if input_box.value.strip() == "":
                return
            msg = f"Vấn đề được chọn :```{selected_type.value}```Giải thích:```{input_box.value.strip()}```"
        elif selected_type.value == "Độ hài lòng":
            if current_rating == 0:
                return
            msg = f"Bạn đã được đánh giá: `{current_rating}` sao!"
        else:
            return

        response = requests.post(webhook_url, json={"content": msg})
        if response.status_code == 204:
            print("Feedback sent successfully")
        else:
            print("Failed to send feedback:", response.text)

        input_box.value = ""
        for star in rating.current.controls:
            star.icon = ft.icons.STAR_BORDER
        feedback_dialog.open = True
        page.update()

    def on_star_click(e):
        nonlocal current_rating
        clicked_index = int(e.control.data)
        current_rating = clicked_index + 1
        for i, star in enumerate(rating.current.controls):
            star.icon = ft.icons.STAR if i <= clicked_index else ft.icons.STAR_BORDER
        page.update()

    star_row = ft.Row(
        [
            ft.IconButton(ft.icons.STAR_BORDER, data=str(i), on_click=on_star_click)
            for i in range(5)
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        visible=False,
        ref=rating
    )

    send_button = ft.ElevatedButton("Gửi", on_click=send_feedback)
    back_button = ft.ElevatedButton("Trở về", on_click=back_code)

    page.add(
        ft.Column([
            ft.Image(src="./assest/icon.png", height=100),
            ft.Text("Gửi Feedback", size=20, weight=ft.FontWeight.BOLD),
            feedback_options,
            input_box,
            star_row,
            send_button,
            ft.Row([back_button], alignment=ft.MainAxisAlignment.END)
        ], alignment=ft.MainAxisAlignment.CENTER,
           horizontal_alignment=ft.CrossAxisAlignment.CENTER,
           spacing=20),
        feedback_dialog
    )


ft.app(target=main)
