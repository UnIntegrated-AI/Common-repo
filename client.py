import socket
import threading

HOST = "127.0.0.1"
PORT = 5000

username = input("Enter Your Username: ")
password = input("Enter Your Password: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT)) # client connected to the ip and port of server 


def recieve():
    while True:
        try: # if connection is good
            message = client.recv(1024).decode() # receiving any message sent by the server

            if username == "Kirmada":
                client.send("Admin".encode())
                get_admin_user = client.recv(1024).decode
                if get_admin_user == "Get Admin User":
                    client.send(username.encode())
            else:
                if message == "Naam Batao": # if server is asking for username
                    client.send(username.encode()) # sending username to server (client hi bhej raha hai)
                    get_pass = client.recv(1024).decode()
                    if get_pass == "Get Password":
                        client.send(password.encode())
                else:
                    print(message) # printing message if server is not asking for username
        except: # if connection is lost
            print("An error occured!") # informing user about lost connection
            client.close() # closing client connection
            break


def write():
    while True:
        msg = input("")
        if msg:
            message = f"{username}: {msg}"
            client.send(message.encode())
            # message = f'{username}: {input("")}' # Forces the user to either send a message or close connection
        else:
            pass

recieve_thread = threading.Thread(target=recieve) # thread for recieving messages
recieve_thread.start()

write_thread = threading.Thread(target=write) # thread for writing message
write_thread.start()