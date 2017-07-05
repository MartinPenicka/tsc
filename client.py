import socket, sys, threading, logging, time
from msg_buffer import MessageBuffer

class SocketClient:

    def __init__(self, hostname, port):

        self.__host = hostname
        self.__port = port
        
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__thread         = threading.Thread(target=self.__harvest_messages)
        self.__thread.daemon  = True
        self.__msg_buffer = MessageBuffer()

        self.__keep_running = True

    def __harvest_messages(self):

        while self.__keep_running:

            received = self.__socket.recv(1024)
            if not received:
                logging.debug("Connection with server %s lost", str(self.__host))
                self.__keep_running = False
                break

            self.__msg_buffer.append(received)
            time.sleep(1)

    def connect(self):

        logging.debug("Attempting to connect to server with address %s, port %s", str(self.__host), str(self.__port))
        self.__socket.connect((self.__host, self.__port))
        logging.debug("Connected")
        self.__thread.start()

    def disconnect(self):

        logging.debug("Disconnecting from server")
        self.__socket.close()

    def send(self, data):

        logging.debug("Sending to server: %s", str(data))
        self.__socket.send(data)

    def get_messages(self):

        pass

if __name__ == '__main__':

    client = SocketClient('localhost', 9999)
    client.connect()

    while True:

        data = raw_input("Enter message: ")
        client.send(data)
        time.sleep(1)
