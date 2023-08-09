import smtplib, ssl
import os

port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "allan@mombo.africa"  # Enter your address
receiver_email = "mwaranguallan345@gmail.com"  # Enter receiver address
password = os.environ["EMAIL_PASS"]  # input("Type your password and press enter: ")
message = """\
Subject: Hi there

This message is sent from Python."""

context = ssl.create_default_context()
with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)
