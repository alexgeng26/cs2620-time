import multiprocessing
import threading
import socket
import json
import queue
import random
import time

# Base port for the machines
BASE_PORT = 6000
NUM_MACHINES = 3

class VirtualMachine:
    def __init__(self, vm_id, tick_rate, partner_info, run_duration):
        self.vm_id = vm_id
        self.tick_rate = tick_rate              # Ticks per second
        self.partner_info = partner_info        # List of (partner_id, host, port) tuples
        self.run_duration = run_duration
        self.logical_clock = 0
        self.message_queue = queue.Queue()
        self.log_filename = f"machine_{self.vm_id}.log"
        self.stop_event = threading.Event()
        self.server_socket = None

    def start_listener(self):
        """Set up a server socket and listen for incoming messages."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', BASE_PORT + self.vm_id))
        self.server_socket.listen(5)
        self.server_socket.settimeout(1.0)  # Use timeout to periodically check for stop_event
        while not self.stop_event.is_set():
            try:
                conn, addr = self.server_socket.accept()
                threading.Thread(target=self.handle_client, args=(conn,), daemon=True).start()
            except socket.timeout:
                continue
        self.server_socket.close()

    def handle_client(self, conn):
        """Handle incoming connection, read data, and enqueue the message."""
        try:
            data = b""
            while True:
                chunk = conn.recv(1024)
                if not chunk:
                    break
                data += chunk
            if data:
                message = json.loads(data.decode('utf-8'))
                self.message_queue.put(message)
        except Exception as e:
            print(f"VM {self.vm_id} error handling client: {e}")
        finally:
            conn.close()

    def send_message(self, partner_host, partner_port, message):
        """Connect to a partner's server socket and send a JSON message."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((partner_host, partner_port))
                s.sendall(json.dumps(message).encode('utf-8'))
        except Exception as e:
            print(f"VM {self.vm_id} failed to send message: {e}")

    def log_event(self, event_type, system_time, additional_info=""):
        """Log an event to the machine's log file."""
        log_line = (f"{event_type} | System Time: {system_time:.4f} | "
                    f"Logical Clock: {self.logical_clock} | {additional_info}\n")
        with open(self.log_filename, "a") as log_file:
            log_file.write(log_line)

    def process_message(self, message, system_time):
        """Process a received message and update the logical clock."""
        received_clock = message.get("clock", 0)
        self.logical_clock = max(self.logical_clock, received_clock) + 1
        q_len = self.message_queue.qsize()
        self.log_event("RECEIVE", system_time, f"From VM {message.get('sender')}, Queue Length: {q_len}")

    def run(self):
        """Main loop: process incoming messages or perform events on each tick."""
        # Start listener thread for incoming socket connections.
        listener_thread = threading.Thread(target=self.start_listener, daemon=True)
        listener_thread.start()

        start_time = time.time()
        while time.time() - start_time < self.run_duration:
            system_time = time.time()
            if not self.message_queue.empty():
                try:
                    message = self.message_queue.get_nowait()
                    self.process_message(message, system_time)
                except queue.Empty:
                    pass
            else:
                event_choice = random.randint(1, 4)
                if event_choice == 1:
                    # Send to first partner, if available.
                    if self.partner_info:
                        partner_id, host, port = self.partner_info[0]
                        msg = {"sender": self.vm_id, "clock": self.logical_clock}
                        self.send_message(host, port, msg)
                        self.logical_clock += 1
                        self.log_event("SEND to VM " + str(partner_id), system_time,
                                       f"Message Clock Sent: {msg['clock']}")
                elif event_choice == 2:
                    # Send to second partner, if available.
                    if len(self.partner_info) > 1:
                        partner_id, host, port = self.partner_info[1]
                        msg = {"sender": self.vm_id, "clock": self.logical_clock}
                        self.send_message(host, port, msg)
                        self.logical_clock += 1
                        self.log_event("SEND to VM " + str(partner_id), system_time,
                                       f"Message Clock Sent: {msg['clock']}")
                elif event_choice == 3:
                    # Send to all partners.
                    if self.partner_info:
                        for partner_id, host, port in self.partner_info:
                            msg = {"sender": self.vm_id, "clock": self.logical_clock}
                            self.send_message(host, port, msg)
                        self.logical_clock += 1
                        partner_ids = ", ".join(str(p[0]) for p in self.partner_info)
                        self.log_event("SEND to VMs " + partner_ids, system_time,
                                       f"Message Clock Sent: {msg['clock']}")
                else:
                    # Internal event.
                    self.logical_clock += 1
                    self.log_event("INTERNAL", system_time)
            time.sleep(1 / self.tick_rate)

        # Signal listener thread to stop and wait for it to finish.
        self.stop_event.set()
        listener_thread.join()

def vm_process(vm_id, run_duration):
    """Process target for each Virtual Machine."""
    tick_rate = random.randint(1, 6)
    # Prepare partner info: (partner_id, host, port) for every other VM.
    partner_info = [(pid, 'localhost', BASE_PORT + pid) for pid in range(NUM_MACHINES) if pid != vm_id]
    vm = VirtualMachine(vm_id, tick_rate, partner_info, run_duration)
    print(f"VM {vm_id} starting with tick rate {tick_rate} ticks/sec, listening on port {BASE_PORT + vm_id}.")
    vm.run()
    print(f"VM {vm_id} finished.")

if __name__ == "__main__":
    run_duration = 60  # seconds to run the simulation
    processes = []
    for vm_id in range(NUM_MACHINES):
        p = multiprocessing.Process(target=vm_process, args=(vm_id, run_duration))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()
    print("Simulation completed.")
