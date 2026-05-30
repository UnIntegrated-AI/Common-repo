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
cursor.execute("create table if not exists clients(username char(50) primary key, password varchar(50) not null, banned bool default False)")

HOST = "127.0.0.1" # Put Local IP Address to use multiple devices on same network
PORT = 5000 # putting unique port here


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # creating the server object
server.bind((HOST, PORT)) # binding server with our desired 
server.listen() # starts looking for connection

clients = [] # list of online clients
usernames = [] # list of online usernames
ban_list = []

# def fetch_user():
#     cursor.execute(f"select username from clients where banned = False")
#     user = cursor.fetchall()
#     if user:
#         return True
#     else:
#         return False

cursor.execute("select username from clients where banned = True")
buser = cursor.fetchall()
for buser in buser:
    ban_list.append(buser)


# brodacast messages

def broadcast(msg): 
    for client in clients:
        client.send(msg) # broadcasting the message to each and every client


# handle clients

def handle(client):
    while True:
        try:        # if connection is open
            message = client.recv(1024).decode() # receving messages from clients
            print(f'{message}') # log on server
            if message == "Admin":
                client.send("Get Admin User".encode())
                username = client.recv(1024).decode()
                broadcast(f"Beware! {username} has joined the server".encode())

            broadcast(message.encode()) # sending to client

                        
        except:         # if connection is closed
            index = clients.index(client) # fetching index of client
            clients.remove(client) # removing client
            client.close() # closing client connection
            username = usernames[index]
            broadcast(f"{username} left the chat!".encode())
            usernames.remove(username) # removing username of client
            break

# recieve messages
    
def recieve():
    while True:
        client, address = server.accept() # accept the client connection
        print(f"Connected With {str(address)}")

        client.send("Naam Batao".encode()) # prompting user for username (client ko bhejo)
        username = client.recv(1024).decode()
        client.send("Get Password".encode()) # recieving username
        password = client.recv(1024).decode()
        
        if username in ban_list: # checking if user is banned or not
            client.send("you are banned".encode())
            broadcast(f"Banned user: {username} tried to join the chat but our security took over".encode())
            client.close() # closing connection
            break 
        else:
            print("aa rha h")
            cursor.execute(f"select username from clients where banned = False and username = {username}")
            user = cursor.fetchone()
            if not user: # if user doesn't exists in databse
                cursor.execute(f"insert into clients values({username}, {password}, null)") # register new user
                usernames.append(username) # adding username to server's database
            else:
                cursor.execute(f"select password from clients where username = {username}") # retriving password if user exists
                passwd = cursor.fetchall()[0]
                if password == passwd: # checking if entered password matches the actual one
                    pass
                else:
                    client.send("You entered wrong password".encode()) 
                    client.close() # closing connection is password is wrong
                    break
        

        # Add conditions for username to create a admin page

        if username == "Kirmada" and password == "passwd":
            client.send(f"Welcome {username}".encode())
            broadcast(f"\nBeware! {username} has joined the server.\n".encode())



        # clients.append(client) # adding client to server's client list


        print(f'{username} joined the chat!\n') # log of client in server
        broadcast(f'{username} joined the chat!'.encode()) # broadcasts the joining of client to all clients
        client.send("Connected To the Server!".encode()) # confirmation for client

        thread = threading.Thread(target=handle, args=(client,)) # create a thread for client for handling clients
        thread.start() # start the thread

print("Server running...")
recieve() # main recieve function