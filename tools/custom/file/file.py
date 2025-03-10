import mimetypes
import os

def file_command(filename):
    if not os.path.exists(filename):
        return f"{filename}: No such file or directory"

    mime_type, _ = mimetypes.guess_type(filename)
    return f"{filename}: {mime_type or 'Unknown MIME type'}"

# print(file_command("example.txt"))
