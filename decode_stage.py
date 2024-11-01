import multiprocessing
from components.registers import Registers
from instructions import Instruction
from fetch_stage import FetchTest

class DecodeTest:
    def __init__(self, IF_ID):
        self.IF_ID = IF_ID  # Queue for fetched instructions
        self.ID_EX = {}
        self.registers = Registers()  # Initialize registers

    def decode_stage(self):
        """Simulate decode stage and display output."""
        while True:
            if not self.IF_ID.empty():
                fetched_data = self.IF_ID.get()

                # Check for end signal
                if fetched_data is None:  # If None is received, break the loop
                    break

                IR = fetched_data['IR']
                opcode = int(IR[:6], 2)

                # Create the instruction object based on opcode
                inst = Instruction(type=0 if opcode == 0 else (2 if opcode in [2, 3] else 1), instruction=IR)
                
                self.ID_EX['instruction'] = inst
                self.ID_EX['PC'] = fetched_data['PC']
                self.ID_EX['RS'] = self.registers.read(int(inst.rs, 2))
                self.ID_EX['RT'] = self.registers.read(int(inst.rt, 2))

                if inst.type == 1:
                    immediate = int(inst.immediate, 2)
                    if (immediate & 0x8000):  # Sign extend if negative
                        immediate |= 0xFFFF0000
                    self.ID_EX['Immediate'] = immediate
                
                print("Decoded instruction:", self.ID_EX)

def run_pipeline(file_path):
    # Create a multiprocessing Queue for the IF_ID stage
    IF_ID = multiprocessing.Queue()
    
    # Create and start the FetchTest process
    fetch_test = FetchTest(file_path, IF_ID)
    fetch_process = multiprocessing.Process(target=fetch_test.fetch_stage)
    fetch_process.start()

    # Create DecodeTest instance and run the decode stage
    decode_test = DecodeTest(IF_ID)

    # Run the decode stage in a loop, periodically checking the queue
    decode_process = multiprocessing.Process(target=decode_test.decode_stage)
    decode_process.start()

    # Wait for the fetch process to finish
    fetch_process.join()
    
    # After fetching is done, signal the decode stage to stop
    IF_ID.put(None)  # Signal that no more instructions will be fetched

    # Wait for the decode process to finish
    decode_process.join()

if __name__ == "__main__":
    run_pipeline(file_path="assets/binary.txt")
