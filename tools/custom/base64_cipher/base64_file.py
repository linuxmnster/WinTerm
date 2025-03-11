import base64
import os
os.system("chcp 65001")


def base64_tool(mode, input_type, input_data, output_file=None):
    """
    Base64 Encrypt/Decrypt Tool
    ---------------------------------
    mode        : "encrypt" or "decrypt"
    input_type  : "string" or "file"
    input_data  : The string or file path
    output_file : Output file path (for file input)
    """

    if mode not in ["encrypt", "decrypt"]:
        print(" Invalid mode. Use 'encrypt' or 'decrypt'.")
        return
    
    if input_type not in ["string", "file"]:
        print(" Invalid input type. Use 'string' or 'file'.")
        return

    # ======== If Input Type is STRING ========
    if input_type == "string":
        if mode == "encrypt":
            encoded_data = base64.b64encode(input_data.encode()).decode()
            print(f" Encrypted Base64 Data:\n{encoded_data}")
        elif mode == "decrypt":
            try:
                decoded_data = base64.b64decode(input_data.encode()).decode()
                print(f" Decrypted Data:\n{decoded_data}")
            except Exception as e:
                print(f" Failed to decrypt. Error: {e}")

    # ======== If Input Type is FILE ========
    elif input_type == "file":
        try:
            with open(input_data, "rb") as file:
                file_data = file.read()

            if mode == "encrypt":
                encoded_data = base64.b64encode(file_data)
                if output_file:
                    with open(output_file, "wb") as out_file:
                        out_file.write(encoded_data)
                    print(f"File Encrypted and saved to '{output_file}'")
                else:
                    print(f" Encrypted Base64 Data:\n{encoded_data.decode()}")

            elif mode == "decrypt":
                decoded_data = base64.b64decode(file_data)
                if output_file:
                    with open(output_file, "wb") as out_file:
                        out_file.write(decoded_data)
                    print(f" File Decrypted and saved to '{output_file}'")
                else:
                    print(f" Decrypted Data:\n{decoded_data.decode()}")

        except FileNotFoundError:
            print(" File not found. Please check the file path.")
        except Exception as e:
            print(f" An error occurred: {e}")

# ============================
# Usage Examples
# ============================

# Encrypt a string
base64_tool("encrypt", "string", "Hello CTF!")

# Decrypt a string
base64_tool("decrypt", "string", "SGVsbG8gQ1RGIQ==")

# Encrypt a file
base64_tool("encrypt", "file", "test.txt", "test_encrypted.txt")

# Decrypt a file
base64_tool("decrypt", "file", "test_encrypted.txt", "test_decrypted.txt")