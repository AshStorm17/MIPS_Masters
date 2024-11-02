import multiprocessing
from components.registers import Registers

class WriteBackTest:
    def __init__(self, MEM_WB):
        self.registers = Registers(initialise=True)  # Initialize the register file
        self.MEM_WB = MEM_WB  # Queue to receive MEM/WB pipeline data

    def write_back(self):
        """Simulate write-back stage and display output."""
        while True:
            # Retrieve data from MEM_WB queue
            if not self.MEM_WB.empty():
                wb = self.MEM_WB.get()

                # Check for end signal
                if wb is None:  # If None is received, break the loop
                    break

                inst = wb.get('instruction')
                reg_dst = wb.get('RegDst')
                
                # Perform the write-back operation
                if inst['type'] == 1 and inst['op'][:3] == "100":  # Load instruction
                    self.registers.write(reg_dst, wb['Mem_data'])
                elif inst['type'] in [0, 1]:  # R-type or I-type ALU instruction
                    self.registers.write(reg_dst, wb['ALU_result'])
                
                # Output the result of the write-back stage
                print("Write-back Stage:", {'RegDst': reg_dst, 'Value': self.registers.read(reg_dst)})

# Separate testing script for the write-back stage
if __name__ == "__main__":
    # Create a multiprocessing queue for MEM/WB data
    MEM_WB = multiprocessing.Queue()

    # Example MEM_WB dictionary for testing
    wb = {
        'instruction': {
            'type': 1,
            'op': "100011",  # Example opcode for a load instruction
            'rt': '00010'  # Example target register
        },
        'RegDst': 2,  # Example destination register
        'Mem_data': 1234  # Example memory data
    }

    # Put the example MEM_WB data into the queue
    MEM_WB.put(wb)

    # Create and start the WriteBackTest process
    write_back_test = WriteBackTest(MEM_WB)
    write_back_process = multiprocessing.Process(target=write_back_test.write_back)
    write_back_process.start()

    # After all data has been processed, signal the write-back stage to stop
    MEM_WB.put(None)  # Send termination signal

    # Wait for the write-back process to finish
    write_back_process.join()
