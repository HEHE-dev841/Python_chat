import os
import socket
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog, messagebox
import vlc

# Global variables
client_socket = None
username = None

def on_video_end(player, video_window):
    """Close video window when video ends."""
    player.stop()  # Stop playback
    video_window.destroy()  # Close video window

# Function to open the chat window
def open_chat_window():
    global client_socket, message_entry, chat_display, username

    chat_window = tk.Tk()
    chat_window.title(f"Chat Application - {username}")
    chat_window.geometry("600x600")

    # Apply a dark theme with neon accents and rounded corners
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TFrame", background="#1e1e1e")
    style.configure("TButton", background="#333333", foreground="white", borderwidth=1, focusthickness=3, focuscolor="none", font=('Arial', 12, 'bold'), relief="flat")
    style.map("TButton", background=[('active', '#444444')], relief=[('pressed', 'sunken'), ('!pressed', 'flat')])
    style.configure("TEntry", fieldbackground="#2b2b2b", foreground="white", font=('Arial', 14), padding=10, relief="flat")
    style.configure("TLabel", background="#1e1e1e", foreground="white", font=('Arial', 12))
    style.configure("Vertical.TScrollbar", gripcount=0, background="#333333", darkcolor="#444444", lightcolor="#333333", troughcolor="#1e1e1e", bordercolor="#1e1e1e")

    main_frame = ttk.Frame(chat_window, padding="5 5 5 5", style="TFrame")
    main_frame.pack(fill=tk.BOTH, expand=True)

    chat_display = scrolledtext.ScrolledText(main_frame, state=tk.DISABLED, wrap=tk.WORD, bg='#1c1c1c', fg='cyan', font=('Arial', 14), borderwidth=0, selectbackground='#222', selectforeground='cyan')
    chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    input_frame = ttk.Frame(main_frame, style="TFrame")
    input_frame.pack(fill=tk.X, padx=5, pady=5, side=tk.BOTTOM)

    message_entry = tk.Entry(input_frame, bg='#1c1c1c', fg='cyan', font=('Arial', 14), bd=0, highlightthickness=1, highlightbackground="#444", highlightcolor="#555")
    message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 5))
    message_entry.bind("<Return>", send_message)  # Bind Enter key to send message

    send_button = tk.Button(input_frame, text="Send", command=send_message, bg="#333", fg="white", font=('Arial', 12, 'bold'), bd=0, highlightthickness=1, highlightbackground="#444", highlightcolor="#555", relief="flat", activebackground='#555')
    send_button.pack(side=tk.RIGHT, ipadx=10, ipady=5)

    receive_thread = threading.Thread(target=receive_messages,
                                      args=(client_socket,
                                            chat_display,
                                            username))
    receive_thread.daemon = True 
    receive_thread.start()

    chat_window.mainloop()

# Function to receive messages from the server and display them
def receive_messages(client_socket, chat_display, username):
    while True:
        try:
            message = client_socket.recv(1024)
            if message:
                decoded_message = message.decode('utf-8')
                if not decoded_message.startswith(f"{username}:"):
                    chat_display.config(state=tk.NORMAL)  # Enable editing
                    chat_display.insert(tk.END, decoded_message + "\n")  # Show received message
                    chat_display.config(state=tk.DISABLED)  # Disable editing
                    chat_display.yview(tk.END)  # Auto-scroll to the bottom
        except:
            break

# Function to send messages to the server
def send_message(event=None):
    message = message_entry.get()
    if message:
        client_socket.send(f"{username}: {message}".encode('utf-8'))  # Send message to server with username
        
        # Display the message in the chat area
        chat_display.config(state=tk.NORMAL)  # Enable editing
        chat_display.insert(tk.END, f"{username}: {message}\n")  # Show username instead of "You:"
        chat_display.config(state=tk.DISABLED)  # Disable editing
        chat_display.yview(tk.END)  # Auto-scroll to the bottom
        
        # Clear the message entry box
        message_entry.delete(0, tk.END)

# Function to set up the client and GUI components.
def start_client(server_ip, server_port):
    global client_socket, username

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((server_ip, server_port))
    except Exception as e:
        messagebox.showerror("Connection Error", f"Unable to connect to server: {e}")
        return

    username = simpledialog.askstring("Username", "Enter your username:")
    if not username:
        return  
    
    password = simpledialog.askstring("Password", "Enter the password:", show="*")
    if not password:
        return  

    client_socket.send(username.encode('utf-8'))
    client_socket.send(password.encode('utf-8'))

    response = client_socket.recv(1024).decode('utf-8')
    if "Incorrect password" in response:
        messagebox.showerror("Login Error", response)
        client_socket.close()
        return

    video_window = tk.Tk()
    video_window.title("Welcome Video")
    video_window.geometry("800x600")

    # Create a VLC instance and player
    instance = vlc.Instance()
    player = instance.media_player_new()
    
    # Load the video file from the script's directory
    script_directory = os.path.dirname(os.path.abspath(__file__))
    media_path = os.path.join(script_directory, "Start.mp4")
    media = instance.media_new(media_path)
    player.set_media(media)

    # Create a frame for video display
    video_frame = ttk.Frame(video_window)
    video_frame.pack(fill=tk.BOTH, expand=True)

    label = tk.Label(video_frame)
    label.pack(fill=tk.BOTH, expand=True)

    def embed_player():
        hwnd = label.winfo_id()  # Get the window ID for embedding
        player.set_hwnd(hwnd)
    
    embed_player()
    
    player.play()  # Start playing the video

    # Attach event listener for when video ends
    event_manager = player.event_manager()
    event_manager.event_attach(vlc.EventType.MediaPlayerEndReached,
                               lambda event: on_video_end(player, video_window))

    # Open chat window after 5 seconds and close video window
    def switch_to_chat():
        video_window.destroy()
        open_chat_window()

    video_window.after(3750, switch_to_chat)

    video_window.mainloop()

if __name__ == "__main__":
    server_ip = "0.0.0.0.0.0."  # Replace with your DuckDNS subdomain
    server_port = 12345
    
    start_client(server_ip, server_port)
