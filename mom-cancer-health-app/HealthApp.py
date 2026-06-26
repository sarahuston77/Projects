import argparse
import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk

import reminders
import storage


class HealthReminderApp:
    def __init__(self, demo_mode=False):
        self.demo_mode = demo_mode
        self.reminder_configs = []
        self.active_reminder = None
        self.root = tk.Tk()
        self.root.title("Care Companion")
        self.root.geometry("1100x760")
        self.root.minsize(900, 680)
        self.root.configure(bg="#f4f7fb")
        self.root.option_add("*Font", "Segoe UI 11")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        storage.init_db()
        self.reminder_configs = self._load_reminder_configs()
        self._build_ui()
        self._refresh_status()
        self.root.after(300, self._check_reminders_loop)

        if self.demo_mode:
            self.root.after(1000, self._run_demo_sequence)

        self.root.mainloop()

    def _load_reminder_configs(self):
        try:
            return reminders.load_reminders()
        except (OSError, ValueError, KeyError) as exc:
            print(f"Could not load reminders.json, using defaults: {exc}")
            return reminders.build_fallback_reminders()

    def _build_ui(self):
        self.main = ttk.Frame(self.root, padding=24)
        self.main.pack(fill="both", expand=True)
        self.main.configure(style="Main.TFrame")

        self.header = tk.Frame(self.main, bg="#1f4e7a", height=120)
        self.header.pack(fill="x", pady=(0, 18))
        self.header.pack_propagate(False)

        icon_path = os.path.join(os.path.dirname(__file__), "assets", "images", "dog-training.png")
        self.header_icon = self._load_image(icon_path, (70, 70))
        tk.Label(self.header, image=self.header_icon, bg="#1f4e7a").place(x=24, y=24)

        tk.Label(
            self.header,
            text="Care Companion",
            fg="white",
            bg="#1f4e7a",
            font=("Segoe UI", 24, "bold"),
        ).place(x=110, y=26)
        tk.Label(
            self.header,
            text="Comfort, reminders, and daily support in one place",
            fg="#e4f2ff",
            bg="#1f4e7a",
            font=("Segoe UI", 13),
        ).place(x=110, y=66)

        content = tk.Frame(self.main, bg="#f4f7fb")
        content.pack(fill="both", expand=True)

        left_panel = tk.Frame(content, bg="white", padx=20, pady=20)
        left_panel.pack(side="left", fill="both", expand=True)

        right_panel = tk.Frame(content, bg="#f8fbff", padx=20, pady=20)
        right_panel.pack(side="right", fill="both", expand=False)
        right_panel.configure(width=360)

        tk.Label(
            left_panel,
            text="Daily care actions",
            font=("Segoe UI", 20, "bold"),
            fg="#243b53",
            bg="white",
            anchor="w",
        ).pack(fill="x", pady=(0, 6))
        tk.Label(
            left_panel,
            text="Track sleep, log mood, and review your week.",
            font=("Segoe UI", 13),
            fg="#5b6f84",
            bg="white",
            anchor="w",
        ).pack(fill="x", pady=(0, 18))

        self.sleep_label_var = tk.StringVar(value="Log your Sleep (1-10):")
        tk.Label(left_panel, textvariable=self.sleep_label_var, fg="#243b53", bg="white", anchor="w", font=("Segoe UI", 13, "bold")).pack(fill="x", pady=(8, 4))
        self.sleep_button = tk.Button(left_panel, text="Log Sleep", bg="#2b73c9", fg="white", relief="flat", padx=12, pady=10, command=self.log_sleep)
        self.sleep_button.pack(fill="x", pady=(0, 12))

        self.mood_label_var = tk.StringVar(value="Log your Mood (1-10):")
        tk.Label(left_panel, textvariable=self.mood_label_var, fg="#243b53", bg="white", anchor="w", font=("Segoe UI", 13, "bold")).pack(fill="x", pady=(8, 4))
        self.mood_button = tk.Button(left_panel, text="Log Mood", bg="#2b73c9", fg="white", relief="flat", padx=12, pady=10, command=self.log_mood)
        self.mood_button.pack(fill="x", pady=(0, 12))

        self.history_button = tk.Button(left_panel, text="View This Week", bg="#5c7b99", fg="white", relief="flat", padx=12, pady=10, command=self.show_week_history)
        self.history_button.pack(fill="x", pady=(8, 0))

        tk.Label(
            right_panel,
            text="Today’s reminder",
            font=("Segoe UI", 20, "bold"),
            fg="#243b53",
            bg="#f8fbff",
            anchor="w",
        ).pack(fill="x", pady=(0, 6))
        tk.Label(
            right_panel,
            text="A calm, supportive check-in for the day.",
            font=("Segoe UI", 13),
            fg="#5b6f84",
            bg="#f8fbff",
            anchor="w",
        ).pack(fill="x", pady=(0, 18))

        self.reminder_text_var = tk.StringVar(value=self._waiting_message())
        self.reminder_message = tk.Label(
            right_panel,
            textvariable=self.reminder_text_var,
            wraplength=300,
            justify="left",
            fg="#2f4156",
            bg="#f8fbff",
            anchor="nw",
            font=("Segoe UI", 12),
        )
        self.reminder_message.pack(fill="both", expand=True, pady=(0, 18))

        self.acknowledge_button = tk.Button(right_panel, text="Acknowledge", bg="#1f4e7a", fg="white", relief="flat", padx=12, pady=10, command=self.acknowledge_reminder)
        self.acknowledge_button.pack(fill="x")

        self.summary_text = tk.StringVar(value="")

    def _load_image(self, path, size):
        image = Image.open(path).convert("RGBA")
        image = image.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image)

    def _waiting_message(self):
        next_times = ", ".join(r["time"] for r in self.reminder_configs[:3])
        if len(self.reminder_configs) > 3:
            next_times += ", ..."
        return (
            "Reminders appear at your scheduled times.\n"
            f"Today: {next_times}\n\n"
            "Tap Acknowledge when you see a reminder."
        )

    def _refresh_status(self):
        self.reminder_text_var.set(self._waiting_message())

    def _check_reminders_loop(self):
        self.check_reminders()
        self.root.after(30000, self._check_reminders_loop)

    def check_reminders(self):
        if self.active_reminder:
            return
        due = storage.get_due_reminders(self.reminder_configs)
        if due:
            self.active_reminder = due[0]
            self.reminder_text_var.set(self.active_reminder["text"])

    def acknowledge_reminder(self):
        if self.active_reminder:
            storage.mark_reminder_shown(self.active_reminder["id"])
            self.active_reminder = None
        self.reminder_text_var.set(self._waiting_message())

    def log_sleep(self):
        self._prompt_for_rating("Log Sleep", "Enter your sleep rating (1-10):", self.store_sleep)

    def log_mood(self):
        self._prompt_for_rating("Log Mood", "Enter your mood rating (1-10):", self.evaluate_mood)

    def _prompt_for_rating(self, title, prompt_text, callback):
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.transient(self.root)
        popup.grab_set()
        popup.configure(padx=18, pady=18, bg="white")
        popup.geometry("360x180")

        tk.Label(popup, text=prompt_text, bg="white", font=("Segoe UI", 12), anchor="w").pack(fill="x", pady=(0, 10))
        entry = ttk.Entry(popup, width=24)
        entry.pack(fill="x", pady=(0, 12))
        entry.focus_set()

        def submit():
            callback(entry.get())
            popup.destroy()

        ttk.Button(popup, text="Save", command=submit).pack(anchor="e")
        popup.bind("<Return>", lambda event: submit())

    def revert_sleep_label(self):
        self.sleep_label_var.set("Log your Sleep (1-10):")

    def store_sleep(self, sleep_value):
        try:
            sleep = int(sleep_value)
            if not 1 <= sleep <= 10:
                raise ValueError
            storage.save_log("sleep", sleep)
            self.sleep_label_var.set(f"Logged Sleep: {sleep} (saved)")
            self.reminder_text_var.set("Sleep saved. Great — keep up the good sleep habits!")
            self.root.after(2000, self.revert_sleep_label)
        except ValueError:
            self.reminder_text_var.set("Invalid sleep rating. Enter a whole number from 1 to 10.")

    def revert_mood_label(self):
        self.mood_label_var.set("Log your Mood (1-10):")

    def evaluate_mood(self, mood_value):
        try:
            mood = int(mood_value)
            if not 1 <= mood <= 10:
                raise ValueError
            storage.save_log("mood", mood)
            self.mood_label_var.set(f"Logged Mood: {mood} (saved)")
            self.reminder_text_var.set("Mood saved. I’m happy you’re in a good mood")
            self.root.after(2000, self.revert_mood_label)
        except ValueError:
            self.reminder_text_var.set("Invalid mood rating. Enter a whole number from 1 to 10.")

    def show_week_history(self):
        summary = storage.format_weekly_summary(days=7)
        popup = tk.Toplevel(self.root)
        popup.title("This Week")
        popup.transient(self.root)
        popup.configure(bg="white")
        popup.geometry("520x420")

        text_widget = tk.Text(popup, wrap="word", padx=12, pady=12, bg="white", fg="#243b53")
        text_widget.insert("1.0", summary)
        text_widget.configure(state="disabled")
        text_widget.pack(fill="both", expand=True)

    def on_close(self):
        self.root.destroy()

    def _run_demo_sequence(self):
        output_dir = os.path.join(os.path.dirname(__file__), "demo_output")
        os.makedirs(output_dir, exist_ok=True)

        self._save_preview(os.path.join(output_dir, "demo_capture_1.png"), "Welcome", self._waiting_message())
        self.sleep_label_var.set("Logged Sleep: 8 (saved)")
        self.mood_label_var.set("Logged Mood: 7 (saved)")
        self.reminder_text_var.set("Mood saved. I’m happy you’re in a good mood")
        self._save_preview(os.path.join(output_dir, "demo_capture_2.png"), "Daily log", "Sleep: 8 | Mood: 7")

        summary = storage.format_weekly_summary(days=7)
        self._save_preview(os.path.join(output_dir, "demo_capture_3.png"), "This Week", summary)
        self.root.after(500, self.root.destroy)

    def _save_preview(self, path, title, body):
        img = Image.new("RGB", (1400, 900), "#f4f7fb")
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle((40, 40, 1360, 860), radius=28, fill="#ffffff", outline="#dfe7f2", width=2)
        draw.rounded_rectangle((60, 60, 1340, 180), radius=24, fill="#1f4e7a")
        draw.text((95, 90), "Care Companion", fill="white", font=ImageFont.load_default(size=40) if hasattr(ImageFont, "load_default") else ImageFont.load_default())
        draw.text((95, 130), "Comfort, reminders, and daily support in one place", fill="#e8f3ff")
        draw.rounded_rectangle((80, 230, 620, 720), radius=24, fill="#ffffff", outline="#e1e8f2")
        draw.rounded_rectangle((700, 230, 1320, 720), radius=24, fill="#f8fbff", outline="#e1e8f2")
        draw.text((110, 270), title, fill="#243b53")
        draw.text((110, 320), body.replace("\n", "\n"), fill="#4b5e72")
        img.save(path)
        print(f"Saved preview image: {path}")


def main():
    parser = argparse.ArgumentParser(description="Health reminder app")
    parser.add_argument("--demo", action="store_true", help="Generate a polished demo preview screenshot and exit")
    args = parser.parse_args()
    HealthReminderApp(demo_mode=args.demo)


if __name__ == "__main__":
    main()
