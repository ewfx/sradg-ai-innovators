
import pytest
from unittest.mock import patch, MagicMock
from anomaly_detection.modules.email_notification import EmailNotification

@patch("smtplib.SMTP")
def test_send_email_without_attachment(mock_smtp):
    smtp_instance = MagicMock()
    mock_smtp.return_value = smtp_instance

    EmailNotification.send_email(
        subject="Test Email",
        body="This is a test email body",
        recipient="recipient@example.com",
        attachment=None
    )

    smtp_instance.starttls.assert_called_once()
    smtp_instance.login.assert_called_once()
    smtp_instance.send_message.assert_called_once()
    smtp_instance.quit.assert_called_once()

@patch("smtplib.SMTP")
def test_send_email_with_missing_attachment(mock_smtp):
    smtp_instance = MagicMock()
    mock_smtp.return_value = smtp_instance

    # Intentionally passing non-existent attachment
    EmailNotification.send_email(
        subject="Test with Missing Attachment",
        body="Should handle missing file gracefully.",
        recipient="recipient@example.com",
        attachment="non_existent_file.csv"
    )

    smtp_instance.starttls.assert_called_once()
    smtp_instance.login.assert_called_once()
    smtp_instance.send_message.assert_called_once()
    smtp_instance.quit.assert_called_once()
