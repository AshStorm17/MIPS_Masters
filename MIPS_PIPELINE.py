import multiprocessing
from components.registers import Registers
from components.alu import ALU
from components.memory import Memory
from instructions import Instruction
from execute import Execute
from MIPS_parser import MIPSParser

class MIPSPipeline:
    def __init__(self, file_path):
        # Initialize components
        self.memory = Memory()
        mips_parser = MIPSParser()
        self.memory.data = mips_parser.parse_mips_file(file_path)
        
        self.alu = ALU()
        self.registers = Registers()
        self.PC = multiprocessing.Value('i', 0)  # Shared program counter
        self.pc_lock = multiprocessing.Lock()  # Lock for updating PC
        
        # Intermediate pipeline queues (for communication between stages)
        self.IF_ID = multiprocessing.Queue()
        self.ID_EX = multiprocessing.Queue()
        self.EX_MEM = multiprocessing.Queue()
        self.MEM_WB = multiprocessing.Queue()
        
        # Register and memory locks
        self.register_lock = multiprocessing.Lock()
        
        # Initialize execute handler
        self.execute_handler = Execute(self.memory, self.registers, self.alu, self.PC)

        # Synchronization events for pipeline control
        self.fetch_done = multiprocessing.Event()
        self.decode_done = multiprocessing.Event()
        self.execute_done = multiprocessing.Event()
        self.memory_done = multiprocessing.Event()

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

            self.decode_done.wait()
            self.decode_done.clear()
    
    def decode_stage(self):
        """Decodes instructions and passes them to the execute stage."""
        while True:
            if not self.IF_ID.empty():
                fetched_data = self.IF_ID.get()

                # Check for end signal
                if fetched_data is None:  # If None is received, break the loop
                    break

                IR = fetched_data['IR']
                opcode = int(IR[:6], 2)
    
                # Create the instruction object based on opcode
                if opcode == 0:
                    inst_type = 0  # R-type
                elif opcode in [2, 3]:
                    inst_type = 2  # J-type
                else:
                    inst_type = 1  # I-type
                
                inst = Instruction(type=inst_type, instruction=IR)
                fields = inst.get_fields()

                # Prepare the data to send to the ID_EX stage
                id_ex_data = {
                    'instruction': inst,
                    'PC': fetched_data['PC'],
                    'RS': self.registers.read(int(fields['rs'], 2)),  # Read value of RS register
                }

                # Handle I-type immediate value and sign extension
                if inst.type == 1:  # I-type instruction
                    immediate = int(IR[16:], 2)  # Immediate is bits 16-31
                    if (immediate & 0x8000):  # Sign extend if negative
                        immediate |= 0xFFFF0000
                    id_ex_data['Immediate'] = immediate
                
                # Handle J-type instruction
                if inst.type == 2:  # J-type instruction
                    id_ex_data['Address'] = int(IR[6:], 2)  # Convert address to decimal

                # Create a dictionary with the mapped values
                decoded_values = {
                    'Instruction': id_ex_data['instruction'],
                    'PC': id_ex_data['PC'],
                    'RS': id_ex_data['RS'],
                }

                # Include RT only for R-type and J-type instructions
                if inst.type == 0 or inst.type == 2:  # R-type or J-type
                    id_ex_data['RT'] = self.registers.read(int(fields['rt'], 2))  # Read RT register
                    decoded_values['RT'] = id_ex_data['RT']
                
                # Add Immediate or Address if they exist
                if 'Immediate' in id_ex_data:
                    decoded_values['Immediate'] = id_ex_data['Immediate']
                if 'Address' in id_ex_data:
                    decoded_values['Address'] = id_ex_data['Address']

                # Send the decoded values to the ID_EX queue
                self.ID_EX.put(decoded_values)
                self.decode_done.set()
    
    def execute_stage(self):
        """Executes instructions and updates the EX/MEM pipeline register."""
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
    
    def memory_access_stage(self):
        """Handles memory operations and passes results to write-back stage."""
        while True:
            if not self.EX_MEM.empty():
                inst = self.EX_MEM.get('instruction')

                if inst['type'] == 1 and inst['op'][:3] == "100":  # Load instruction
                    address = self.EX_MEM['ALU_result']
                    mem_data = "".join(self.memory.load_byte(address + i) for i in range(4))  # Load 4 bytes
                    self.MEM_WB['Mem_data'] = mem_data
                    self.MEM_WB['RegDst'] = self.EX_MEM['RD']
                
                elif inst['type'] == 1 and inst['op'][:3] == "101":  # Store instruction
                    address = self.EX_MEM['ALU_result']
                    store_data = self.EX_MEM['RT']
                    for i in range(4):
                        self.memory.store(store_data[i*8:(i+1)*8], address + i)  # Store each byte individually

                else:  # No memory access, pass ALU result
                    self.MEM_WB['ALU_result'] = self.EX_MEM['ALU_result']
                    self.MEM_WB['RegDst'] = self.EX_MEM['RD']
                
                self.MEM_WB['instruction'] = inst
                self.MEM_WB.put(self.MEM_WB)
                self.memory_done.set()
    
    def write_back_stage(self):
        """Writes data back to registers if necessary."""
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
    
    def run_pipeline(self):
        """Starts and manages pipeline stages as parallel processes."""
        #check the state of registers
        print(self.registers.reg)
        # Initialize processes for each stage
        fetch_process = multiprocessing.Process(target=self.fetch_stage)
        decode_process = multiprocessing.Process(target=self.decode_stage)
        execute_process = multiprocessing.Process(target=self.execute_stage)
        mem_access_process = multiprocessing.Process(target=self.memory_access_stage)
        write_back_process = multiprocessing.Process(target=self.write_back_stage)
        
        # Start all processes
        fetch_process.start()
        decode_process.start()
        execute_process.start()
        mem_access_process.start()
        write_back_process.start()
        
        # Wait for all processes to complete
        fetch_process.join()
        decode_process.join()
        execute_process.join()
        mem_access_process.join()
        write_back_process.join()    

        #check the final state of registers
        print(self.registers.reg)
    
if __name__=="__main__":
    mips_pipeline = MIPSPipeline(file_path="assets/binary.txt")
    mips_pipeline.run_pipeline()
    