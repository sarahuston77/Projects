"""Will have a health score for kathy and send her automatic reminders."""

import smtplib
from email.mime.text import MIMEText

sender_email: str = "shuston007@gmail.com"
password: str = "Soccerrules7"
server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login(sender_email, password)

class Health:

    water: int
    sleep: str
    mental_health: str
    manifest_score: int

    def __init__(self, water: int = 1, sleep: int = 1, mental_health: int = 1, manifest_score: int = 1):
        """Initilize the class of mother's health with four attributes."""
        self.water = water
        self.sleep = sleep
        self.mental_health = mental_health
        self.manifest_score = manifest_score
    





