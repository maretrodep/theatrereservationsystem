import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def email_send(email_list, subject, content):
    sender_email = "email@example.com"
    sender_password = "123"
    # Gmail SMTP server details
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    try:
        # Connect to the Gmail SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Start TLS encryption
        server.login(sender_email, sender_password)  # Log in to Gmail

        # Iterate over each recipient and send the email
        for recipient in email_list:
            # Create the email
            message = MIMEMultipart()
            message['From'] = sender_email
            message['To'] = recipient
            message['Subject'] = subject

            # Attach the email body content
            message.attach(MIMEText(content, 'plain'))

            # Send the email
            server.sendmail(sender_email, recipient, message.as_string())

        print("Emails sent successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        server.quit()
        pass
