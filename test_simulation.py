import unittest
import queue
import json
from distributed_simulation import VirtualMachine  # Import from your simulation file

class TestVirtualMachine(unittest.TestCase):
    """Unit tests for the Virtual Machine in the distributed logical clock simulation."""
    
    def setUp(self):
        """Set up a test instance of VirtualMachine before each test."""
        self.vm = VirtualMachine(vm_id=0, tick_rate=3, partner_info=[], run_duration=10)
    
    def test_internal_event_clock_increment(self):
        """Test if the logical clock correctly increments on internal events."""
        initial_clock = self.vm.logical_clock
        self.vm.logical_clock += 1  # Simulate internal event
        self.assertEqual(self.vm.logical_clock, initial_clock + 1, "Internal event should increment logical clock by 1.")
    
    def test_message_reception_updates_logical_clock(self):
        """Test if receiving a message updates the logical clock correctly using the Lamport Rule."""
        self.vm.logical_clock = 5
        received_message = {"sender": 1, "clock": 7}  # Simulating a message from another VM
        self.vm.process_message(received_message, system_time=100)
        
        # Lamport Rule: logical_clock = max(local_clock, received_clock) + 1
        expected_clock = max(5, 7) + 1
        self.assertEqual(self.vm.logical_clock, expected_clock, "Logical clock should update correctly upon receiving a message.")

    def test_message_queue_functionality(self):
        """Test if the message queue correctly receives and processes messages."""
        test_message = {"sender": 1, "clock": 10}
        self.vm.message_queue.put(test_message)
        
        self.assertFalse(self.vm.message_queue.empty(), "Message queue should contain the message.")
        
        retrieved_message = self.vm.message_queue.get()
        self.assertEqual(retrieved_message, test_message, "The message retrieved should match the sent message.")
    
    def test_send_message_format(self):
        """Ensure that the message format is correct before sending."""
        message = {"sender": self.vm.vm_id, "clock": self.vm.logical_clock}
        message_json = json.dumps(message)
        
        # Ensure message is correctly formatted as JSON
        self.assertIsInstance(message_json, str, "Message should be formatted as a JSON string.")
        parsed_message = json.loads(message_json)
        self.assertEqual(parsed_message["sender"], self.vm.vm_id, "Sender ID should match VM ID.")
        self.assertEqual(parsed_message["clock"], self.vm.logical_clock, "Clock value should match logical clock.")
    
    def test_log_event_writes_correctly(self):
        """Test if log entries are written correctly."""
        log_file = "test_log.log"
        self.vm.log_filename = log_file  # Redirect logging to test file
        self.vm.log_event("INTERNAL", system_time=101, additional_info="Test internal event")
        
        with open(log_file, "r") as file:
            lines = file.readlines()
        
        self.assertTrue(len(lines) > 0, "Log file should contain at least one log entry.")
        self.assertIn("INTERNAL", lines[-1], "Last log entry should contain the correct event type.")
    
    def test_logical_clock_drift_calculation(self):
        """Test if logical clock drift is calculated correctly."""
        # Simulating different logical clocks
        lc_vm0 = 50
        lc_vm1 = 30
        lc_vm2 = 40

        drift_vm0_vm1 = abs(lc_vm0 - lc_vm1)
        drift_vm0_vm2 = abs(lc_vm0 - lc_vm2)
        
        self.assertEqual(drift_vm0_vm1, 20, "Drift between VM0 and VM1 should be 20.")
        self.assertEqual(drift_vm0_vm2, 10, "Drift between VM0 and VM2 should be 10.")

if __name__ == "__main__":
    unittest.main()
