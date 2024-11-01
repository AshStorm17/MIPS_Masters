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
                self.decode_done.set()
    
    def execute_stage(self):
        """Executes instructions and updates the EX/MEM pipeline register."""
        while True:
            if not self.ID_EX.empty():
                decoded_data = self.ID_EX.get()
                inst = decoded_data['instruction']
                self.EX_MEM['instruction'] = inst
                
                if inst.type == 0:  # R-type instruction
                    src1 = decoded_data['RS']
                    src2 = decoded_data['RT']
                    
                    if inst.funct == '001000':  # jr
                        self.pc = src1
                    elif inst.funct[:3] == "000":  # shift operations
                        result = self.alu.alu_shift(inst.funct, src1, int(inst.shamt, 2))
                    else:  # arithmetic/logical operations
                        result = self.alu.alu_arith(inst.funct, src1, src2)
                    
                    dst_reg = int(inst.rd, 2)
                    self.EX_MEM['ALU_result'] = result
                    self.EX_MEM['RegDst'] = dst_reg
                
                elif inst.type == 1:  # I-type instruction
                    src1 = decoded_data['RD_1']
                    imm = decoded_data['Immediate']
                    
                    if inst.op[:3] == "100":  # load
                        address = self.alu.giveAddr(src1, imm)
                        self.EX_MEM['ALU_result'] = address
                        self.EX_MEM['RegDst'] = int(inst.rt, 2)
                    elif inst.op[:3] == "101":  # store
                        address = self.alu.giveAddr(src1, imm)
                        self.EX_MEM['ALU_result'] = address
                        self.EX_MEM['RD_2'] = decoded_data['RD_2']
                    else:  # other arithmetic/logical I-type
                        result = self.alu.alu_arith_i(inst.op[3:6], src1, imm)
                        self.EX_MEM['ALU_result'] = result
                        self.EX_MEM['RegDst'] = int(inst.rt, 2)
                
                elif inst.type == 2:  # J-type instruction
                    addr = int(inst.address, 2)
                    
                    if inst.op[3:] == '000010':  # j instruction
                        self.pc = (self.pc & 0xF0000000) | (addr << 2)
                    elif inst.op[3:] == '000011':  # jal instruction
                        self.registers.write(31, self.pc + 4)  # Write return address
                        self.pc = (self.pc & 0xF0000000) | (addr << 2)
                        
                self.execute_done.set()
    
    def memory_access_stage(self):
        """Handles memory operations and passes results to write-back stage."""
        while True:
            if not self.EX_MEM.empty():
                execute_data = self.EX_MEM.get()
                result, dest_reg, inst_type = execute_data['ALU_result'], execute_data['dest_reg'], execute_data['inst_type']
                mem_data = None
                if inst_type == "load":
                    mem_data = self.memory.load(result)
                elif inst_type == "store":
                    with self.register_lock:
                        self.memory.store(result, self.registers.read(dest_reg))
                self.MEM_WB.put({'mem_data': mem_data, 'ALU_result': result, 'dest_reg': dest_reg})
                self.memory_done.set()
    
    def write_back_stage(self):
        """Writes data back to registers if necessary."""
        while True:
            if not self.MEM_WB.empty():
                mem_data = self.MEM_WB.get()
                dest_reg = mem_data['dest_reg']
                if dest_reg is not None:
                    with self.register_lock:
                        self.registers.write(dest_reg, mem_data['mem_data'] if mem_data['mem_data'] else mem_data['ALU_result'])
    
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
    