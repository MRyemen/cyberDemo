import hashlib
import time


class Protocol:
    # Use a fixed-size header. 4 digits allow for messages up to 9999 chars.
    LENGTH_FIELD_SIZE = 4
    # Ensure the port matches the server
    PORT = 12345

    def __init__(self, sock=None):
        """
        Allows object creation even without a socket,
        so the client can use the crack_md5 function.
        """
        self.sock = sock

    def create_msg(self, data):
        """
        Creates a message with a fixed-length prefix.
        Returns in bytes format, ready to be sent.
        """
        msg = str(data)
        length = str(len(msg)).zfill(Protocol.LENGTH_FIELD_SIZE)
        return (length + msg).encode()  # encode to bytes

    def get_msg(self):
        """
        Reads a message from the socket according to the protocol.
        First reads the header (length), then reads the message itself.
        """
        if not self.sock:
            return False, "Error: Socket not initialized"

        try:
            # Read the 4-byte header
            length_str = self.sock.recv(Protocol.LENGTH_FIELD_SIZE).decode()
            if not length_str:
                return False, None  # Connection closed

            msg_len = int(length_str)

            # Read the exact number of bytes specified by the header
            msg = self.sock.recv(msg_len).decode()
            return True, msg

        except (ConnectionError, ValueError, OverflowError) as e:
            print(f"Error in get_msg: {e}")
            return False, None
        except Exception as e:
            print(f"An unknown error occurred in get_msg: {e}")
            return False, None

    def crack_md5(self, start, end, solution_found_event, result_list):
        """
        The Worker function that runs in a Thread.
        Scans a given range and stops if the event is set.
        """
        # The target hash, in str format and lowercase
        target_hash = "ec9c0f7edcc18a98b1f31853b1813301"

        # print(f"Thread started. Checking range: {start} - {end}")
        current = start

        while current > end and not solution_found_event.is_set():
            s = str(current)
            res_hex = hashlib.md5(s.encode()).hexdigest()

            if res_hex == target_hash:
                print(f"\n!!! FOUND IT !!! Number: {current}")
                result_list.append(current)  # Store the result
                solution_found_event.set()  # Signal other threads to stop
                return

            # Periodically check the event (not on every iteration)
            if current % 1000000 == 0:
                if solution_found_event.is_set():
                    # print(f"Thread for {start}-{end} stopping early.")
                    return

            current -= 1

        # if not solution_found_event.is_set():
        # print(f"Thread finished range {start}-{end}. Not found.")