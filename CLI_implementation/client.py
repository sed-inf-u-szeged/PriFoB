import socket
import shared_functions


def send(msg, receiver_ip_address, format='UTF-8', header=512, port=5050):
    try:
        server = receiver_ip_address
        address = (server, port)
        self_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self_client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self_client.connect(address)

        msg = shared_functions.get_dict_ready_to_sending(msg)
        third_message = msg.encode(format)
        content_length = len(third_message)
        print(content_length/8)
        second_message = str(content_length).encode(format)
        header_length = len(second_message)
        print(header_length/8)
        first_message = str(header_length).encode(format)
        first_message += b' ' * (header - len(first_message))
        print(len(first_message)/8)
        self_client.send(first_message)
        self_client.send(second_message)
        self_client.send(third_message)

        self_client.close()
    except Exception as e:
        print(e)









