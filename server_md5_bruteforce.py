import socket
import threading
import time
# Import the renamed protocol file
import protocol_md5_bruteforce as protocol


class WorkManager:
    """
    This class replaces 'Ranger'. It manages the entire task pool,
    tracks in-progress tasks, and returns failed tasks back to the pool.
    """

    def __init__(self):
        self.lock = threading.Lock()
        self.chunk_size = 50000000  # Size of each work chunk

        # Pools for task management
        self.todo_chunks = []
        self.in_progress_chunks = {}  # { (start, end) : (client_addr, timestamp) }

        # Create all search tasks in advance
        self._generate_all_chunks()

    def _generate_all_chunks(self):
        """
        Generates all work ranges in advance and puts them in the 'todo' list.
        """
        print("Generating all work chunks...")
        current_start = 10000000000
        while current_start > 0:
            start = current_start
            end = max(0, current_start - self.chunk_size)
            self.todo_chunks.append((start, end))
            current_start -= self.chunk_size
        print(f"Total chunks created: {len(self.todo_chunks)}")

    def get_next_chunk(self, client_addr):
        """
        Takes a task from the todo list, adds it to 'in_progress' tracking, and returns it.
        """
        with self.lock:
            if not self.todo_chunks:
                return None, None  # No more work

            chunk = self.todo_chunks.pop(0)  # Take the next task in line
            self.in_progress_chunks[chunk] = (client_addr, time.time())
            print(f"Assigning chunk {chunk} to {client_addr}")
            return chunk

    def return_chunk_on_failure(self, chunk):
        """
        Returns a failed task (due to disconnect) back to the start of the todo list.
        """
        with self.lock:
            if chunk in self.in_progress_chunks:
                del self.in_progress_chunks[chunk]
                self.todo_chunks.insert(0, chunk)  # Return to the front of the queue
                print(f"WARNING: Chunk {chunk} re-queued due to client failure.")

    def complete_chunk(self, chunk):
        """
        Removes a successfully completed task from the tracking list.
        """
        with self.lock:
            if chunk in self.in_progress_chunks:
                del self.in_progress_chunks[chunk]


class Server:
    def __init__(self, port):
        self.SERVER_HOST = '0.0.0.0'
        self.SERVER_PORT = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.SERVER_HOST, self.SERVER_PORT))
        self.clients = []
        self.clients_lock = threading.Lock()

        # Using the new WorkManager
        self.work_manager = WorkManager()

        self.solution_found_event = threading.Event()
        self.start_time = 0.0

    def handle_client(self, client_sock: socket, addr):
        print(f"Client connected from {addr}")
        pro = protocol.Protocol(client_sock)

        current_chunk = None  # Local variable to track this thread's current task

        try:
            while not self.solution_found_event.is_set():
                # 1. Get a task from the manager
                chunk_tuple = self.work_manager.get_next_chunk(addr)
                if chunk_tuple == (None, None):
                    print(f"Client {addr}: No more work available.")
                    break  # End loop, no more work

                start, end = chunk_tuple
                current_chunk = chunk_tuple  # Store the current task

                # 2. Send task to the client
                client_sock.send(pro.create_msg(start))
                client_sock.send(pro.create_msg(end))

                # 3. Wait for a response (this is where disconnects are caught)
                ok, response = pro.get_msg()

                if not ok:
                    # If 'ok' is False, there was a read error (disconnect)
                    print(f"Client {addr} disconnected while working on chunk {current_chunk}.")
                    break  # Exit the loop, finally block will handle re-queuing

                # 4. Process the response
                if response.startswith("done:"):
                    total_duration = time.time() - self.start_time
                    parts = response.split(':')
                    solution = parts[1]
                    client_time = parts[2] if len(parts) > 2 else "N/A"

                    print("\n" + "=" * 40)
                    print(f"!!! SOLUTION FOUND by {addr}: {solution} !!!")
                    print(f"Client computation time for this chunk: {client_time} seconds")
                    print(f"TOTAL TIME since server start: {total_duration:.2f} seconds")
                    print("=" * 40 + "\n")

                    self.work_manager.complete_chunk(current_chunk)
                    self.solution_found_event.set()  # Signal all to stop
                    break

                elif response.startswith("not found:"):
                    client_time = response.split(':', 1)[1]
                    print(f"Client {addr} finished chunk {current_chunk}. Took {client_time}s. Assigning new range.")
                    self.work_manager.complete_chunk(current_chunk)
                    current_chunk = None  # Reset current task, it's done
                    # The loop will continue and request a new task

            if self.solution_found_event.is_set():
                print(f"Notifying client {addr} to stop.")

        except (ConnectionResetError, BrokenPipeError, socket.error) as e:
            print(f"Client {addr} connection lost abruptly: {e}")

        finally:
            # --- This is the critical part ---
            # If the thread ends for any reason (disconnect, error, etc.)
            # and it was still "holding" an incomplete task, return it to the pool.
            if current_chunk:
                self.work_manager.return_chunk_on_failure(current_chunk)

            # Clean up the client from the active list
            with self.clients_lock:
                if client_sock in self.clients:
                    self.clients.remove(client_sock)
            client_sock.close()
            print(f"Client {addr} handler finished.")

    def main(self):
        self.server_socket.listen(5)
        print(f"Server listening on {self.SERVER_HOST}:{self.SERVER_PORT}")
        self.start_time = time.time()
        print(f"Server started at {time.ctime(self.start_time)}")

        try:
            while not self.solution_found_event.is_set():
                try:
                    self.server_socket.settimeout(1.0)
                    client_sock, addr = self.server_socket.accept()

                    if self.solution_found_event.is_set():
                        client_sock.close()
                        break

                    with self.clients_lock:
                        self.clients.append(client_sock)

                    threading.Thread(target=self.handle_client,
                                     args=(client_sock, addr),
                                     daemon=True).start()

                except socket.timeout:
                    continue

        except KeyboardInterrupt:
            print("\nServer shutting down (KeyboardInterrupt)...")

        finally:
            print("Server shutting down.")
            self.solution_found_event.set()
            time.sleep(1)
            with self.clients_lock:
                for c in self.clients:
                    c.close()
            self.server_socket.close()
            print("Server shutdown complete.")


if __name__ == "__main__":
    my_server = Server(protocol.Protocol.PORT)
    my_server.main()