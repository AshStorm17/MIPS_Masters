from components.alu import ALU
from components.memory import Memory
from components.registers import Registers
from utils.instruction_old import Instruction
from parser_old import parse_mips_file
import multiprocessing as mp
from queue import Empty
from multiprocessing import Process, Queue, Event, Value
from ctypes import c_bool
import time

class PipelinedProcessor:
    def __init__(self, mem, alu, reg):
        self.memory = mem
        self.alu = alu
        self.registers = reg
        self.pc = Value('i', 0)
        
        # Shared halt flag
        self.halt = Value(c_bool, False)
        
        # Pipeline stage queues
        self.IF_ID_queue = Queue()
        self.ID_EX_queue = Queue()
        self.EX_MEM_queue = Queue()
        self.MEM_WB_queue = Queue()
        
        # Pipeline control events
        self.fetch_done = Event()
        self.all_done = Event()
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
        """Fetch stage process"""
        while not self.halt.value:
            try:
                # Fetch instruction from memory
                instr = ""
                current_pc = self.pc.value
                for i in range(4):
                    instr += self.memory.data[current_pc + i]
                
                # Check for halt instruction
                if self.is_halt_instruction(instr):
                    self.halt.value = True
                    print("Halt instruction encountered. Stopping fetch.")
                    self.fetch_done.set()
                    break
                
                # Put instruction in IF/ID queue
                self.IF_ID_queue.put({
                    'instruction': instr,
                    'PC': format(current_pc + 4, '032b')
                })
                
                # Update PC
                with self.pc.get_lock():
                    self.pc.value += 4
                
                time.sleep(0.1)  # Simulate clock cycle
                
            except Exception as e:
                print(f"Fetch stage error: {e}")
                break
        
        # Signal fetch completion
        self.fetch_done.set()

    def decode_stage(self):
        """Decode stage process"""
        while not (self.fetch_done.is_set() and self.IF_ID_queue.empty()):
            try:
                # Get instruction from IF/ID queue
                if_id_data = self.IF_ID_queue.get(timeout=0.1)
                inst = if_id_data['instruction']
                
                # Decode instruction
                opcode = int(inst[:6], 2)
                if opcode == 0:
                    decoded_inst = Instruction(type=0, instruction=inst)
                elif opcode in [2, 3]:
                    decoded_inst = Instruction(type=2, instruction=inst)
                else:
                    decoded_inst = Instruction(type=1, instruction=inst)
                
                # Prepare ID/EX data
                id_ex_data = {
                    'instruction': decoded_inst,
                    'PC': if_id_data['PC'],
                    'RD_1': self.registers.read(int(decoded_inst.rs, 2)),
                    'RD_2': self.registers.read(int(decoded_inst.rt, 2))
                }
                
                # Handle immediate value for I-type instructions
                if decoded_inst.type == 1:
                    immediate = int(decoded_inst.immediate, 2)
                    if (immediate & 0x8000):
                        immediate = immediate | 0xFFFF0000
                    id_ex_data['Immediate'] = immediate
                
                # Put decoded data in ID/EX queue
                self.ID_EX_queue.put(id_ex_data)
                print("Decode Stage:", id_ex_data)
                
                time.sleep(0.1)  # Simulate clock cycle
                
            except Empty:
                continue
            except Exception as e:
                print(f"Decode stage error: {e}")
                continue

    def execute_stage(self):
        """Execute stage process"""
        while not (self.fetch_done.is_set() and self.ID_EX_queue.empty()):
            try:
                # Get instruction from ID/EX queue
                id_ex_data = self.ID_EX_queue.get(timeout=0.1)
                inst = id_ex_data['instruction']
                
                ex_mem_data = {'instruction': inst}
                
                # Execute based on instruction type
                if inst.type == 0:  # R-type
                    src1 = id_ex_data['RD_1']
                    src2 = id_ex_data['RD_2']
                    if inst.funct == '001000':  # jr
                        with self.pc.get_lock():
                            self.pc.value = src1
                    elif inst.funct[:3] == "000":  # shift
                        result = self.alu.alu_shift(inst.funct, src1, int(inst.shamt, 2))
                    else:  # arithmetic/logical
                        result = self.alu.alu_arith(inst.funct, src1, src2)
                    ex_mem_data.update({
                        'ALU_result': result,
                        'RegDst': int(inst.rd, 2)
                    })
                
                elif inst.type == 1:  # I-type
                    src1 = id_ex_data['RD_1']
                    imm = id_ex_data['Immediate']
                    if inst.op[:3] == "100":  # load
                        address = self.alu.giveAddr(src1, imm)
                        ex_mem_data.update({
                            'ALU_result': address,
                            'RegDst': int(inst.rt, 2)
                        })
                    elif inst.op[:3] == "101":  # store
                        address = self.alu.giveAddr(src1, imm)
                        ex_mem_data.update({
                            'ALU_result': address,
                            'RD_2': id_ex_data['RD_2']
                        })
                    else:
                        result = self.alu.alu_arith_i(inst.op[3:6], src1, imm)
                        ex_mem_data.update({
                            'ALU_result': result,
                            'RegDst': int(inst.rt, 2)
                        })
                
                elif inst.type == 2:  # J-type
                    addr = int(inst.address, 2)
                    if inst.op[3:] == '000010':  # j
                        with self.pc.get_lock():
                            self.pc.value = (self.pc.value & 0xF0000000) | (addr << 2)
                    elif inst.op[3:] == '000011':  # jal
                        self.registers.write(31, self.pc.value + 4)
                        with self.pc.get_lock():
                            self.pc.value = (self.pc.value & 0xF0000000) | (addr << 2)
                
                # Put executed data in EX/MEM queue
                self.EX_MEM_queue.put(ex_mem_data)
                print("Execute Stage:", ex_mem_data)
                
                time.sleep(0.1)  # Simulate clock cycle
                
            except Empty:
                continue
            except Exception as e:
                print(f"Execute stage error: {e}")
                continue

    def memory_stage(self):
        """Memory stage process"""
        while not (self.fetch_done.is_set() and self.EX_MEM_queue.empty()):
            try:
                # Get instruction from EX/MEM queue
                ex_mem_data = self.EX_MEM_queue.get(timeout=0.1)
                inst = ex_mem_data['instruction']
                
                mem_wb_data = {'instruction': inst}
                
                if inst.type == 1 and inst.op[:3] == "100":  # load
                    address = ex_mem_data['ALU_result']
                    mem_data = "".join(self.memory.load(address + i) for i in range(4))
                    mem_wb_data.update({
                        'Mem_data': mem_data,
                        'RegDst': ex_mem_data['RegDst']
                    })
                
                elif inst.type == 1 and inst.op[:3] == "101":  # store
                    address = ex_mem_data['ALU_result']
                    store_data = ex_mem_data['RD_2']
                    for i in range(4):
                        self.memory.store(store_data[i*8:(i+1)*8], address + i)
                
                else:  # No memory access
                    mem_wb_data.update({
                        'ALU_result': ex_mem_data['ALU_result'],
                        'RegDst': ex_mem_data['RegDst']
                    })
                
                # Put memory stage data in MEM/WB queue
                self.MEM_WB_queue.put(mem_wb_data)
                print("Memory Stage:", mem_wb_data)
                
                time.sleep(0.1)  # Simulate clock cycle
                
            except Empty:
                continue
            except Exception as e:
                print(f"Memory stage error: {e}")
                continue

    def writeback_stage(self):
        """Writeback stage process"""
        while not (self.fetch_done.is_set() and self.MEM_WB_queue.empty()):
            try:
                # Get instruction from MEM/WB queue
                mem_wb_data = self.MEM_WB_queue.get(timeout=0.1)
                inst = mem_wb_data['instruction']
                reg_dst = mem_wb_data['RegDst']
                
                # Write back based on instruction type
                if inst.type == 1 and inst.op[:3] == "100":  # load
                    self.registers.write(reg_dst, mem_wb_data['Mem_data'])
                elif inst.type in [0, 1]:  # R-type or I-type ALU
                    self.registers.write(reg_dst, mem_wb_data['ALU_result'])
                
                print("Write-back Stage:", {
                    'RegDst': reg_dst,
                    'Value': self.registers.read(reg_dst)
                })
                
                time.sleep(0.1)  # Simulate clock cycle
                
            except Empty:
                continue
            except Exception as e:
                print(f"Writeback stage error: {e}")
                continue

    def pipelined(self):
        """Start the pipelined processor with parallel stages"""
        # Create processes for each pipeline stage
        processes = [
            Process(target=self.fetch_stage),
            Process(target=self.decode_stage),
            Process(target=self.execute_stage),
            Process(target=self.memory_stage),
            Process(target=self.writeback_stage)
        ]
        
        # Start all processes
        for p in processes:
            p.start()
        
        # Wait for all processes to complete
        for p in processes:
            p.join()
        
        if self.halt.value:
            print("Processor has halted.")

