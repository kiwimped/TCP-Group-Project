import socket
import threading
import tkinter as tk
from tkinter import messagebox
import os

class MyGUI:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 20000
        self.nickname = None
        self.receive_thread = None
        self.client = None
        
        self.root = tk.Tk()
        self.root.title('Chat')

        self.label_nickname = tk.Label(self.root, text='Enter your nickname:', font=('Arial', 12))
        self.label_nickname.pack(padx=10, pady=5)
        
        self.nickname_entry = tk.Entry(self.root, font=('Arial', 12))
        self.nickname_entry.pack(padx=10, pady=5)
        
        self.connect_button = tk.Button(self.root, text='Connect', font=('Arial', 12), command=self.connect_to_server)
        self.connect_button.pack(padx=10, pady=5)
        
        self.label = tk.Label(self.root, text='Type your message:', font=('Arial', 12))
        self.label.pack(padx=10, pady=5)
        
        self.textbox = tk.Text(self.root, height=3, font=('Arial', 12))
        self.textbox.pack(padx=10, pady=5)
        
        self.send_button = tk.Button(self.root, text='Send', font=('Arial', 12), command=self.send_message)
        self.send_button.pack(padx=10, pady=5)
        
        self.label2 = tk.Label(self.root,text='Live Chat Box',font=('Arial',18))
        self.label2.pack(padx=10,pady=10)
        self.chat_text = tk.Text(self.root,height=15,font=('Arial',16))
        self.chat_text.pack()
        self.scrollbar = tk.Scrollbar(self.root, command=self.chat_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.clear_button = tk.Button(self.root, text='Clear', font=('Arial', 12), command=self.clear_chat)
        self.clear_button.pack(padx=10, pady=5)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.root.mainloop()

    def connect_to_server(self):
        nickname = self.nickname_entry.get().strip()
        if nickname:
            self.nickname = nickname
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((self.host, self.port))
            self.client.send(self.nickname.encode('utf-8'))
            self.receive_thread = threading.Thread(target=self.receive)
            self.receive_thread.start()
        else:
            messagebox.showwarning('Warning', 'Please enter a nickname')
            
    def receive(self):
        while True:
            try:
                message = self.client.recv(1024).decode('utf-8')
                if message.startswith('FILE:'):
                    filename = message[5:]
                    file_contents = b""
                    while True:
                        data = self.client.recv(1024)
                        if not data:
                            break
                        file_contents += data
                    folder_name = "received_files"
                    if not os.path.exists(folder_name):
                        os.makedirs(folder_name)
                    file_path = os.path.join(folder_name, filename)
                    with open(file_path, 'wb') as file:
                        file.write(file_contents)
                    self.chat_text.insert(tk.END, f"File received: {file_path}\n")
                else:
                    folder_name = "received_messages"
                    if not os.path.exists(folder_name):
                        os.makedirs(folder_name)
                    file_path = os.path.join(folder_name, "received_message.txt")
                    with open(file_path, 'a') as file:
                        file.write(message + '\n')
                    self.chat_text.insert(tk.END, f"{message}\n")  # Display the message in the chat text widget
            except ConnectionAbortedError:
                break
                
    def send_message(self):
        message = self.textbox.get('1.0', tk.END).strip()
        if message:
            if os.path.exists(message):
                self.client.send(f'FILE:{message}'.encode('utf-8'))
                with open(message, 'rb') as file:
                    file_data = file.read()
                self.client.sendall(file_data)
                self.chat_text.insert(tk.END, f"File sent: {message}\n")
            else:
                self.client.send(message.encode('utf-8'))
                self.chat_text.insert(tk.END, f"{message}\n")  # Display the message in the chat text widget
            self.textbox.delete('1.0', tk.END)
            
    def on_closing(self):
        if self.client:
            self.client.close()
        self.root.destroy()
        
    def clear_chat(self):
        self.chat_text.delete('1.0', tk.END)

MyGUI()
