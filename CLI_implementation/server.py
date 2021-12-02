import socket
import time
import memory_pool
import json
import my_address

header = 512
PORT = 5050
ip_address = my_address.provide_my_address()
print("IP address of this Server: " + str(ip_address))
ADDR = (ip_address, PORT)
FORMAT = 'UTF-8'
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


def prepare_server():
    try_to_connect = True
    while try_to_connect:
        try:
            server.bind(ADDR)
            try_to_connect = False
            print('Server is ready')
        except Exception as e:
            print(e)
            print('Trying to bind the socket with the port.. Hold please. You can either restart your device to instantly solve this, or wait.')
            time.sleep(5)


def handle_client(connection, address):
    try:
        string_header_length = connection.recv(header).decode(FORMAT)
        if string_header_length:
            int_header_length = int(string_header_length)
            # print(int_header_length)
            string_content_length = connection.recv(int_header_length).decode(FORMAT)
            if string_content_length:
                int_content_length = int(string_content_length)
                # print(int_content_length)
                content = connection.recv(int_content_length)
                if content:
                    decoded_content = content.decode(FORMAT)
                    # print(content)
                    connection.close()
                    received_dictionary = json.loads(decoded_content)
                    memory_pool.received_msgs.put([received_dictionary, address, time.time()])
                else:
                    print('message was not received fully')
    except Exception as e:
        print(e)


def start():
    prepare_server()
    print("[STARTING] this device is ready to receive messages...")
    server.listen()
    print("[LISTENING] ... ")
    while True:
        connection, address = server.accept()
        handle_client(connection, address)
