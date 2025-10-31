import socket
import random
import datetime
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=
    [
        logging.FileHandler('logg_of_server'),
        #logging.StreamHandler() only when there is a need to show the logs to the user
    ]
)


SERVER_IP = '0.0.0.0'
SERVER_PORT = 1729
MAX_PACKET = 1024

def random_num():
    response = str(random.randint(0, 10))
    return response



def handle_client(client_socket):
    while 1==1:
        cmd = client_socket.recv(4).decode().strip()  #gets the user input
        if not cmd:
            break

        if cmd == 'TIME':
            response = str(datetime.datetime.now())
            logging.info('command is' "TIME")

        elif cmd == 'NAME':
            response = 'Dvirs server'
            assert response == 'Dvirs server'
            logging.info('command is' "NAME")
        elif cmd == 'RAND':
            response = random_num()
            assert (str(0)<=response <=str(10))
            logging.info('command is' "RAND")
        elif cmd == 'EXIT':
            response = 'Bye!'
            try:
                 client_socket.send(response.encode())
                 logging.info('commend is' "EXIT")
            finally:
                break

        else:
            response = 'Unknown command'

        client_socket.send(response.encode())

    client_socket.close()


def main():
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((SERVER_IP, SERVER_PORT))
        server_socket.listen(3)
        print("Server is listening...")
        logging.info('Server is listening...')
    except:
        logging.info('Server is NOT listening...')

    while 1==1:
        client_socket, client_addr = server_socket.accept()
        print("Client connected:", client_addr)
        handle_client(client_socket)
        print("Client disconnected")


if __name__ == '__main__':
    main()