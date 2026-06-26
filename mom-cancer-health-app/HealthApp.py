import argparse
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText

os.environ.setdefault("KIVY_NO_ARGS", "1")

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

import personalization
import reminders
import storage
import ui_theme as theme
from ui_components import AccentButton, Card, SectionHeader, Spacer, StatusBadge


class HealthReminderApp(App):
    title = "Care Companion"

    def __init__(self, demo_mode=False, screenshot_mode=False, no_audio=False, **kwargs):
        super().__init__(**kwargs)
        self.demo_mode = demo_mode
        self.screenshot_mode = screenshot_mode
        self.no_audio = no_audio
        self.active_reminder = None
        self.reminder_configs = []
        self.profile = personalization.load_profile()

    def build(self):
        storage.init_db()
        self.profile = personalization.load_profile()
        if self.demo_mode:
            storage.seed_demo_data()
        self.reminder_configs = self._load_reminder_configs()

        Window.clearcolor = theme.BG
        Window.size = (1280, 800)
        Window.minimum_width = 960
        Window.minimum_height = 640

        root = BoxLayout(orientation="vertical", padding=dp(24), spacing=dp(20))
        self.root = root
        with root.canvas.before:
            Color(*theme.BG)
            self.root_bg = Rectangle()
        root.bind(pos=self._sync_root_bg, size=self._sync_root_bg)

        root.add_widget(self._build_header())
        root.add_widget(Spacer(12))

        body = BoxLayout(orientation="horizontal", spacing=dp(20), size_hint_y=1)
        body.add_widget(self._build_wellness_panel())
        body.add_widget(self._build_reminder_panel())
        root.add_widget(body)

        if not self.no_audio:
            self.play_song()

        Clock.schedule_interval(self.check_reminders, 30)

        if self.demo_mode:
            Clock.schedule_once(self._apply_demo_state, 0.5)

        if self.screenshot_mode:
            Clock.schedule_once(self._capture_screenshots, 2.0)

        Window.bind(on_resize=self.update_font_sizes)
        self.update_font_sizes(Window, Window.width, Window.height)
        return root

    def _sync_root_bg(self, *_args):
        self.root_bg.pos = self.root.pos
        self.root_bg.size = self.root.size

    def _build_header(self):
        header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(88),
            padding=(dp(24), dp(16)),
            spacing=dp(16),
        )
        with header.canvas.before:
            Color(*theme.PRIMARY)
            self.header_bg = RoundedRectangle(radius=[dp(theme.CARD_RADIUS)])

        def _sync_header(*_args):
            self.header_bg.pos = header.pos
            self.header_bg.size = header.size

        header.bind(pos=_sync_header, size=_sync_header)

        title_block = BoxLayout(orientation="vertical", spacing=dp(2), size_hint_x=0.65)
        self.title_label = Label(
            text=f"{self.profile['user_name']}'s Care Companion",
            font_size=dp(28),
            bold=True,
            color=theme.TEXT_ON_PRIMARY,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(36),
        )
        self.subtitle_label = Label(
            text=f"Daily wellness and reminders for {self.profile['user_name']}",
            font_size=dp(14),
            color=(1, 1, 1, 0.85),
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(22),
        )
        self.title_label.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0], None)))
        self.subtitle_label.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0], None)))
        title_block.add_widget(self.title_label)
        title_block.add_widget(self.subtitle_label)

        self.date_label = Label(
            text=datetime.now().strftime("%A, %B %d"),
            font_size=dp(14),
            color=(1, 1, 1, 0.9),
            halign="right",
            valign="middle",
            size_hint_x=0.35,
        )

        header.add_widget(title_block)
        header.add_widget(Widget())  # spacer
        header.add_widget(self.date_label)
        return header

    def _build_wellness_panel(self):
        panel = BoxLayout(orientation="vertical", spacing=dp(16), size_hint_x=0.55)

        wellness_card = Card(spacing=12)
        wellness_card.add_widget(
            SectionHeader("Wellness Check-In", "Track sleep and mood on a 1–10 scale")
        )

        self.sleep_status = Label(
            text="Sleep: not logged today",
            font_size=dp(15),
            color=theme.TEXT_SECONDARY,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(24),
        )
        self.mood_status = Label(
            text="Mood: not logged today",
            font_size=dp(15),
            color=theme.TEXT_SECONDARY,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(24),
        )
        self.sleep_status.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0], None)))
        self.mood_status.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0], None)))

        wellness_card.add_widget(self.sleep_status)
        wellness_card.add_widget(self.mood_status)
        wellness_card.add_widget(Spacer(8))

        self.sleep_button = AccentButton(text="Log Sleep", accent_color=theme.ACCENT_SLEEP)
        self.sleep_button.bind(on_press=self.log_sleep)
        self.mood_button = AccentButton(text="Log Mood", accent_color=theme.ACCENT_MOOD)
        self.mood_button.bind(on_press=self.log_mood)
        self.history_button = AccentButton(text="View This Week", accent_color=theme.ACCENT_HISTORY)
        self.history_button.bind(on_press=self.show_week_history)

        wellness_card.add_widget(self.sleep_button)
        wellness_card.add_widget(self.mood_button)
        wellness_card.add_widget(self.history_button)
        panel.add_widget(wellness_card)

        schedule_card = Card(spacing=10)
        schedule_card.add_widget(SectionHeader("Today's Schedule", "Upcoming reminders"))
        schedule_scroll = ScrollView(size_hint_y=1, do_scroll_x=False)
        self.schedule_label = Label(
            text=self._schedule_text(),
            font_size=dp(14),
            color=theme.TEXT_SECONDARY,
            halign="left",
            valign="top",
            size_hint_y=None,
            markup=False,
        )
        self.schedule_label.bind(texture_size=self._set_label_height)
        self.schedule_label.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0], None)))
        schedule_scroll.add_widget(self.schedule_label)
        schedule_card.add_widget(schedule_scroll)
        panel.add_widget(schedule_card)

        return panel

    def _build_reminder_panel(self):
        panel = BoxLayout(orientation="vertical", size_hint_x=0.45)

        reminder_card = Card(bg_color=theme.SURFACE_ALT, spacing=14)
        header_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(36))
        header_row.add_widget(
            Label(
                text="Active Reminder",
                font_size=dp(20),
                bold=True,
                color=theme.TEXT_PRIMARY,
                halign="left",
                valign="middle",
            )
        )
        self.status_badge = StatusBadge(text="Waiting", status="waiting")
        header_row.add_widget(self.status_badge)

        self.reminder_message_label = Label(
            text=self._waiting_message(),
            font_size=dp(17),
            color=theme.TEXT_PRIMARY,
            halign="left",
            valign="top",
            size_hint_y=1,
            line_height=1.35,
        )
        self.reminder_message_label.bind(size=self._update_reminder_text_size)

        self.acknowledge_button = AccentButton(
            text="Acknowledge Reminder",
            accent_color=theme.PRIMARY,
            size_hint_y=None,
            height=dp(58),
        )
        self.acknowledge_button.bind(on_press=self.acknowledge_reminder)

        reminder_card.add_widget(header_row)
        reminder_card.add_widget(Spacer(4))
        reminder_card.add_widget(self.reminder_message_label)
        reminder_card.add_widget(Spacer(8))
        reminder_card.add_widget(self.acknowledge_button)
        panel.add_widget(reminder_card)

        return panel

    def _load_reminder_configs(self):
        try:
            return reminders.load_reminders()
        except (OSError, ValueError, KeyError) as e:
            print(f"Could not load reminders.json, using defaults: {e}")
            return reminders.build_fallback_reminders()

    def _schedule_text(self):
        lines = []
        for r in self.reminder_configs:
            lines.append(f"  {r['time']}  ·  {r['text'].split(chr(10))[0]}")
        return "\n".join(lines)

    def _waiting_message(self):
        greeting = personalization.build_greeting(self.profile)
        if self.reminder_configs:
            next_times = ", ".join(r["time"] for r in self.reminder_configs[:3])
            if len(self.reminder_configs) > 3:
                next_times += ", ..."
            return (
                f"{greeting}\n"
                f"Reminders are here for you today.\n"
                f"Today: {next_times}\n\n"
                "When one shows up here, tap Acknowledge to mark it complete."
            )
        return (
            f"{greeting}\n\n"
            "You're all caught up for now. Reminders will appear here when they are due."
        )

    def _update_reminder_text_size(self, instance, value):
        instance.text_size = (value[0], None)

    def _set_label_height(self, instance, texture_size):
        instance.height = max(texture_size[1], dp(24))

    def update_font_sizes(self, window, width, height):
        scale = max(width / 1280, 0.85)
        self.title_label.font_size = dp(28 * scale)
        self.subtitle_label.font_size = dp(14 * scale)
        self.date_label.font_size = dp(14 * scale)
        self.reminder_message_label.font_size = dp(17 * scale)

    def _apply_demo_state(self, _dt):
        if self.reminder_configs:
            self.active_reminder = self.reminder_configs[0]
            self.reminder_message_label.text = self.active_reminder["text"]
            self.status_badge.set_status("active", "Due now")
            self.acknowledge_button.background_color = theme.ACCENT_ALERT

    def _capture_screenshots(self, _dt):
        if self.schedule_label.texture_size[1]:
            self.schedule_label.height = self.schedule_label.texture_size[1]

        out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "screenshots")
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, f"care-companion-{datetime.now().strftime('%Y%m%d-%H%M%S')}.png")
        if self.root:
            self.root.export_to_png(path)
            print(f"Screenshot saved: {path}", flush=True)

    def check_reminders(self, dt):
        if self.active_reminder or self.demo_mode:
            return

        due = storage.get_due_reminders(self.reminder_configs)
        if due:
            self.active_reminder = due[0]
            self.reminder_message_label.text = self.active_reminder["text"]
            self.status_badge.set_status("active", "Due now")
            self.acknowledge_button.background_color = theme.ACCENT_ALERT

    def acknowledge_reminder(self, instance):
        if self.active_reminder:
            storage.mark_reminder_shown(self.active_reminder["id"])
            self.active_reminder = None
        self.reminder_message_label.text = self._waiting_message()
        self.status_badge.set_status("success", "Complete")
        self.acknowledge_button.background_color = theme.PRIMARY
        Clock.schedule_once(lambda _dt: self.status_badge.set_status("waiting", "Waiting"), 2)

    def show_week_history(self, instance):
        summary = storage.format_weekly_summary(days=7)
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))

        title = Label(
            text="Weekly Summary",
            font_size=dp(20),
            bold=True,
            color=theme.TEXT_PRIMARY,
            size_hint_y=None,
            height=dp(32),
        )
        scroll = ScrollView(size_hint=(1, 0.82))
        label = Label(
            text=summary,
            font_size=dp(15),
            color=theme.TEXT_PRIMARY,
            size_hint_y=None,
            halign="left",
            valign="top",
            line_height=1.4,
        )
        label.bind(texture_size=self._set_label_height)
        label.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0], None)))
        scroll.add_widget(label)

        close_btn = AccentButton(text="Close", accent_color=theme.PRIMARY_DARK, size_hint_y=None, height=dp(48))
        content.add_widget(title)
        content.add_widget(scroll)
        content.add_widget(close_btn)

        popup = Popup(
            title="",
            content=content,
            size_hint=(0.75, 0.65),
            separator_height=0,
            background_color=theme.SURFACE,
        )
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def play_song(self):
        audio_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "audio", "Rachel Platten - Fight Song.mp3")
        if os.path.isfile(audio_path):
            sound = SoundLoader.load(audio_path)
            if sound:
                sound.volume = 0.6
                sound.play()

    def log_sleep(self, instance):
        self.show_popup(
            f"Log {self.profile['user_name']}'s Sleep",
            f"How was {self.profile['user_name']}'s sleep last night? (1 = poor, 10 = excellent)",
            self.store_sleep,
        )

    def log_mood(self, instance):
        self.show_popup(
            f"Log {self.profile['user_name']}'s Mood",
            f"How is {self.profile['user_name']} feeling today? (1 = low, 10 = great)",
            self.evaluate_mood,
        )

    def show_popup(self, title, message, on_submit):
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))
        label = Label(
            text=message,
            font_size=dp(15),
            color=theme.TEXT_PRIMARY,
            size_hint_y=None,
            height=dp(48),
            halign="left",
            valign="middle",
        )
        label.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0], None)))
        text_input = TextInput(
            multiline=False,
            font_size=dp(20),
            input_filter="int",
            hint_text="1 – 10",
            size_hint_y=None,
            height=dp(48),
            padding=(dp(12), dp(12)),
        )

        popup = Popup(title=title, content=content, size_hint=(0.55, 0.42), auto_dismiss=True)

        def on_button_press(instance):
            on_submit(text_input.text)
            popup.dismiss()

        button = AccentButton(text="Save", accent_color=theme.PRIMARY, size_hint_y=None, height=dp(48))
        button.bind(on_press=on_button_press)

        content.add_widget(label)
        content.add_widget(text_input)
        content.add_widget(button)
        popup.open()

    def evaluate_mood(self, mood_value):
        try:
            mood = int(mood_value)
            if not 1 <= mood <= 10:
                raise ValueError

            storage.save_log("mood", mood)
            self.mood_status.text = f"Mood: {mood}/10 logged today"
            self.mood_status.color = theme.STATUS_SUCCESS

            if mood < 6:
                caregiver_name = self.profile.get("caregiver_name", "your caregiver")
                sent = self.send_sms_via_email(
                    "verizon",
                    personalization.personalize_message(
                        f"Mood rating is low: {mood}. Check in with {caregiver_name}.",
                        {**self.profile, "caregiver_name": caregiver_name},
                    ),
                    os.environ.get("HEALTH_APP_CAREGIVER_PHONE", ""),
                )
                if sent:
                    self.reminder_message_label.text = personalization.personalize_message(
                        "Mood {mood} saved. A message was sent to {caregiver_name}.",
                        {**self.profile, "mood": mood},
                    )
            elif mood < 8:
                self.reminder_message_label.text = personalization.personalize_message(
                    "Mood saved. {caregiver_name} would love to check in with you soon.",
                    self.profile,
                )
            else:
                self.reminder_message_label.text = personalization.personalize_message(
                    "Mood saved. I’m so glad you’re feeling brighter today, {user_name}.",
                    self.profile,
                )

        except ValueError:
            self.reminder_message_label.text = personalization.personalize_message(
                "{user_name}, please enter a whole number from 1 to 10 for your mood.",
                self.profile,
            )

    def store_sleep(self, sleep_value):
        try:
            sleep = int(sleep_value)
            if not 1 <= sleep <= 10:
                raise ValueError

            storage.save_log("sleep", sleep)
            self.sleep_status.text = f"Sleep: {sleep}/10 logged today"
            self.sleep_status.color = theme.STATUS_SUCCESS

            if sleep < 6:
                self.reminder_message_label.text = personalization.personalize_message(
                    "Sleep saved. {caregiver_name} can help you feel supported tonight.",
                    self.profile,
                )
            elif sleep < 8:
                self.reminder_message_label.text = personalization.personalize_message(
                    "Sleep saved. {user_name}, a little extra rest might help today.",
                    self.profile,
                )
            else:
                self.reminder_message_label.text = personalization.personalize_message(
                    "Sleep saved. That sounds like a restful night, {user_name}.",
                    self.profile,
                )

        except ValueError:
            self.reminder_message_label.text = personalization.personalize_message(
                "{user_name}, please enter a whole number from 1 to 10 for your sleep.",
                self.profile,
            )

    def send_sms_via_email(self, carrier, message, phone_number=""):
        carrier_gateways = {
            "verizon": "vtext.com",
            "att": "txt.att.net",
            "tmobile": "tmomail.net",
            "sprint": "messaging.sprintpcs.com",
        }

        if carrier not in carrier_gateways:
            print("Carrier not supported")
            self.reminder_message_label.text = personalization.personalize_message(
                f"Mood saved, but the note to {{caregiver_name}} could not be sent: carrier '{carrier}' not supported.",
                self.profile,
            )
            return False

        digits = "".join(ch for ch in phone_number if ch.isdigit())
        if len(digits) != 10:
            print(f"Invalid phone number: {phone_number}")
            self.reminder_message_label.text = personalization.personalize_message(
                "Mood saved, but the note to {caregiver_name} could not be sent: caregiver phone not configured.",
                self.profile,
            )
            return False

        to_email = f"{digits}@{carrier_gateways[carrier]}"
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = os.environ.get("HEALTH_APP_EMAIL", "")
        sender_password = os.environ.get("HEALTH_APP_PASSWORD", "")

        if not sender_email or not sender_password:
            print("HEALTH_APP_EMAIL / HEALTH_APP_PASSWORD not set; cannot send SMS.")
            self.reminder_message_label.text = personalization.personalize_message(
                "Mood saved, but the note to {caregiver_name} could not be sent: email credentials not configured.",
                self.profile,
            )
            return False

        msg = MIMEText(message)
        msg["From"] = sender_email
        msg["To"] = to_email
        msg["Subject"] = "Health Reminder"

        try:
            with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, [to_email], msg.as_string())
            print("SMS sent successfully")
            return True
        except Exception as e:
            print(f"Failed to send SMS: {e}")
            self.reminder_message_label.text = personalization.personalize_message(
                f"Mood saved, but the note to {{caregiver_name}} failed: {e}",
                self.profile,
            )
            return False


def parse_args():
    parser = argparse.ArgumentParser(description="Care Companion health reminder app")
    parser.add_argument("--demo", action="store_true", help="Show demo state with sample reminder and history")
    parser.add_argument("--screenshot", action="store_true", help="Auto-save a screenshot after launch")
    parser.add_argument("--no-audio", action="store_true", help="Skip startup audio")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    HealthReminderApp(
        demo_mode=args.demo,
        screenshot_mode=args.screenshot,
        no_audio=args.no_audio,
    ).run()
