import requests
from flask import Flask, request, Response

app = Flask(__name__)

@app.route('/test')
def test():
    resp = requests.get('http://34.71.230.63:5000/', json=request.get_json())
    excluded_headers = ['content - encoding', 'content - length', 'transfer - encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
    response = Response(resp.content, resp.status_code, headers)
    return response

if __name__ == '__main__':
    app.run(host="0.0.0.0")
