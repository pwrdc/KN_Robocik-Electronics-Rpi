import zmq
import time
import ast
import zmq

class ZMQ_Server():
    """
    Klasa  służąca do komunikacji dwóch programów
    data -> dane otrzymywane ze sterownika i wysyłane do klienta
    driver_up (Bool) - czy sterownik jest podłączony
    client_up (Bool) - czy klient jest podłączony
    """

    def __init__(self,data_template, driver_port, client_port, sleep_time=0.1, timeout=100):
        """
        Metoda inicjalizująca serwer dla dwóch portów na localhost
        :param driver_port: -> port sterownika
        :param client_port: -> port programu na rpi
        :param sleep_time: -> czas spania pomiędzy obsługą rządań [s]
        :param timeout: -> czas oczekiwania na otrzymanie lub odebranie wiadomości [ms]

        """
        self.data = data_template
        self.driver_up = False
        self.client_up = False
        self.sleep_time = sleep_time

        self.driver_context = zmq.Context()
        self.client_context = zmq.Context()

        self.driver_socket = self.driver_context.socket(zmq.REP)
        self.client_socket = self.client_context.socket(zmq.REP)

        self.driver_socket.setsockopt(zmq.RCVTIMEO, timeout)
        self.client_socket.setsockopt(zmq.RCVTIMEO, timeout)

        self.driver_adress = "tcp://*:" + str(client_port)
        self.client_adress = "tcp://*:" + str(driver_port)

        self.driver_socket.bind(self.driver_adress) #bug with ports
        self.client_socket.bind(self.client_adress) #communication works with oppposite ports


        print("Server active...")

    def run(self):
        """
        funkcja obsługująca w pętli rządania od klienta i sterownika
        najpierw odbiera dane od sterownika
        potem wysyła dane do klienta
        :return: None
        """
        while True:
            time.sleep(self.sleep_time)
            try:
                self.data = self.driver_socket.recv()  # zmq.NOBLOCK)
                try:
                    self.data = self.data.decode("utf-8")
                    #self.data = ast.literal_eval(self.data)
                except Exception as e:
                    print('Probably wrong data type, exception:',e)
                
                print(self.data) #COMMENT AFTER TESTS

                #print("Driver connected...")
                self.driver_socket.send(b"thanks")  # ,zmq.NOBLOCK)
                self.driver_up = True
            except zmq.error.Again:
                #print("No driver...")
                self.driver_up = False
                pass
            try:
                message = self.client_socket.recv()  # zmq.NOBLOCK)
                #print("Client connected...")
                #self.client_socket.send(bytes(str(self.data), 'utf-8'))  # ,zmq.NOBLOCK)
                self.client_socket.send(bytes(str(self.data), 'utf-8'))
                self.client_up = True
            except zmq.error.Again:
                self.client_up = False
                #print("No client...")
                pass


class Client():
    """


    """
    server_up = False
    connection_on = False
    port = None
    timeout = None

    def __init__(self, port, timeout=200):
        """
        :param port:
        :param timeout: zalecany 2x większy niż timeout serwera
        """
        self.port = port
        self.timeout = timeout
        self.context = zmq.Context()
        print("Connecting to server…")
        self.socket = self.context.socket(zmq.REQ)
        self.socket.setsockopt(zmq.RCVTIMEO, timeout)
        self.socket.connect("tcp://localhost:" + str(self.port))
        self.connection_on = True

    def reboot(self):
        print("rebooting")
        self.context = zmq.Context()
        print("Trying to reconnect…")
        self.socket = self.context.socket(zmq.REQ)
        self.socket.setsockopt(zmq.RCVTIMEO, self.timeout)
        self.socket.connect("tcp://localhost:" + str(self.port))


    def get_data(self):
        try:
            self.socket.send(b"give")
            #print("Sending request...")
            message = self.socket.recv()
            message = message.decode("utf-8")
            if message[0] == '{':
                message = ast.literal_eval(message)  #parsing dicts only
            #print("Received reply:", message)
            self.server_up = True
            return message
        except zmq.ZMQError:
            #print("Server_down...")
            self.server_up = False
        if self.server_up is False:
            self.reboot()

    def send_data(self, data):
        try:
            self.socket.send(bytes(str(data), 'utf-8'))
            #print("Sending data...")
            message = self.socket.recv()  # zmq.NOBLOCK)
            #print("Received reply:", message)
            self.server_up = True
        except zmq.ZMQError:
            self.server_up = False
            #print("Server_down")
        if self.server_up is False:
            self.reboot()