# # Example usage
# if __name__ == "__main__":
#     file_path = "assets\\binary_2.txt"
#     memory = Memory(initialise=True)
#     alu = ALU()
#     registers = Registers(initialise=True)
#     parse_mips_file(file_path, memory)
#     print(memory.data[:20])
#     mips = MIPSProcessor(memory, alu, registers)
#     mips.pipelined()

if __name__ == "__main__":
    # Enable multiprocessing support for Windows
    # freeze_support()
    
    try:
        # Initialize components
        file_path = "assets\\binary.txt"
        memory = Memory(initialise=True)
        alu = ALU()
        registers = Registers(initialise=True)
        
        # Parse and load MIPS binary file
        print(f"Loading MIPS binary from {file_path}")
        parse_mips_file(file_path, memory)
        
        # Print initial state
        print("\nInitial State:")
        print("PC: 0")
        
        # Create and run pipelined processor
        processor = PipelinedProcessor(memory, alu, registers)
        print("\nStarting pipelined execution...")
        processor.pipelined()
        
        # Print final state
        print("\nFinal State:")
        print(f"PC: {processor.pc.value}")
        
        # Print the first 10 instructions in memory for verification
        print("\nFirst 10 instructions in memory:")
        for addr in range(0, 40, 4):
            instr = ""
            for i in range(4):
                instr += memory.data[addr + i]
            print(f"Address {addr:04x}: {instr}")
        
        # Print final register values for common registers
        print("\nFinal Register Values:")
        common_regs = [0, 2, 4, 8, 29, 31]  # $zero, $v0, $a0, $t0, $sp, $ra
        for reg in common_regs:
            value = registers.read(reg)
            print(f"${reg:02d}: {value}")
            
    except Exception as e:
        print(f"Error during execution: {e}")
        raise