import socket # importing socket (the server module)
import threading # importing threading (the connector one)
import mysql.connector

conn = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "root"
)

cursor = conn.cursor()

cursor.execute("create database if not exists secure_chat_room")
cursor.execute("use secure_chat_room")
cursor.execute("create table if not exists clients(user char(50) primary key, password varchar(50) not null, banned bool default False)")

HOST = "127.0.0.1" # Put Local IP Address to use multiple devices on same network
PORT = 5000 # putting unique port here


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # creating the server object
server.bind((HOST, PORT)) # binding server with our desired 
server.listen() # starts looking for connection

clients = [] # list of online clients
usernames = [] # list of online usernames
ban_list = []
commands = ['ban','kick']

def find_user(username):
    cursor.execute(f'select * from clients where user = "{username}"')
    inf = cursor.fetchone()
    if inf:
        return True
    else:
        return False

cursor.execute("select user from clients where banned = True")
buser = cursor.fetchall()
for buser in buser:
    ban_list.append(buser)


# brodacast messages

def broadcast(msg): 
    for client in clients:
        client.send(msg) # broadcasting the message to each and every client


# handle clients

def handle(client, uname):
    while True:
        try:        # if connection is open
            message = client.recv(1024).decode() # receving messages from clients
            if uname == "kirmada":
                if message[len(uname)+2] == "?": # kirmada: ?kick username
                    
                    command = message[len(uname)+3:]
                    tname = command.split(" ")
                    cmd = tname[0]
                    tname = tname[1]
                    if  cmd in commands:
                        if  cmd == commands[0]:
                            ban_user(tname)
                            break
                        elif cmd == commands[1]:
                            # client.send("You are kicked by kirmada")
                            
                            kick_user(tname)
                            break


            print(f'{message}') # log on server
            broadcast(message.encode()) # sending to client
        except:         # if connection is closed
            clients.remove(client) # removing client
            client.close() # closing client connection
            broadcast(f"{uname} left the chat!".encode())
            usernames.remove(uname) # removing username of client
            break

def ban_user(tname):
    name_index = usernames.index(tname)
    client_to_ban = clients[name_index]
    clients.remove(client_to_ban)
    client_to_ban.send("You were banned from the Server!")
    client_to_ban.close()
    cursor.execute(f'update clients set banned = True where user = "{tname}"')
    conn.commit()
    broadcast(f"{tname} has been banned from the chat".encode())

def kick_user(tname):
    if tname in usernames:
        name_index = usernames.index(tname)
        client_to_kick = clients[name_index]
        clients.remove(client_to_kick)
        client_to_kick.send("You were kicked by kirmada!".encode())
        client_to_kick.close()
        usernames.remove(client_to_kick)
        broadcast(f"{tname} has been kicked from the chat".encode())

# recieve messages
    
def recieve():
    while True:
        client, address = server.accept() # accept the client connection
        print(f"Connected With {str(address)}")

        client.send("Naam Batao".encode()) # prompting user for username (client ko bhejo)
        username = client.recv(1024).decode()
        client.send("Get Password".encode()) # recieving username
        password = client.recv(1024).decode()
        
        if not find_user(username):
            print("register page entered")
            cursor.execute(f'insert into clients(user, password) values("{username}", "{password}")')
            conn.commit()
            print(f"{username} just signned up")
        else:
            print("trying fetch pass")
            cursor.execute(f'select user,password from clients where user = "{username}"')
            info = cursor.fetchone()
            
            if info[0] == "kirmada" and info[1] == "passwd":
                print('Admin has joined.')
                broadcast("Admin has joined the chat (Be Aware!)".encode())
                client.send("Welcome Admin!".encode())
            elif info[1] == password:
                if username in ban_list:
                    client.send("you are banned".encode())
                    print(f"banned user {username} tried to login")
                    client.close()
                    break
                
                print(f"{username} logged in successfully")
                client.send("login successful".encode())
            else:
                client.send("wrong password".encode())
                client.close()

        clients.append(client) # adding client to server's client list


        print(f'{username} joined the chat!\n') # log of client in server
        broadcast(f'{username} joined the chat!'.encode()) # broadcasts the joining of client to all clients
        client.send("Connected To the Server!".encode()) # confirmation for client

        thread = threading.Thread(target=handle, args=(client,username)) # create a thread for client for handling clients
        thread.start() # start the thread

print("Server running...")
recieve() # main recieve function
