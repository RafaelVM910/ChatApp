import tkinter as tk
import socket
import threading
from vidstream import *

# TKINTER
# Window config
window = tk.Tk()
window.title("Sever")
window.geometry("400x230")
window.configure(bg="#222831")

# images
connect_butt = tk.PhotoImage(file = "images/connect_butt.png")
stop_butt = tk.PhotoImage(file = "images/stop_butt.png")

# labels - host and port
host_label = tk.Label(window, text="Host:\nX.X.X.X", fg="#EEE", bg="#222831", padx="45px", pady="5px")
port_label = tk.Label(window, text="Port:\nXXXX", fg="#EEE", bg="#222831", padx="50px", pady="5px")
# buttons - connect and stop
connect_button = tk.Button(window, image=connect_butt, bd=0, bg="#222831", command=lambda : start_server())
stop_button = tk.Button(window, image=stop_butt, bd=0, bg="#222831", command=lambda : stop_server(), state=tk.DISABLED)
# users box
users_label = tk.Label(window, text="Users Connected:", fg="#EEE", bg="#222831")
users_box = tk.Text(window, height=10, width=25, bg="#393E46", fg="#EEE")

# grid
host_label.grid(row=0, column=0)
port_label.grid(row=1, column=0)

connect_button.grid(row=2, column=0)
stop_button.grid(row=3, column=0)

users_label.grid(row=0, column=1)
users_box.grid(row=1, column=1, rowspan=3)

# CHAT
server = None
HOST_ADDR = socket.gethostbyname(socket.gethostname())
HOST_PORT = 8080
client_name = " "
clients = []
clients_names = []
vidstream_server = StreamingServer(HOST_ADDR, 9999)
vidstream_audio = AudioReceiver(HOST_ADDR, 8888)

# function to start server
def start_server():
    connect_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(socket.AF_INET)
    print(socket.SOCK_STREAM)

    server.bind((HOST_ADDR, HOST_PORT))
    server.listen(5)

    threading._start_new_thread(accept_clients, (server, " "))

    host_label["text"] = "Host:\n" + HOST_ADDR
    port_label["text"] = "Port:\n" + str(HOST_PORT)
    
    # start vidstream server
    vidstream_server.start_server()
    vidstream_audio.start_server()

# Stop server 
def stop_server():
    global server
    connect_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    # stop vidstream
    vidstream_server.stop_server()
    vidstream_audio.stop_server()

# function that handles clients
def accept_clients(the_server, y):
    while True:
        client, addr = the_server.accept()
        clients.append(client)

        threading._start_new_thread(send_receive_client_message, (client, addr))

# receive message from current client and send that message to other clients
def send_receive_client_message(client_connection, client_ip_addr):
    global server, client_name, clients, clients_addr
    client_msg = " "

    # Welcome user
    client_name  = client_connection.recv(4096).decode()
    welcome_msg = "Welcome " + client_name + ". Type 'exit' to quit"
    client_connection.send(welcome_msg.encode())

    clients_names.append(client_name)
    update_client_names_display(clients_names) 

    while True:
        data = client_connection.recv(4096).decode()
        if not data: break
        if data == "exit": break

        client_msg = data

        idx = get_client_index(clients, client_connection)
        sending_client_name = clients_names[idx]

        for c in clients:
            if c != client_connection:
                server_msg = str(sending_client_name + "->" + client_msg)
                c.send(server_msg.encode())

    # find the client index then remove from both lists
    idx = get_client_index(clients, client_connection)
    del clients_names[idx]
    del clients[idx]
    server_msg = "BYE!"
    client_connection.send(server_msg.encode())
    client_connection.close()

    update_client_names_display(clients_names)

# helper functions
# Return the index of the current client in the list of clients
def get_client_index(client_list, curr_client):
    idx = 0
    for conn in client_list:
        if conn == curr_client:
            break
        idx = idx + 1

    return idx

# Update client name display
def update_client_names_display(name_list):
    users_box.config(state=tk.NORMAL)
    users_box.delete('1.0', tk.END)

    for c in name_list:
        users_box.insert(tk.END, c+"\n")
    users_box.config(state=tk.DISABLED)

# Main loop
window.mainloop()