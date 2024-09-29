#lqzg mxac zcum qxwj
import smtplib
from email.mime.text import MIMEText
from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.core.image import Image
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.uix.popup import Popup
from datetime import datetime, timedelta
from kivy.uix.image import Image

class HealthReminderApp(App):
    ### App for my mom to help her with health reminders
    def build(self):
        # Main layout with horizontal orientation (2/3 widgets, 1/3 messages)
        main_layout = BoxLayout(orientation='horizontal', padding=30, spacing=25)

        # Left layout (2/3 of the screen) for interactive widgets
        self.left_layout = BoxLayout(orientation='vertical', padding=20, spacing=20, size_hint=(0.66, 1))

        # Right layout (1/3 of the screen) for messages
        self.right_layout = BoxLayout(orientation='vertical', padding=20, spacing=20, size_hint=(0.33, 1))

        # Set background color using canvas.before for left layout
        with self.left_layout.canvas.before:
            Color(0.9, 0.9, 0.9, 1)  # Set light grey background (RGBA format)
            self.left_rect = Rectangle(size=self.left_layout.size, pos=self.left_layout.pos)

        # Ensure the background adjusts when the layout size changes
        self.left_layout.bind(size=self.update_background_rect, pos=self.update_background_rect)

        with self.right_layout.canvas.before:
            Color(0.8, 0.9, 1, 1)  # Set light blue background (RGBA format)
            self.right_rect = Rectangle(size=self.right_layout.size, pos=self.right_layout.pos)

        # Ensure the background adjusts when the layout size changes
        self.right_layout.bind(size=self.update_right_background_rect, pos=self.update_right_background_rect)

        # Create a horizontal layout for the title and icons
        self.title_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.3), padding=(20, 20))

        # Left icon (Image) to the left of the title
        self.left_icon = Image(
            source='assets/images/dog-training.png',  # Path to the left icon PNG file
            size_hint=(0.1, 1),  # Adjust size hint (10% of width)
            allow_stretch=True,  # Stretch the image to fit the space
            keep_ratio=True  # Keep the aspect ratio
        )

        # Title label (centered between the icons)
        self.title_label = Label(
            text="Health Reminder App",
            font_size=48,
            font_name="Arial",
            color=(1, 1, 1, 1),
            size_hint=(0.8, 1),  # Title takes up 80% of width
            bold=True,
            halign="center",
            valign="middle",
            padding=(20, 20)
        )

        # Right icon (Image) to the right of the title
        self.right_icon = Image(
            source='assets/images/dog-training.png',  # Path to the right icon PNG file
            size_hint=(0.1, 1),  # Adjust size hint (10% of width)
            allow_stretch=True,
            keep_ratio=True
        )

        # Add the left icon, title, and right icon to the layout
        self.title_layout.add_widget(self.left_icon)
        self.title_layout.add_widget(self.title_label)
        self.title_layout.add_widget(self.right_icon)

        # Set background color using canvas.before for the title layout
        with self.title_layout.canvas.before:
            Color(0.1, 0.6, 0.8, 1)  # Set a nice blue background color (RGBA format)
            self.title_rect = Rectangle(size=self.title_layout.size, pos=self.title_layout.pos)

        # Ensure the background adjusts when the layout size changes
        self.title_layout.bind(size=self.update_title_background_rect, pos=self.update_title_background_rect)

        Window.clearcolor = (1.0, 0.5451, 0.2392, 1.0)

        # Label and button styling for the left layout
        label_style = {'font_size': 22, 'color': (0.1, 0.1, 0.5, 1)}
        button_style = {
            'size_hint': (1, 0.4),
            'background_color': (0.2, 0.6, 0.8, 1),
            'font_size': 20,
            'color': (1, 1, 1, 1)
        }

        # Reminder label (for the right layout)
        self.reminder_message_label = Label(
            text="Drink plenty of water to flush your bladder.\nGo get Starbucks water since it’s your fav",
            width=50,  # Set a specific width for the label
            font_size=22
        )

        # Acknowledge button
        self.acknowledge_button = Button(text="Acknowledge", **button_style)
        self.acknowledge_button.bind(on_press=self.acknowledge_reminder)

        self.sleep_label = Label(text="Log your Sleep (1-10):", **label_style)
        self.sleep_button = Button(text="Log Sleep", **button_style)
        self.sleep_button.bind(on_press=self.log_sleep)

        self.mood_label = Label(text="Log your Mood (1-10):", **label_style)
        self.mood_button = Button(text="Log Mood", **button_style)
        self.mood_button.bind(on_press=self.log_mood)

        # Add widgets to the left layout
        self.left_layout.add_widget(self.sleep_label)
        self.left_layout.add_widget(self.sleep_button)
        self.left_layout.add_widget(self.mood_label)
        self.left_layout.add_widget(self.mood_button)

        # Add the message label to the right layout
        self.right_layout.add_widget(self.reminder_message_label)
        self.right_layout.add_widget(self.acknowledge_button)
        # Add both left and right layouts to the main layout
        main_layout.add_widget(self.left_layout)
        main_layout.add_widget(self.right_layout)

        # Bladder cancer-related reminders
        self.reminders = [
            {"text": "Drink plenty of water to flush your bladder.\nGo get Starbucks water since it’s your fav",
             "time": datetime.now() + timedelta(seconds=10)},
            {"text": "Avoid spicy foods (Like Papa Joes pasta meal)\nto reduce bladder irritation.",
             "time": datetime.now() + timedelta(seconds=30)},
            {"text": "Check if your follow-up appointment\nis scheduled (every 6 weeks!!!!).",
             "time": datetime.now() + timedelta(seconds=60)},
            {"text": "Limit caffeine intake to prevent\nbladder irritation. You don't want\nto be awake anyways. Hahahh",
             "time": datetime.now() + timedelta(seconds=90)},
            {"text": "Consider getting a healthy dinner with Sara :)\nto support bladder health.",
             "time": datetime.now() + timedelta(seconds=120)}, ]

        self.active_reminder = None

        self.play_song()
        self.current_reminder_index = 0
        Clock.schedule_interval(self.check_reminders, 1)

        final_layout = BoxLayout(orientation='vertical')
        final_layout.add_widget(self.title_layout)
        final_layout.add_widget(main_layout)

        Window.bind(on_resize=self.update_font_sizes)
        self.update_font_sizes(Window, Window.width, Window.height)
        return final_layout

    def update_font_sizes(self, window, width, height):
        base_font_size = width * 0.03

        self.title_label.font_size = base_font_size * 1.5

        self.reminder_message_label.font_size = base_font_size * 0.5
        self.sleep_label.font_size = base_font_size
        self.mood_label.font_size = base_font_size
        self.acknowledge_button.font_size = base_font_size
        self.sleep_button.font_size = base_font_size
        self.mood_button.font_size = base_font_size


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
        """Check for active reminders and show them if the time has passed"""
        now = datetime.now()
        if not self.active_reminder:
            reminder = self.reminders[self.current_reminder_index]
            if now >= reminder["time"]:
                self.active_reminder = reminder
                self.reminder_message_label.text = reminder["text"]


    def acknowledge_reminder(self, instance):
        if self.active_reminder:
            self.active_reminder = None

        self.current_reminder_index += 1

        if self.current_reminder_index >= len(self.reminders):
            self.current_reminder_index = 0

        next_reminder = self.reminders[self.current_reminder_index]
        self.reminder_message_label.text = next_reminder["text"]

    def play_song(self):
        sound = SoundLoader.load('assets/audio/Rachel Platten - Fight Song.mp3')
        if sound:
            print("Sound loaded successfully!")
            sound.volume = 1.0
            sound.play()
        else:
            print("Failed to load sound.")


    def log_sleep(self, instance):
        self.show_popup("Log Sleep", "Enter your sleep rating (1-10):", self.store_sleep)


    def log_mood(self, instance):
        self.show_popup("Log Mood", "Enter your mood rating (1-10):", self.evaluate_mood)


    def show_popup(self, title, message, on_submit):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        label = Label(text=message, size_hint=(1, 0.6))
        text_input = TextInput(multiline=False, size_hint=(1, 0.4))

        def on_button_press(instance):
            user_input = text_input.text
            on_submit(user_input)
            popup.dismiss()

        button = Button(text="Submit", size_hint=(1, 0.3))
        button.bind(on_press=on_button_press)

        content.add_widget(label)
        content.add_widget(text_input)
        content.add_widget(button)

        popup = Popup(title=title, content=content, size_hint=(0.8, 0.5), auto_dismiss=True)
        popup.open()


    def revert_mood_label(self, dt):
        self.mood_label.text = "Log your Mood (1-10):"


    def evaluate_mood(self, mood_value):
        try:
            mood = int(mood_value)
            self.mood_label.text = f"Logged Mood: {mood}"
            Clock.schedule_once(self.revert_mood_label, 2)

            if mood < 8:
                self.reminder_message_label.text = "You should call your daughter she'd love to spend time with you"
            if mood < 6:
                self.send_sms_via_email('verizon', f"Mood rating is low: {mood}. Check in with her.", "248-318-8361")
                self.reminder_message_label.text = f"Mood {mood}: Message sent to Sara"
            else:
                self.reminder_message_label.text = "I'm happy you're in a good mood"

        except ValueError:
            self.reminder_message_label.text = "Invalid mood rating. Please enter a number."


    def revert_sleep_label(self, dt):
        self.sleep_label.text = "Log your Mood (1-10):"

    def store_sleep(self, sleep_value):
        try:
            sleep = int(sleep_value)

            if sleep < 6:
                self.reminder_message_label.text = "Call Sara, she might be able to help you sleep"
            elif sleep < 8:
                self.reminder_message_label.text = "You might need more rest!\nConsider improving your sleep routine."
            else:
                self.reminder_message_label.text = "Great! Keep up the good sleep habits!"

            self.sleep_label.text = f"Logged Sleep: {sleep}"

        except ValueError:
            self.reminder_message_label.text = "Invalid sleep rating. Please enter a number."


    def send_sms_via_email(self, carrier, message, phone_number="248-318-8361"):
        carrier_gateways = {
            'verizon': 'vtext.com',
            'att': 'txt.att.net',
            'tmobile': 'tmomail.net',
            'sprint': 'messaging.sprintpcs.com'
        }

        if carrier not in carrier_gateways:
            print("Carrier not supported")
            return

        to_email = 'khuston@hotmail.com'

        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        sender_email = 'shuston007@gmail.com'
        sender_password = 'lqzg mxac zcum qxwj'

        msg = MIMEText(message)
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = 'Health Reminder'

        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, [to_email], msg.as_string())
            server.quit()
            print("SMS sent successfully")
        except Exception as e:
            print(f"Failed to send SMS: {e}")


if __name__ == "__main__":
    HealthReminderApp().run()