import multiprocessing
from components.memory import Memory
from components.registers import Registers
from decode_stage import DecodeTest
from components.alu import ALU 
from fetch_stage import FetchTest

class ExecuteTest:
    def __init__(self, ID_EX, EX_MEM):
        self.memory = Memory()
        self.registers = Registers(initialise=True)  # Initialize registers
        self.alu = ALU()  # Create an instance of the ALU
        self.PC = multiprocessing.Value('i', 0)
        self.pc_lock = multiprocessing.Lock()
        self.ID_EX = ID_EX  # Queue for decoded instructions
        self.EX_MEM = EX_MEM  # Queue for executed results
        self.execute_done = multiprocessing.Event()

    def execute_stage(self):
        """Simulate execute stage and display output."""
        while True:
            if not self.ID_EX.empty():
                decoded_data = self.ID_EX.get()

                # Check for end signal
                if decoded_data is None:  # If None is received, break the loop
                    break

                # Retrieve the instruction and type
                inst = decoded_data['Instruction']
                type = inst.type  # Save the type of instruction
                inst = inst.get_fields()  # Get the instruction fields as a dictionary

                result = {'instruction': decoded_data['Instruction']}
                
                print("Executing instruction:", inst)

                # Simulated ALU operations based on instruction type
                if type == 0:  # R-type
                    src1 = decoded_data['RS']
                    src2 = decoded_data.get('RT', 0)  # Get RT; default to 0 if not present
                    
                    # ALU operations based on funct
                    if inst['funct'] == '001000':  # jr
                        with self.pc_lock:
                            self.PC.value = src1
                    elif inst['funct'][:3] == "000":  # Shift operations
                        result['ALU_result'] = self.alu.alu_shift(inst['funct'], src1, int(inst['shamt'], 2))
                    else:  # Arithmetic/logical operations
                        result['ALU_result'] = self.alu.alu_arith(inst['funct'], src1, src2)
                        result['RD'] = int(inst['rd'], 2)
                
                elif type == 1:  # I-type
                    src1 = decoded_data['RS']
                    imm = decoded_data.get('Immediate', 0)

                    if inst['op'][:3] == "100":  # Load
                        result['ALU_result'] = self.alu.giveAddr(src1, imm)
                        result['RD'] = int(inst['rt'], 2)
                    elif inst['op'][:3] == "101":  # Store
                        result['ALU_result'] = self.alu.giveAddr(src1, imm)
                        result['RT'] = decoded_data.get('RT', 0)  # Default to 0 if not present
                    else:  # Arithmetic/logical operations
                        result['ALU_result'] = self.alu.alu_arith_i(inst['op'][3:6], src1, imm)
                        result['RD'] = int(inst['rt'], 2)

                elif type == 2:  # J-type
                    addr = int(inst['address'], 2)
                    if inst['op'][3:] == '000010':  # j
                        with self.pc_lock:
                            self.PC.value = (self.PC.value & 0xF0000000) | (addr << 2)
                    elif inst['op'][3:] == '000011':  # jal
                        self.registers.write(31, self.PC.value + 4)
                        with self.pc_lock:
                            self.PC.value = (self.PC.value & 0xF0000000) | (addr << 2)

                print("Executed instruction:", result)
                
                # Put the result in the EX_MEM queue
                self.EX_MEM.put(result)
                self.execute_done.set()

def run_pipeline(file_path):
    # Create a multiprocessing Queue for the IF_ID stage
    IF_ID = multiprocessing.Queue()
    ID_EX = multiprocessing.Queue()  # Create a Queue for ID/EX stage
    EX_MEM = multiprocessing.Queue()  # Create a Queue for EX/MEM stage
    
    # Create and start the FetchTest process
    fetch_test = FetchTest(file_path, IF_ID)
    fetch_process = multiprocessing.Process(target=fetch_test.fetch_stage)
    fetch_process.start()

    # Create DecodeTest instance and run the decode stage
    decode_test = DecodeTest(IF_ID, ID_EX)

    # Run the decode stage in a separate process
    decode_process = multiprocessing.Process(target=decode_test.decode_stage)
    decode_process.start()

    # Create ExecuteTest instance and run the execute stage
    execute_test = ExecuteTest(ID_EX, EX_MEM)
    execute_process = multiprocessing.Process(target=execute_test.execute_stage)
    execute_process.start()

    # Wait for the fetch process to finish
    fetch_process.join()

    # After fetching is done, signal the decode stage to stop
    IF_ID.put(None)  # Signal that no more instructions will be fetched

    # Wait for the decode process to finish
    decode_process.join()

    # After decoding is done, signal the execute stage to stop
    ID_EX.put(None)  # Signal that no more instructions will be executed

    # Wait for the execute process to finish
    execute_process.join()

if __name__ == "__main__":
    run_pipeline(file_path="assets/binary.txt")
