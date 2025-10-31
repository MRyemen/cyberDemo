import socket
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=
    [
        logging.FileHandler('logg_of_client'),
        #logging.StreamHandler() only when there is a need to show the logs to the user
    ]
)

SERVER_IP = '127.0.0.1'
SERVER_PORT = 1729
MAX_PACKET = 1024

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((SERVER_IP, SERVER_PORT))
        logging.info('Client connected successfully') #giving a logg message
        print('Connected to server at'+ SERVER_IP + str(SERVER_PORT))

        while 1==1:
            cmd = input("Enter command (TIME, NAME, RAND, EXIT): ").strip().upper()
            cmd = cmd.ljust(4)[:4]  #making sure its 4 bytes

            client_socket.send(cmd.encode())#sending the command to the server
            logging.info('Command sent to server successfully')

            response = client_socket.recv(MAX_PACKET)#getting a response from the server
            logging.info('Response received from server')
            print("Server response:", response.decode())


            if cmd.strip() == "EXIT":#if cmd == 'exit' then leave the while loop
                print("see ya later")
                break

    except Exception as e:
        print("Error:", e)
    finally:
        client_socket.close()
        print("Connection closed.")

if __name__ == "__main__":
    main()