import multiprocessing
from components.memory import Memory
from MIPS_parser import MIPSParser
from components.registers import Registers

class FetchTest:
    def __init__(self, file_path, IF_ID):
        self.memory = Memory()
        mips_parser = MIPSParser()
        # Store the parsed instructions directly in memory.data as a list of dictionaries
        self.memory.data = mips_parser.parse_mips_file(file_path)
        self.registers = Registers()  # Registers are not needed for this test

        self.PC = multiprocessing.Value('i', 0)  # Shared program counter
        self.pc_lock = multiprocessing.Lock()  # Lock for updating PC
        self.IF_ID = IF_ID  # Queue for fetched instructions

    def is_halt_instruction(self, IR):
        """Check if an instruction is a halt instruction (`syscall` or `jr $ra`)."""
        opcode = int(IR[:6], 2)
        func = int(IR[-6:], 2)

        if opcode == 0:  # This is an R-type instruction
            if func == 12:  # syscall
                return True
            elif func == 8:  # jr (jump register)
                rs = int(IR[6:11], 2)  # Extract the rs field (source register)
                if rs == 31:  # Check if it's $ra (register 31)
                    ra = self.registers.read(31)  # Read the $ra register
                    if ra == 0:  # If $ra holds 0, it indicates end
                        return True
        return False

    def fetch_stage(self):
        """Fetches instructions from memory."""
        while True:
            with self.pc_lock:
                # Check if PC is within range
                if self.PC.value // 4 < len(self.memory.data):
                    instruction_data = self.memory.data[self.PC.value // 4]
                    IR = instruction_data["IR"]
                    if self.is_halt_instruction(IR):
                        break  # Exit when halt instruction is reached
                    PC = instruction_data["PC"]
                    self.IF_ID.put({'PC': PC, 'IR': IR})
                    self.PC.value += 4
                else:
                    break  # Exit when end of instructions is reached

    def run_fetch_test(self):
        """Run the fetch stage and display the queue contents."""
        self.fetch_stage()
        
        # Display instructions fetched into IF_ID queue
        print("\nInstructions in IF_ID queue:")
        while not self.IF_ID.empty():
            instruction = self.IF_ID.get()
            print(instruction)


if __name__ == "__main__":
    # Test with binary instructions file
    fetch_test = FetchTest(file_path="assets/binary.txt", IF_ID=multiprocessing.Queue())
    fetch_test.run_fetch_test()
