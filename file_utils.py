import os
import stat

def set_file_read_only(file_path: str):
    current_permissions = os.stat(file_path).st_mode
    os.chmod(file_path, current_permissions & ~stat.S_IWUSR)
