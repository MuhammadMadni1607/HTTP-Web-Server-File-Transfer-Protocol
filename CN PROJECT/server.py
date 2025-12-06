import socket
import threading
import os

# Configuration
HOST = '127.0.0.1'
PORT = 8080
STORAGE_DIR = 'files'

# Ensure storage directory exists
if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

def handle_client(conn, addr):
    print(f"[NEW CONN] {addr} connected.")
    try:
        # 1. Receive Request
        request = conn.recv(4096).decode('utf-8', errors='ignore')
        if not request: return

        # 2. Parse HTTP Headers manually (Complex Analysis)
        headers = request.split('\r\n')
        top_line = headers[0].split()
        method = top_line[0]  # GET or POST
        filename = top_line[1].lstrip('/') # e.g., "test.txt"
        
        # Default to index if empty
        if filename == '': filename = 'index.html'

        filepath = os.path.join(STORAGE_DIR, filename)

        # ---------------------------------------------------------
        # HANDLE DOWNLOAD (HTTP GET)
        # ---------------------------------------------------------
        if method == 'GET':
            if os.path.exists(filepath) and os.path.isfile(filepath):
                # Read file binary
                with open(filepath, 'rb') as f:
                    content = f.read()
                
                # Construct HTTP Response Header
                response_header = "HTTP/1.1 200 OK\r\n"
                response_header += f"Content-Length: {len(content)}\r\n"
                response_header += "Content-Type: application/octet-stream\r\n"
                response_header += "Connection: close\r\n\r\n"
                
                # Send Header + Content
                conn.send(response_header.encode() + content)
                print(f"[200 OK] Sent {filename} to {addr}")
            else:
                # 404 Error
                err_msg = "<h1>404 Not Found</h1>"
                response = f"HTTP/1.1 404 Not Found\r\nContent-Length: {len(err_msg)}\r\n\r\n{err_msg}"
                conn.send(response.encode())
                print(f"[404 Error] {filename} requested by {addr}")

        # ---------------------------------------------------------
        # HANDLE UPLOAD (HTTP POST)
        # ---------------------------------------------------------
        elif method == 'POST':
            # Extract Content-Length to know how much data to read
            content_length = 0
            for line in headers:
                if line.startswith("Content-Length:"):
                    content_length = int(line.split(":")[1].strip())

            # Find where the headers end and body begins
            body_start = request.find('\r\n\r\n') + 4
            header_part_size = body_start
            
            # The body might not be fully received in the first recv()
            # We calculate how much body we already have
            body_data = request.encode('utf-8')[body_start:]
            remaining = content_length - len(body_data)

            # Receive the rest of the file
            while remaining > 0:
                chunk = conn.recv(4096)
                if not chunk: break
                body_data += chunk
                remaining -= len(chunk)

            # Save the file
            with open(filepath, 'wb') as f:
                f.write(body_data)
            
            response = "HTTP/1.1 201 Created\r\n\r\nFile Uploaded Successfully"
            conn.send(response.encode())
            print(f"[201 Created] {filename} uploaded by {addr}")

    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        conn.close()

# Main Server Loop
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print(f"HTTP Server started on http://{HOST}:{PORT}")
print(f"Serving files from ./{STORAGE_DIR}/")

while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr)).start()