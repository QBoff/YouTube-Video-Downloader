# for implementing the HTTP Web servers
import http.server
# provides access to the BSD socket interface
import socket
# a framework for network servers
import socketserver
# to display a Web-based documents to users
import webbrowser
# to generate qrcode
import pyqrcode
from pyqrcode import QRCode

import png  # for converting into png format
import os

from datamanager import Manager, Profile


PORT = 8010
# it will work when i will connect it with main.py
# account = Manager.getActiveUser()
# pr = Profile(account.userLogin)
# print(pr.settings)

user_path = os.path.join(os.getcwd(), "qboff\\Videos")
os.chdir(user_path)

Handler = http.server.SimpleHTTPRequestHandler

hostname = socket.gethostname()

# finding the IP address of the PC
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
IP = "http://" + s.getsockname()[0] + ":" + str(PORT)
link = IP

# converts the IP address into a Qrcode
url = pyqrcode.create(link)
# saves the Qrcode inform of svg
url.svg("myqr.svg", scale=8)
# opens the Qrcode image in the web browser
webbrowser.open('myqr.svg')


# Creating the HTTP request and serving the
# folder in the PORT 8010,and the pyqrcode is generated
 
# continuous stream of data between client and server
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    print("Type this in your Browser", IP)
    print("or Use the QRCode")
    httpd.serve_forever()