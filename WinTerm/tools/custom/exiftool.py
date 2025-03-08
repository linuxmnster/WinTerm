import os
import sys
import pyfiglet
from PIL import Image
from PIL.ExifTags import TAGS
from PyPDF2 import PdfReader

def extract_image_metadata(file_path):
    try:
        image = Image.open(file_path)
        exif_data = image._getexif()
        if exif_data:
            print("\n📸 Image Metadata:")
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                print(f"{tag}: {value}")
        else:
            print("❌ No metadata found in the image.")
    except Exception as e:
        print("❌ Error reading image metadata:", e)

def extract_pdf_metadata(file_path):
    try:
        reader = PdfReader(file_path)
        metadata = reader.metadata
        if metadata:
            print("\n📄 PDF Metadata:")
            for key, value in metadata.items():
                print(f"{key}: {value}")
        else:
            print("❌ No metadata found in the PDF.")
    except Exception as e:
        print("❌ Error reading PDF metadata:", e)

def show_help():
    print("\nAvailable Commands:")
    print(" exif <file> → Extract metadata from an image or PDF.")
    print(" help → Show this help menu.")
    print(" exit → Exit the program.")

def main():
    print(pyfiglet.figlet_format("ExifTool"))
    while True:
        command = input("\nExifTool> ").strip().split()
        if not command:
            continue
        
        if command[0] == "exif" and len(command) == 2:
            file_path = command[1]
            if not os.path.exists(file_path):
                print("❌ File not found.")
            elif file_path.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".heif", ".heic")):
                extract_image_metadata(file_path)
            elif file_path.lower().endswith(".pdf"):
                extract_pdf_metadata(file_path)
            else:
                print("❌ Unsupported file format.")
        
        elif command[0] == "help":
            show_help()
        
        elif command[0] == "exit":
            break
        else:
            print("❌ Unknown command. Use 'help' to see available commands.")

if __name__ == "__main__":
    main()