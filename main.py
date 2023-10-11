import os
from mega import Mega


def find_files_under_size(folder_path, max_size_bytes, allowed_extensions):
    """Find files under the specified size in bytes and with allowed extensions in the specified folder."""
    found_files = []
    try:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                if file.lower().endswith(allowed_extensions) and os.path.getsize(file_path) < max_size_bytes:
                    found_files.append(file_path)
    except Exception as e:
        print(f"An error occurred while searching for files: {e}")
    return found_files


def mega_login(email, password):
    """Login to Mega using the provided email and password."""
    try:
        mega = Mega()
        mega.login(email, password)
        return mega
    except Exception as e:
        print(f"An error occurred during Mega login: {e}")
        return None


def upload_files_to_mega(mega, file_paths, target_folder_h):
    """Upload files to the specified Mega folder."""
    try:
        for file_path in file_paths:
            mega.upload(file_path, target_folder_h)
        print("Files uploaded to Mega successfully.")
    except Exception as e:
        print(f"An error occurred during file upload to Mega: {e}")


def main():
    main_folder = input("Enter the path to the main folder: ")

    try:
        max_file_size = int(input("Enter the maximum file size in megabytes: ")) * 1024 * 1024
    except ValueError:
        print("Invalid input for file size. Please enter a valid number.")
        return

    # Find files under the specified size and extensions
    allowed_extensions = ('.docx', '.doc', '.pdf')
    found_files_list = find_files_under_size(main_folder, max_file_size, allowed_extensions)

    print("Files found:")
    for found_file in found_files_list:
        print(f"- {found_file}")

    # Login to Mega
    email = input("Enter your Mega email: ")
    password = input("Enter your Mega password: ")
    mega = mega_login(email, password)
    if mega is None:
        return

    # Specify the target Mega folder ('your_folder' placeholder)
    target_folder_name = 'your_folder'
    folders = mega.get_folders()
    target_folder = None
    for folder in folders:
        if folder['name'] == target_folder_name:
            target_folder = folder
            break

    if target_folder is None:
        print(f"Mega folder '{target_folder_name}' not found.")
        return

    # Upload files to the specified Mega folder
    upload_files_to_mega(mega, found_files_list, target_folder['h'])


if __name__ == "__main__":
    main()
