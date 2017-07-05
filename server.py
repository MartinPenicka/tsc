import sys, socket, time, threading, logging
from msg_buffer import MessageBuffer

'''
There should be single thread for accepting new connections and separate thread for everi client
'''

class ClientConnection:

    def __init__(self, connection, address):

        self.__connection     = connection
        self.__address        = address
        self.__keep_running   = True

        self.__msg_buffer     = MessageBuffer()
        
        self.__thread         = threading.Thread(target=self.__harvest_messages)
        self.__thread.daemon  = True

    def __harvest_messages(self):

        logging.info("Starting client connection from address %s", str(self.__address))
        while self.__keep_running:

            received = self.__connection.recv(1024)
            if not received:
                logging.debug("Client with address %s disconnected", str(self.__address))
                self.__keep_running = False
                break

            self.__msg_buffer.append(received)
            time.sleep(1)

    def start_thread(self):

        self.__thread.start()

    def stop_thread(self):

        self.__keep_running = False

    def get_messages(self):

        return self.__msg_buffer.get_msg()

    def send_message(self, msg):

        self.__connection.sendall(msg)

    def is_active(self):

        return self.__keep_running

    def get_address(self):
        return self.__address

class SocketServer:

    def __init__(self, port):
        
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__host   = 'localhost'
        self.__port   = port

        self.__thread_connection_accepter = None
        self.__thread_clients             = []

        self.__keep_running_accepting_connections = True

        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__socket.bind((self.__host, self.__port))

        self.__init_threads()

    def __init_threads(self):

        self.__thread_connection_accepter = threading.Thread(target=self.__start_accepting_connections)
        self.__thread_connection_accepter.daemon = True
        self.__thread_connection_accepter.start()

    def __start_accepting_connections(self):

        logging.info("Starting server")
        while self.__keep_running_accepting_connections:

            logging.debug("Listening, waiting for client")
            self.__socket.listen(1)
            conn, addr = self.__socket.accept()

            logging.debug("New client accepted")
            cl_conn = ClientConnection(conn, addr)
            self.__thread_clients.append(cl_conn)
            self.__thread_clients[-1].start_thread()

            time.sleep(1)
            disconnected_clients = []
            for cl_conn in self.__thread_clients:
                if not cl_conn.is_active():
                    disconnected_clients.append(cl_conn)

            for disconnected in disconnected_clients:
                self.__thread_clients.remove(disconnected)

    def stop_server(self):

        self.__keep_running_accepting_connections = False
        for conn in self.__thread_clients:
            conn.stop_thread()

        self.__socket.close()

    def get_messages_from_client_with_index(self, index):

        if index >= len(self.__thread_clients):
            logging.error("[ERROR] Index exceeds number of clients")
            return []
        else:
            return self.__thread_clients[index].get_messages()

    def get_num_of_clients(self):

        return len(self.__thread_clients)

    def get_client_with_index(self, index):

        if index >= len(self.__thread_clients):
            logging.error("[ERROR] Index exceeds number of clients")
            return None
        else:
            return self.__thread_clients[index]

if __name__ == '__main__':

    logging.basicConfig(stream=sys.stdout, \
                        format="%(asctime)s - %(levelname)s:%(message)s", \
                        level=logging.DEBUG, datefmt='%d/%m/%Y %I:%M:%S %p')
    server = SocketServer(9999)

    while True:

        num_clients = server.get_num_of_clients()
        if num_clients > 0:
            for x in range(num_clients):

                msgs = server.get_messages_from_client_with_index(x)
                if len(msgs) > 0:
                    logging.info("Received from client %s data: %s", \
                            str(server.get_client_with_index(x).get_address()), \
                            str(msgs))
        time.sleep(1)
