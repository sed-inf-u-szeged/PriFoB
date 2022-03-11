import socket
import requests

def provide_my_address():
    ip = requests.get('https://api.ipify.org').content.decode('utf8')
    return ip
