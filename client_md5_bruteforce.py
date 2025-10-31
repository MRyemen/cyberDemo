import socket
import threading
import os
# Import the renamed protocol file
import protocol_md5_bruteforce as protocol
import time

SERVER_IP = "127.0.0.1"  # Change to the server's IP if not local
SERVER_PORT = 12345  # Must match the port in the server and protocol
# Set the number of cores to use
CPU_COUNT = os.cpu_count() or 4  # Default to 4 if os.cpu_count() fails


def worker_function(start, end, solution_found_event, result_list):
    """
    This is the function that will run in each thread.
    It calls the cracking logic from the protocol.
    """
    p = protocol.Protocol()  # Create an object just to use the function
    p.crack_md5(start, end, solution_found_event, result_list)


def main():
    print(f"Client starting... configured to use {CPU_COUNT} cores.")

    try:
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_sock.connect((SERVER_IP, SERVER_PORT))
        print(f"Connected to server at {SERVER_IP}:{SERVER_PORT}")

        # Create a protocol object with the server's socket
        pro = protocol.Protocol(client_sock)

        # Main client loop - keeps requesting work
        while True:
            # 1. Get work (start and end range)
            print("Requesting work from server...")
            ok, start_str = pro.get_msg()
            if not ok or start_str is None:
                print("Failed to get 'start' range. Server disconnected.")
                break

            ok, end_str = pro.get_msg()
            if not ok or end_str is None:
                print("Failed to get 'end' range. Server disconnected.")
                break

            try:
                # The server sends (high, low)
                start_range = int(start_str)
                end_range = int(end_str)
                print(f"Received range: {start_range} down to {end_range}")

            except ValueError:
                print(f"Received invalid range data: {start_str}, {end_str}")
                continue  # Request new work

            # Record the start time for processing this chunk
            chunk_start_time = time.time()

            # 2. Process the work using Threads
            threads = []
            solution_found_event = threading.Event()
            result_list = []  # List to store the result (if found)

            # Calculate the range size for each thread
            total_range_size = start_range - end_range
            # Prevent division by zero if range is smaller than core count
            chunk_size = (total_range_size // CPU_COUNT) + 1

            print(f"Dividing work into {CPU_COUNT} threads...")

            for i in range(CPU_COUNT):
                # Calculate the sub-range for the current thread
                sub_start = start_range - (i * chunk_size)
                sub_end = max(end_range, sub_start - chunk_size)

                if sub_start <= end_range:
                    break  # No need for more threads if we've covered the range

                # print(f"Thread {i} getting range {sub_start} -> {sub_end}")
                t = threading.Thread(target=worker_function,
                                     args=(sub_start, sub_end, solution_found_event, result_list))
                threads.append(t)
                t.start()

            # Wait for all threads to finish
            for t in threads:
                t.join()

            # Calculate the processing time
            chunk_duration = time.time() - chunk_start_time
            print(f"Chunk processing complete. Duration: {chunk_duration:.2f} seconds.")

            # 3. Report results
            if solution_found_event.is_set():
                # We found it!
                found_number = result_list[0]
                print(f"Work complete. Found solution: {found_number}")
                # Add the time to the message
                client_sock.send(pro.create_msg(f"done:{found_number}:{chunk_duration:.2f}"))
                print("Solution sent to server. Exiting.")
                break  # Exit the main loop
            else:
                # We didn't find it
                print("Work complete. Solution not in this range.")
                # Add the time to the message
                client_sock.send(pro.create_msg(f"not found:{chunk_duration:.2f}"))
                # The loop will continue and request a new range

    except ConnectionRefusedError:
        print("Connection refused. Is the server running?")
    except (ConnectionResetError, BrokenPipeError):
        print("Connection to server was lost.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'client_sock' in locals():
            client_sock.close()
        print("Connection closed.")


if __name__ == "__main__":
    main()