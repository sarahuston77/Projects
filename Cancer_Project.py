from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from datetime import datetime, timedelta

class HealthReminderApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        self.reminder_label = Label(text="No reminders yet.")
        self.acknowledge_button = Button(text="Acknowledge", size_hint=(1, 0.2))
        self.acknowledge_button.bind(on_press=self.acknowledge_reminder)
        
        self.layout.add_widget(self.reminder_label)
        self.layout.add_widget(self.acknowledge_button)
        
        self.reminders = [
            {"text": "Drink water", "time": datetime.now() + timedelta(seconds=10)},
            {"text": "Take medication", "time": datetime.now() + timedelta(seconds=30)},
            {"text": "Schedule follow-up appointment", "time": datetime.now() + timedelta(seconds=60)}
        ]
        
        Clock.schedule_interval(self.check_reminders, 1)
        return self.layout

    def check_reminders(self, dt):
        now = datetime.now()
        for reminder in self.reminders:
            if now >= reminder["time"]:
                self.reminder_label.text = reminder["text"]
                self.reminders.remove(reminder)
                break

    def acknowledge_reminder(self, instance):
        self.reminder_label.text = "Reminder acknowledged."

if __name__ == "__main__":
    HealthReminderApp().run()
