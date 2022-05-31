import tkinter as tk
from vidstream import *
from tkinter import messagebox
import socket
import threading

username = " "
client = None
HOST_ADDR = socket.gethostbyname(socket.gethostname())
HOST_PORT = 8080

# VIDSTREAM
# thread to start camera
def start_camera():
    camera_client = CameraClient(HOST_ADDR, 9999)
    t3 = threading.Thread(target=camera_client.start_stream)
    t3.start()

# thread to start screenshare
def start_screenshare():
    screen_client = ScreenShareClient(HOST_ADDR, 9999)
    t4 = threading.Thread(target=screen_client.start_stream)
    t4.start()

# thread to start audio
def start_audio():
    audio_sender = AudioSender(HOST_ADDR, 8888)
    t5 = threading.Thread(target=audio_sender.start_stream)
    t5.start()

# connect button function
def connect():
    global username, client
    if len(nickname_text.get()) < 1:
        tk.messagebox.showerror(title="ERROR!!!", message="You MUST enter your first name <e.g. John>")
    else:
        username = nickname_text.get()
        connect_to_server(username)
       
# connect the user to the server
def connect_to_server(name):
    global client, HOST_PORT, HOST_ADDR
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST_ADDR, HOST_PORT))
        client.send(name.encode()) # Send name to server after connecting

        nickname_text.config(state=tk.DISABLED)
        connect_button.config(state=tk.DISABLED)
        send_text.config(state=tk.NORMAL)

        # start a thread to keep receiving message from server
        threading._start_new_thread(receive_message_from_server, (client, "m"))
    except Exception as e:
        tk.messagebox.showerror(title="ERROR!!!", message="Cannot connect to host: " + HOST_ADDR + " on port: " + str(HOST_PORT) + " Server may be Unavailable. Try again later")

# receive messages from server
def receive_message_from_server(sck, m):
    while True:
        from_server = sck.recv(4096).decode()

        if not from_server: break

        # display message from server on the chat window
        texts = chat_text.get("1.0", tk.END).strip()
        chat_text.config(state=tk.NORMAL)
        if len(texts) < 1:
            chat_text.insert(tk.END, from_server)
        else:
            chat_text.insert(tk.END, "\n\n"+ from_server)

        chat_text.config(state=tk.DISABLED)
        chat_text.see(tk.END)

    sck.close()
    window.destroy()

# get the messages
def getChatMessage(msg):
    msg = msg.replace('\n', '')
    texts = chat_text.get("1.0", tk.END).strip()

    # enable the display area and insert the text and then disable.
    chat_text.config(state=tk.NORMAL)
    if len(texts) < 1:
        chat_text.insert(tk.END, "You->" + msg, "tag_your_message")
    else:
        chat_text.insert(tk.END, "\n\n" + "You->" + msg, "tag_your_message")

    chat_text.config(state=tk.DISABLED)

    send_mssage_to_server(msg)

    chat_text.see(tk.END)
    send_text.delete('1.0', tk.END)


def send_mssage_to_server(msg):
    client_msg = str(msg)
    client.send(client_msg.encode())
    if msg == "exit":
        client.close()
        window.destroy()
    print("Sending message")

# TKINTER
window = tk.Tk()
window.title("Client")
window.configure(bg="#222831")

# images
connect_butt = tk.PhotoImage(file = "images/connect_butt.png")
stop_butt = tk.PhotoImage(file = "images/stop_butt.png")
camera_butt = tk.PhotoImage(file = "images/cam_butt.png")
audio_butt = tk.PhotoImage(file = "images/audio_butt.png")
screen_butt = tk.PhotoImage(file = "images/screen_butt.png")

# Nickname area
nickname_label = tk.Label(window, text="Nickname:", bg="#222831", fg="#EEE", height=2)
nickname_text = tk.Entry(window, width=15)
connect_button = tk.Button(window, text="Connect", bd=0, bg="#FFD369", fg="#000", command=lambda : connect())

# see and send text
chat_text = tk.Text(window, width=47, height=15, bg="#393E46", fg="#EEE")
chat_text.tag_config("tag_your_message", foreground="#FFD369")
chat_text.config(highlightbackground="grey", state="disabled")
send_text = tk.Text(window, width=47, height=2, bg="#393E46", fg="#EEE")
send_text.config(highlightbackground="grey", state="disabled")
send_text.bind("<Return>", (lambda event: getChatMessage(send_text.get("1.0", tk.END))))

# cam, audio and screen button
camera_button = tk.Button(window, image=camera_butt, bd=0, bg="#222831", command=start_camera)
audio_button = tk.Button(window, image=audio_butt, bd=0, bg="#222831", command=start_audio)
screen_button = tk.Button(window, image=screen_butt, bd=0, bg="#222831", command=start_screenshare)

# grid
nickname_label.grid(row=1, column=0, pady=5, sticky=tk.E)
nickname_text.grid(row=1, column=1, pady=5)
connect_button.grid(row=1, column=2, sticky=tk.W)

chat_text.grid(row=2, column=0, columnspan=3, pady=5, padx=10)
send_text.grid(row=3, column=0, columnspan=3, pady=5, padx=10)

camera_button.grid(row=4, column=0, pady=10, padx=10)
audio_button.grid(row=4, column=1)
screen_button.grid(row=4, column=2, padx=10)

# main loop
window.mainloop()