import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import yaml

# Load configuration (ensure this is done only once)
try:
    with open('config/config.yaml') as file:
        config = yaml.safe_load(file)
except FileNotFoundError:
    print("Error: config.yaml file not found. Using default configurations.")
    config = {
        'paths': {'data_file': 'data/generated_reconciliation_data.csv', 'anomaly_output': 'data/detected_anomalies_{timestamp}.csv'},
        'data_validation': {'quantity_threshold': 10},
        'api_keys': {'openai': 'YOUR_OPENAI_API_KEY'},
        'email': {'sender': 'your_email@gmail.com', 'password': 'your_password', 'recipient': 'recipient@example.com'},
    }

class EmailNotification:
    @staticmethod
    def send_email(subject, body, recipient, attachment):
        """
        Sends an email notification.

        Args:
            subject (str): Email subject.
            body (str): Email body.
            recipient (str): Recipient email address.
            attachment (str, optional): Path to an attachment file.
        """
        try:
            message = MIMEMultipart()
            message['From'] = config['email']['sender']
            message['To'] = recipient
            message['Subject'] = subject
            message.attach(MIMEText(body, 'plain'))
            if attachment:
                with open(attachment, 'rb') as file:
                    mime = MIMEBase('application', 'octet-stream')
                    mime.set_payload(file.read())
                    encoders.encode_base64(mime)
                    mime.add_header('Content-Disposition', f'attachment; filename={attachment}')
                    message.attach(mime)
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(config['email']['sender'], config['email']['password'])
            server.send_message(message)
            server.quit()
            logging.info({"message": "Email sent.", "recipient": recipient})
        except smtplib.SMTPException as e:
            logging.error({"message": "Error sending email.", "error": str(e)})
        except FileNotFoundError:
            logging.error({"message": "Attachment file not found."})
        except Exception as e:
            logging.error({"message": "Error during email sending.", "error": str(e)})