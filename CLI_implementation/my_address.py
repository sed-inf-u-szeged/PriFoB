import socket


def provide_my_address():
    ip = socket.gethostbyname(socket.gethostname())
    return ip
