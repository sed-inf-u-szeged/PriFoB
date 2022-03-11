import socket
import requests


def provide_my_address():
    #ip = socket.gethostbyname(socket.gethostname())
    #metadata_url = "http://metadata/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip"
    #metadata_header = {'Metadata-Flavor' : 'Google'}
    #ip = requests.get(metadata_url, headers = metadata_header).text
    ip = requests.get('https://api.ipify.org').content.decode('utf8')
    print('ip: ',ip)
    return ip
