import socket
from _thread import *
from netbuffer import buffer
import os


def threaded_echo(client_socket, addr):
    print('Connected by :', addr[0], ':', addr[1])
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                print('Disconnected by ' + addr[0], ':', addr[1])
                break
            print('Received from ' + addr[0], ':', addr[1], data.decode())
            client_socket.send(data)
        except ConnectionResetError as e:
            print('Disconnected by ' + addr[0], ':', addr[1])
            break
    client_socket.close()


def thread_file(connbuf, conn):
    while True:
        #hash_type = connbuf.get_utf8()
        #if not hash_type:
        #    break
        #print('hash type: ', hash_type)

        file_name = connbuf.get_utf8()
        if not file_name:
            break
        file_name = os.path.join('uploads', file_name)
        print('file name: ', file_name)

        file_size = int(connbuf.get_utf8())
        print('file size: ', file_size)

        with open(file_name, 'wb') as f:
            remaining = file_size
            while remaining:
                # set chunk size
                chunk_size = 4096 if remaining >= 4096 else remaining
                chunk = connbuf.get_bytes(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                remaining -= len(chunk)
            if remaining:
                print('File incomplete.  Missing', remaining, 'bytes.')
            else:
                print('File received successfully.')

    print('Connection closed.')
    conn.close()
    pass

try:
    os.mkdir('uploads')
except FileExistsError:
    pass

HOST = '0.0.0.0'
PORT = 9080

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()

print('server start')

while True:
    print('wait')

    client_socket, addr = server_socket.accept()
    customBuffer = buffer.Buffer(client_socket)

    start_new_thread(thread_file, (customBuffer, client_socket))

server_socket.close()
