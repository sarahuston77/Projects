import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

import personalization
import reminders
import storage


class HealthReminderApp(App):
    def build(self):
        storage.init_db()
        self.profile = personalization.load_profile()
        self.reminder_configs = self._load_reminder_configs()
        self.active_reminder = None

        main_layout = BoxLayout(orientation='horizontal', padding=30, spacing=25)

        self.left_layout = BoxLayout(orientation='vertical', padding=20, spacing=20, size_hint=(0.66, 1))
        self.right_layout = BoxLayout(orientation='vertical', padding=20, spacing=20, size_hint=(0.33, 1))

        with self.left_layout.canvas.before:
            Color(0.9, 0.9, 0.9, 1)
            self.left_rect = Rectangle(size=self.left_layout.size, pos=self.left_layout.pos)
        self.left_layout.bind(size=self.update_background_rect, pos=self.update_background_rect)

        with self.right_layout.canvas.before:
            Color(0.8, 0.9, 1, 1)
            self.right_rect = Rectangle(size=self.right_layout.size, pos=self.right_layout.pos)
        self.right_layout.bind(size=self.update_right_background_rect, pos=self.update_right_background_rect)

        self.title_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.3), padding=(20, 20))

        self.left_icon = Image(
            source='assets/images/dog-training.png',
            size_hint=(0.1, 1),
            allow_stretch=True,
            keep_ratio=True,
        )

        self.title_label = Label(
            text=f"{self.profile['user_name']}'s Care Companion",
            font_size=48,
            font_name="Arial",
            color=(1, 1, 1, 1),
            size_hint=(0.8, 1),
            bold=True,
            halign="center",
            valign="middle",
            padding=(20, 20),
        )

        self.right_icon = Image(
            source='assets/images/dog-training.png',
            size_hint=(0.1, 1),
            allow_stretch=True,
            keep_ratio=True,
        )

        self.title_layout.add_widget(self.left_icon)
        self.title_layout.add_widget(self.title_label)
        self.title_layout.add_widget(self.right_icon)

        with self.title_layout.canvas.before:
            Color(0.1, 0.6, 0.8, 1)
            self.title_rect = Rectangle(size=self.title_layout.size, pos=self.title_layout.pos)
        self.title_layout.bind(size=self.update_title_background_rect, pos=self.update_title_background_rect)

        Window.clearcolor = (1.0, 0.5451, 0.2392, 1.0)

        label_style = {'font_size': 22, 'color': (0.1, 0.1, 0.5, 1)}
        button_style = {
            'size_hint': (1, 0.35),
            'background_color': (0.2, 0.6, 0.8, 1),
            'font_size': 20,
            'color': (1, 1, 1, 1),
        }

        self.reminder_message_label = Label(
            text=self._waiting_message(),
            font_size=22,
            halign="left",
            valign="top",
        )
        self.reminder_message_label.bind(size=self._update_reminder_text_size)

        self.acknowledge_button = Button(text="Acknowledge", **button_style)
        self.acknowledge_button.bind(on_press=self.acknowledge_reminder)

        self.sleep_label = Label(text=f"How did {self.profile['user_name']} sleep? (1-10)", **label_style)
        self.sleep_button = Button(text="Log Sleep", **button_style)
        self.sleep_button.bind(on_press=self.log_sleep)

        self.mood_label = Label(text=f"How is {self.profile['user_name']} feeling today? (1-10)", **label_style)
        self.mood_button = Button(text="Log Mood", **button_style)
        self.mood_button.bind(on_press=self.log_mood)

        self.history_button = Button(text="View This Week", **button_style)
        self.history_button.bind(on_press=self.show_week_history)

        self.left_layout.add_widget(self.sleep_label)
        self.left_layout.add_widget(self.sleep_button)
        self.left_layout.add_widget(self.mood_label)
        self.left_layout.add_widget(self.mood_button)
        self.left_layout.add_widget(self.history_button)

        self.right_layout.add_widget(self.reminder_message_label)
        self.right_layout.add_widget(self.acknowledge_button)

        main_layout.add_widget(self.left_layout)
        main_layout.add_widget(self.right_layout)

        self.play_song()
        Clock.schedule_interval(self.check_reminders, 30)

        final_layout = BoxLayout(orientation='vertical')
        final_layout.add_widget(self.title_layout)
        final_layout.add_widget(main_layout)

        Window.bind(on_resize=self.update_font_sizes)
        self.update_font_sizes(Window, Window.width, Window.height)
        return final_layout

    def _load_reminder_configs(self):
        try:
            return reminders.load_reminders()
        except (OSError, ValueError, KeyError) as e:
            print(f"Could not load reminders.json, using defaults: {e}")
            return reminders.build_fallback_reminders()

    def _waiting_message(self):
        next_times = ", ".join(r["time"] for r in self.reminder_configs[:3])
        if len(self.reminder_configs) > 3:
            next_times += ", ..."
        greeting = personalization.build_greeting(self.profile)
        return (
            f"{greeting}\n"
            f"Reminders are here for you today.\n"
            f"Today: {next_times}\n\n"
            "Tap Acknowledge when you see a reminder."
        )

    def _update_reminder_text_size(self, instance, value):
        instance.text_size = (value[0], None)

    def update_font_sizes(self, window, width, height):
        base_font_size = width * 0.03
        self.title_label.font_size = base_font_size * 1.5
        self.reminder_message_label.font_size = base_font_size * 0.5
        self.sleep_label.font_size = base_font_size
        self.mood_label.font_size = base_font_size
        self.acknowledge_button.font_size = base_font_size
        self.sleep_button.font_size = base_font_size
        self.mood_button.font_size = base_font_size
        self.history_button.font_size = base_font_size

    def update_background_rect(self, *args):
        self.left_rect.pos = self.left_layout.pos
        self.left_rect.size = self.left_layout.size

    def update_right_background_rect(self, *args):
        self.right_rect.pos = self.right_layout.pos
        self.right_rect.size = self.right_layout.size

    def update_title_background_rect(self, *args):
        self.title_rect.pos = self.title_layout.pos
        self.title_rect.size = self.title_layout.size

    def check_reminders(self, dt):
        if self.active_reminder:
            return

        due = storage.get_due_reminders(self.reminder_configs)
        if due:
            self.active_reminder = due[0]
            self.reminder_message_label.text = self.active_reminder["text"]

    def acknowledge_reminder(self, instance):
        if self.active_reminder:
            storage.mark_reminder_shown(self.active_reminder["id"])
            self.active_reminder = None
        self.reminder_message_label.text = self._waiting_message()

    def show_week_history(self, instance):
        summary = storage.format_weekly_summary(days=7)
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        scroll = ScrollView(size_hint=(1, 0.85))
        label = Label(
            text=summary,
            size_hint_y=None,
            halign="left",
            valign="top",
        )
        label.bind(texture_size=self._set_label_height)
        label.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0], None)))
        scroll.add_widget(label)

        close_btn = Button(text="Close", size_hint=(1, 0.15))
        content.add_widget(scroll)
        content.add_widget(close_btn)

        popup = Popup(title="This Week", content=content, size_hint=(0.85, 0.7), auto_dismiss=True)
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def _set_label_height(self, instance, texture_size):
        instance.height = texture_size[1]

    def play_song(self):
        sound = SoundLoader.load('assets/audio/Rachel Platten - Fight Song.mp3')
        if sound:
            sound.volume = 1.0
            sound.play()

    def log_sleep(self, instance):
        self.show_popup(
            f"Log {self.profile['user_name']}'s Sleep",
            f"Enter {self.profile['user_name']}'s sleep rating (1-10):",
            self.store_sleep,
        )

    def log_mood(self, instance):
        self.show_popup(
            f"Log {self.profile['user_name']}'s Mood",
            f"Enter {self.profile['user_name']}'s mood rating (1-10):",
            self.evaluate_mood,
        )

    def show_popup(self, title, message, on_submit):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        label = Label(text=message, size_hint=(1, 0.6))
        text_input = TextInput(multiline=False, size_hint=(1, 0.4))

        popup = Popup(title=title, content=content, size_hint=(0.8, 0.5), auto_dismiss=True)

        def on_button_press(instance):
            on_submit(text_input.text)
            popup.dismiss()

        button = Button(text="Submit", size_hint=(1, 0.3))
        button.bind(on_press=on_button_press)

        content.add_widget(label)
        content.add_widget(text_input)
        content.add_widget(button)
        popup.open()

    def revert_mood_label(self, dt):
        self.mood_label.text = f"How is {self.profile['user_name']} feeling today? (1-10)"

    def evaluate_mood(self, mood_value):
        try:
            mood = int(mood_value)
            if not 1 <= mood <= 10:
                raise ValueError

            storage.save_log("mood", mood)
            self.mood_label.text = f"Logged Mood: {mood} (saved)"
            Clock.schedule_once(self.revert_mood_label, 2)

            if mood < 6:
                caregiver_name = self.profile.get("caregiver_name", "your caregiver")
                sent = self.send_sms_via_email(
                    'verizon',
                    personalization.personalize_message(
                        f"Mood rating is low: {mood}. Check in with {caregiver_name}.",
                        {**self.profile, "caregiver_name": caregiver_name},
                    ),
                    os.environ.get('HEALTH_APP_CAREGIVER_PHONE', ''),
                )
                if sent:
                    self.reminder_message_label.text = personalization.personalize_message(
                        "Mood {mood}: saved and a message was sent to {caregiver_name}.",
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

    def revert_sleep_label(self, dt):
        self.sleep_label.text = f"How did {self.profile['user_name']} sleep? (1-10)"

    def store_sleep(self, sleep_value):
        try:
            sleep = int(sleep_value)
            if not 1 <= sleep <= 10:
                raise ValueError

            storage.save_log("sleep", sleep)
            self.sleep_label.text = f"Logged Sleep: {sleep} (saved)"
            Clock.schedule_once(self.revert_sleep_label, 2)

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
            'verizon': 'vtext.com',
            'att': 'txt.att.net',
            'tmobile': 'tmomail.net',
            'sprint': 'messaging.sprintpcs.com',
        }

        if carrier not in carrier_gateways:
            print("Carrier not supported")
            self.reminder_message_label.text = personalization.personalize_message(
                f"Mood saved, but the note to {{caregiver_name}} could not be sent: carrier '{carrier}' not supported.",
                self.profile,
            )
            return

        digits = ''.join(ch for ch in phone_number if ch.isdigit())
        if len(digits) != 10:
            print(f"Invalid phone number: {phone_number}")
            self.reminder_message_label.text = personalization.personalize_message(
                "Mood saved, but the note to {caregiver_name} could not be sent: caregiver phone not configured.",
                self.profile,
            )
            return

        to_email = f"{digits}@{carrier_gateways[carrier]}"
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        sender_email = os.environ.get('HEALTH_APP_EMAIL', '')
        sender_password = os.environ.get('HEALTH_APP_PASSWORD', '')

        if not sender_email or not sender_password:
            print("HEALTH_APP_EMAIL / HEALTH_APP_PASSWORD not set; cannot send SMS.")
            self.reminder_message_label.text = personalization.personalize_message(
                "Mood saved, but the note to {caregiver_name} could not be sent: email credentials not configured.",
                self.profile,
            )
            return

        msg = MIMEText(message)
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = 'Health Reminder'

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


if __name__ == "__main__":
    HealthReminderApp().run()
