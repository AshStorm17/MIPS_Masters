import multiprocessing
from components.registers import Registers
from components.alu import ALU
from components.memory import Memory
from instructions import RtypeInst, ItypeInst, JtypeInst, giveFields
from execute import Execute
from parser import parse_mips_file

class MIPSPipeline:
    def __init__(self, file_path):
        # Initialize components
        self.memory = Memory()
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
        
        # Load instructions into memory
        parse_mips_file(file_path, self.memory)

        # Synchronization events for pipeline control
        self.fetch_done = multiprocessing.Event()
        self.decode_done = multiprocessing.Event()
        self.execute_done = multiprocessing.Event()
        self.memory_done = multiprocessing.Event()
    
    def is_halt_instruction(self, IR):
        """Check if an instruction is a halt instruction (syscall or jr $ra)."""
        opcode = int(IR[:6], 2)
        func = int(IR[-6:], 2)
        
        if opcode == 0:
            if func == 12:  # syscall
                v0 = self.registers.read(2)  # Check $v0 (register 2)
                if v0 == 10:
                    return True
            elif func == 8:  # jr $ra
                ra = self.registers.read(31)  # Check $ra (register 31)
                if ra == 0:  # If ra holds 0, it indicates end
                    return True
        return False
    
    def fetch_stage(self):
        """Fetches instructions from memory."""
        while True:
            with self.pc_lock:
                if self.PC.value < len(self.memory.data) - 4:
                    IR = ''.join(self.memory.data[self.PC.value:self.PC.value + 4])  # Fetch 32-bit instruction
                    # Check if this is a halt instruction (syscall or jr $ra)
                    if self.is_halt_instruction(IR):
                        print("Halting instruction encountered.")
                        break
                    self.IF_ID.put({'PC': self.PC.value, 'IR': IR})
                    self.PC.value += 4
                else:
                    break  # Exit when end of instructions is reached
            self.decode_done.wait()
            self.decode_done.clear()
    
    def decode_stage(self):
        """Decodes instructions and passes to execute stage."""
        while True:
            if not self.IF_ID.empty():
                fetched_data = self.IF_ID.get()
                IR = fetched_data['IR']
                opcode = int(IR[0:7], 2)
                if opcode == 0:
                    fields = giveFields(IR, 0)  # R-type instruction
                    inst_type = RtypeInst
                elif opcode in [2, 3]:
                    fields = giveFields(IR, 2)  # J-type instruction
                    inst_type = JtypeInst
                else:
                    fields = giveFields(IR, 1)  # I-type instruction
                    inst_type = ItypeInst
                self.ID_EX.put({'fields': fields, 'inst_type': inst_type})
                self.decode_done.set()
    
    def execute_stage(self):
        """Executes instructions and passes results to memory access stage."""
        while True:
            if not self.ID_EX.empty():
                decoded_data = self.ID_EX.get()
                fields, inst_type = decoded_data['fields'], decoded_data['inst_type']
                result, dest_reg, inst_type_name = self.execute_handler.executeInst(inst_type, *fields)
                self.EX_MEM.put({'ALU_result': result, 'dest_reg': dest_reg, 'inst_type': inst_type_name})
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
    