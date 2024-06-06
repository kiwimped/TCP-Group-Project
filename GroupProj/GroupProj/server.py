import socket
import threading
import tkinter as tk
import sys

host = '127.0.0.1'  # Local Host
port = 20000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []  # List to store connected clients' sockets
nicknames = []  # List to store nicknames of connected clients

# Tkinter GUI
root = tk.Tk()
root.title("Server Log")

# Text widget to display log
log_text = tk.Text(root, height=20, width=50)
log_text.pack()

# Function to update the log text widget
# Custom class to redirect stdout to Text widget
class StdoutRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)  # Scroll to the end

    def flush(self):
        pass

# Redirect stdout to Text widget
sys.stdout = StdoutRedirector(log_text)

# Function to broadcast a message to all connected clients
def broadcast(message, sender=None):
    sender_index = None
    if sender:
        sender_index = clients.index(sender)
        message = f"{nicknames[sender_index]}: {message}"
    for client in clients:
        if client != sender:
            client.send(message.encode('utf-8'))

# Function to handle communication with a single client
def handle(client):
    while True:
        try:
            message = client.recv(1024).decode('utf-8')  # Receive message from client
            if message:
                broadcast(message, client)  # Broadcast the received message to all clients
        except:
            # If an error occurs (e.g., client disconnects), remove the client and close its connection
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} left the chat')  # Broadcast that the client left
            nicknames.remove(nickname)
            break

# Function to accept incoming client connections
def receive():
    while True:
        client, address = server.accept()  # Accept a new client connection
        print(f"Connected with {str(address)}")

        nickname = client.recv(1024).decode('utf-8')  # Receive and decode client's nickname
        nicknames.append(nickname)  # Add client's nickname to list
        clients.append(client)  # Add client's socket to list

        print(f'Nickname of the client is {nickname}!')
        broadcast(f'{nickname} joined the chat')  # Broadcast that the client joined
        client.send('Connected to the server!'.encode('utf-8'))  # Send confirmation to the client

        # Start a new thread to handle communication with the client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

    # Close the server socket when the loop ends
    server.close()

print("Server is listening...")
# Start a new thread to run the receive() function
receive_thread = threading.Thread(target=receive)
receive_thread.start()

# Start the Tkinter main loop
root.mainloop()
