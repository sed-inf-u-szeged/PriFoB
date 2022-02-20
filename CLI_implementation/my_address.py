import socket
import requests

def provide_my_address():
    #ip = socket.gethostbyname(socket.gethostname())
	
	#external ip:
	ip = ip = requests.get('https://api.ipify.org').content.decode('utf8')
	
	#for Google Cloud:
	#metadata_url = "http://metadata/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip"
    #metadata_header = {'Metadata-Flavor' : 'Google'}
    #ip = requests.get(metadata_url, headers = metadata_header).text
    return ip