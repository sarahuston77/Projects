from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from datetime import datetime, timedelta

class HealthReminderApp(App):
    ### App for my mom to help her with health reminders
    def build(self):
        self.layout = BoxLayout(orientation='vertical')

        self.reminder_label = Label(text="No reminders yet.")
        self.acknowledge_button = Button(text="Acknowledge", size_hint=(1, 10))
        self.acknowledge_button.bind(on_press=self.acknowledge_reminder)
        self.sleep_label = Label(text="Sleep (1-10):")
        self.sleep_button = Button(text="Log Sleep", size_hint=(1, 0.5))
        self.sleep_button.bind(on_press=self.log_sleep)
        self.mood_label = Label(text ="Mood  (1-10):")
        self.mood_button = Button(text="Log Mood", size_hint=(1, 0.5))
        self.mood_button.bind(on_press=self.log_mood)
        self.layout.add_widget(self.reminder_label)
        self.layout.add_widget(self.acknowledge_button)
        self.layout.add_widget(self.sleep_label)
        self.layout.add_widget(self.sleep_button)
        self.layout.add_widget(self.mood_label)
        self.layout.add_widget(self.mood_button)

        # Bladder cancer-related reminders with personalized notes
        self.reminders = [{"text": "Drink plenty of water to flush your bladder.\nGo get Starbucks water since it’s your fav", "time": datetime.now() + timedelta(seconds=10)},{"text": "Avoid spicy foods (Like Papa Joes pasta meal) to reduce bladder irritation.", "time": datetime.now() + timedelta(seconds=30)},{"text": "Check if your follow-up appointment is scheduled (every 6 weeks!!!!).", "time": datetime.now() + timedelta(seconds=60)},{"text": "Limit caffeine intake to prevent bladder irritation. You don't want to be awake anyways. Hahahh", "time": datetime.now() + timedelta(seconds=90)},{"text": "Consider a getting a healthy dinner with Sara :) to support bladder health.", "time": datetime.now() + timedelta(seconds=120)},]

        self.active_reminder = None
        self.reminder_shown_time = None

        Clock.schedule_interval(self.check_reminders, 1)
        return self.layout
    def check_reminders(self, dt):
        now = datetime.now()
        if not self.active_reminder:  
            for reminder in self.reminders:
                if now >= reminder["time"]:
                    self.active_reminder = reminder
                    self.reminder_shown_time = now
                    self.reminder_label.text = reminder["text"]
                    break

    def acknowledge_reminder(self, instance):
        if self.active_reminder:
            # Mark the reminder as acknowledged and reset
            self.active_reminder = None
            self.reminder_label.text = "Done"


    def send_text_to_sara(self, instance):
        self.reminder_label.text = "Text to Sara sent: 'Let’s get din'"

    def play_song(self, instance):
        sound = SoundLoader.load('//Users//downloads//Fight_Song.mp3')
        if sound:
            sound.play()

    def show_smiley(self, instance):
        self.layout.clear_widgets()
        smiley_image = Image(source='//Users//downloads//Screenshot 2022-09-17 at 10.44.28 AM')
        self.layout.add_widget(smiley_image)


    def log_sleep(self, instance):
         # Maybe do a total hours and aggregate across the weeks that will prompt me to scold her tbh
        
    def log_mood(self, instance):
        # A 1 or 0 score that will prompt me to check in on her? or do something nice? Ask syd

if __name__ == "__main__":
    HealthReminderApp().run()
