import socket
import sys
import os

HOST = '127.0.0.1'
PORT = 8080

def upload_file():
    filename = input("Enter filename to upload (must exist on your disk): ")
    if not os.path.exists(filename):
        print("File not found!")
        return

    # Read the file content
    with open(filename, 'rb') as f:
        content = f.read()

    # Construct HTTP POST Request Manually
    # Note: We send the filename in the URL path
    request = f"POST /{filename} HTTP/1.1\r\n"
    request += f"Host: {HOST}\r\n"
    request += f"Content-Length: {len(content)}\r\n"
    request += "\r\n" # Empty line indicates end of headers

    # Send Request + File Content
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    sock.sendall(request.encode() + content)
    
    # Get Response
    response = sock.recv(1024).decode()
    print("\n--- Server Response ---")
    print(response)
    sock.close()

def download_file():
    filename = input("Enter filename to download from server: ")

    # Construct HTTP GET Request
    request = f"GET /{filename} HTTP/1.1\r\n"
    request += f"Host: {HOST}\r\n"
    request += "\r\n"

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    sock.send(request.encode())

    # Parse Header vs Body
    response_data = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk: break
        response_data += chunk
    
    # Separate Header and Body
    header_end = response_data.find(b"\r\n\r\n")
    if header_end == -1:
        print("Invalid response")
        return

    headers = response_data[:header_end].decode()
    body = response_data[header_end+4:]

    # Check for 200 OK
    if "200 OK" in headers:
        with open(f"downloaded_{filename}", 'wb') as f:
            f.write(body)
        print(f"Success! Saved as downloaded_{filename}")
    elif "404 Not Found" in headers:
        print("Error: File not found on server.")
    else:
        print(headers)

    sock.close()

# Menu
while True:
    print("\n1. Upload File")
    print("2. Download File")
    print("3. Exit")
    choice = input("Choose: ")
    
    if choice == '1': upload_file()
    elif choice == '2': download_file()
    elif choice == '3': break