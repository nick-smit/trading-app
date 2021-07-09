import smtplib, ssl
import config
from helpers import log
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def sendMail(subject, message, html=False):
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(config.smtp_host, config.smtp_port, context=context) as server:
        try:
            server.login(config.smtp_username, config.smtp_password)
        except Exception as e:
            log("Got exception while trying to login to the smtp server: {}".format(e))

        body = ""
        if not html:
            body = "Subject: {}\n\n{}".format(subject, message)
        else:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['To'] = config.notification_email_to
            msg['From'] = config.notification_email_from
            msg.attach(MIMEText(message, 'html'))
            body = msg.as_string()

        log("Sending email to {}".format(config.notification_email_to))

        try:
            server.sendmail(config.notification_email_from, config.notification_email_to, body)
        except Exception as e:
            log("Got exception while trying to send an email: {}".format(e))

        server.quit()

if __name__ == '__main__':
    sendMail('This is a test', 'This is a test')
