import os
import smtplib
import dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EmailServer:

    def __init__(self,
                 username,
                 password):
        self.username = username
        self.password = password
        self.conn = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        self.conn.login(username, password)


class Email:

    def __init__(self,
                 sender,
                 subject,
                 body,
                 to_email):
        self.sender = sender
        self.subject = subject
        self.body = body
        self.to_email = to_email

    def covert(self):
        msg = MIMEMultipart()
        msg['From'] = self.sender
        msg['To'] = self.to_email
        msg['Subject'] = self.subject
        msg.attach(MIMEText(self.body, 'plain'))
        return msg.as_string()


class EmailNotifier:

    def __init__(self,
                 username,
                 password):
        self.server = EmailServer(username, password)

    def send_email(self,
                   subject,
                   body):
        to_email = self.server.username
        email = Email(self.server.username, subject, body, to_email)
        text = email.covert()
        self.server.conn.sendmail(self.server.username, to_email, text)
        print(f'Sent email {subject} to {to_email}')


if __name__ == '__main__':
    dotenv.load_dotenv()
    email_notifier = EmailNotifier(os.getenv('GMAIL_USER'), os.getenv('GMAIL_APP_PASS'))
    email_notifier.send_email(
        'Test Subject',
        'This is the body of the email', )
