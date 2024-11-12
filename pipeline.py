import multiprocessing
from components.registers import Registers
from components.alu import ALU, signedVal, signedBin
from components.memory import Memory
from components.io import MemoryMappedIO
from instructions import Instruction
from parser import MIPSParser
from hazard import HazardManager
import pandas as pd

class MIPSPipeline:
    def __init__(self, file_path):
        # Initialize components
        self.io = MemoryMappedIO()
        self.memory = Memory(initialise=True)
        self.stall = False
        self.curr_state=['---']*5
        mips_parser = MIPSParser()
        instructions_parsed = mips_parser.parse_mips_file(file_path)
        for insts in instructions_parsed:
            for i in range(4):
                self.memory.store(insts["PC"] + i, insts["IR"][i*8:(i+1)*8])
        self.alu = ALU()
        self.registers = Registers(initialise=True)
        self.PC = multiprocessing.Value('i', 0)  # Shared program counter
        self.pc_lock = multiprocessing.Lock()  # Lock for updating PC
        self.halt = multiprocessing.Value('i', 0)
        # Use Manager to create shared dictionary for pipeline registers
        manager = multiprocessing.Manager()
        self.pipeline_registers = manager.dict({
            'IF_ID': None,
            'ID_EX': None,
            'EX_MEM': None,
            'MEM_WB': None,
        })
        
        # Register and memory locks
        self.register_lock = multiprocessing.Lock()
        self.hazard_manager = HazardManager(self.registers)

        # Synchronization events for pipeline control

        # Use a Manager to create a shared list for register states
        self.register_states = manager.list()
        self.register_states.append(self.registers.reg.copy())

    def fetch_stage(self):
        """Fetches instructions from memory."""
        if self.halt.value == 1:
            return
        with self.pc_lock:
            # Check if PC is within range
            if self.PC.value < len(self.memory.data):
                instruction_data = ""
                for i in range(4):
                    instruction_data += self.memory.load(self.PC.value + i)
                IR = instruction_data
                self.pipeline_registers['IF_ID'] = {'PC': self.PC.value , 'IR': IR}
                print(f"Fetch Stage: Instruction at PC {self.PC.value} fetched")
                self.PC.value += 4
            else:
                self.pipeline_registers['IF_ID'] = None
                return  # Exit when end of instructions is reached
       
            
    
    def decode_stage(self, fetched_data):
        """Decodes instructions and passes them to the execute stage."""
        if fetched_data is not None:
            # Check for end signal
            if fetched_data is None:  # If None is received, break the loop
                self.pipeline_registers['ID_EX'] = None
                return

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

            if self.pipeline_registers['ID_EX']:
                inst_prev = self.pipeline_registers['ID_EX']['Instruction'].get_fields()
                
                if self.hazard_manager.check_data_hazard_stall(fields, inst_prev):
                    self.stall = True
            
            try:
                rs_value = self.registers.read(int(fields['rs'], 2))
            except:
                rs_value = 0
        
            # Prepare the data to send to the ID_EX stage
            id_ex_data = {
                'instruction': inst,
                'PC': fetched_data['PC'],
                'RS': rs_value,
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

            if not inst.type == 2:  # RT for R and I types
                id_ex_data['RT'] = int(fields['rt'], 2)
                decoded_values['RT'] = id_ex_data['RT']
            
            # Add Immediate or Address if they exist
            if 'Immediate' in id_ex_data:
                decoded_values['Immediate'] = id_ex_data['Immediate']
            if 'Address' in id_ex_data:
                decoded_values['Address'] = id_ex_data['Address']

            # Send the decoded values to the ID_EX register
            self.pipeline_registers['ID_EX'] = decoded_values
            print(f"Decode Stage: Instruction decoded with PC {fetched_data['PC']}")
            self.curr_state[1]=f"Instruction decoded with PC {fetched_data['PC']}"
            #self.pipeline_registers['IF_ID'] = None
        else:
            self.pipeline_registers['ID_EX'] = None
            self.curr_state[1]='---'
    
    def execute_stage(self, decoded_data):
        """Executes instructions and updates the EX/MEM pipeline register."""
        if decoded_data is not None:
            

            # Check for end signal
            if decoded_data is None:  # If None is received, break the loop
                self.pipeline_registers['EX_MEM'] = None
                return

            # Retrieve the instruction and type
            inst = decoded_data['Instruction']
            type = inst.type  # Save the type of instruction
            inst = inst.get_fields()  # Get the instruction fields as a dictionary

            result = {'instruction': decoded_data['Instruction']}

            # Check for forwarding needs
            ex_mem_data = self.pipeline_registers['EX_MEM']
            mem_wb_data = self.pipeline_registers['MEM_WB']

            
            # Simulated ALU operations based on instruction type
            if type == 0:  # R-type
                rs = int(inst['rs'], 2)
                rt = int(inst['rt'], 2)
                forward_a, forward_b = self.hazard_manager.check_data_hazard(rs, rt, ex_mem_data, mem_wb_data)
                # Get forwarded values if needed
                src1 = self.hazard_manager.get_forwarded_value(rs, forward_a, ex_mem_data, mem_wb_data)
                src2 = self.hazard_manager.get_forwarded_value(rt, forward_b, ex_mem_data, mem_wb_data)
                if inst['funct'] == '001100':
                    print(f"Execute Stage: Halt condition met for instruction at PC {decoded_data['PC']}")
                    self.curr_state[2]=f"Halt condition met for instruction at PC {decoded_data['PC']}"
                    # Set the halt flag and clear the pipeline
                    self.halt.value = 1
                    self.pipeline_registers["IF_ID"] = None
                    self.pipeline_registers["ID_EX"] = None
                    self.pipeline_registers['EX_MEM'] = None
                    return
                elif inst['funct'] == '001000':  # jr
                    if rs == 31 and src1 == 0:
                        print(f"Execute Stage: Halt condition met for instruction at PC {decoded_data['PC']}")
                        self.curr_state[2]=f"Halt condition met for instruction at PC {decoded_data['PC']}"
                        # Set the halt flag and clear the pipeline
                        self.halt.value = 1
                        self.pipeline_registers["IF_ID"] = None
                        self.pipeline_registers["ID_EX"] = None
                        self.pipeline_registers['EX_MEM'] = None
                        return
                    with self.pc_lock:
                        self.PC.value = src1
                    self.pipeline_registers["IF_ID"] = None
                    self.pipeline_registers["ID_EX"] = None
                    result['ALU_result'] = None
                    result['RD'] = None
                elif inst['funct'][:3] == "000":  # Shift operations
                    result['ALU_result'] = self.alu.alu_shift(inst['funct'], src2, int(inst['shamt'], 2))
                    result['RD'] = int(inst['rd'], 2)
                else:  # Arithmetic/logical operations
                    result['ALU_result'] = self.alu.alu_arith(inst['funct'], src1, src2)
                    result['RD'] = int(inst['rd'], 2)
            
            elif type == 1:  # I-type
                rs = int(inst['rs'], 2)
                rt = int(inst['rt'], 2)
                forward_a, forward_b = self.hazard_manager.check_data_hazard(rs, rt, ex_mem_data, mem_wb_data)
                # Get forwarded values if needed
                src1 = self.hazard_manager.get_forwarded_value(rs, forward_a, ex_mem_data, mem_wb_data)
                src2 = self.hazard_manager.get_forwarded_value(rt, forward_b, ex_mem_data, mem_wb_data)
                imm = decoded_data.get('Immediate', 0)

                if inst['op'][:3] == "100":  # Load
                    result['ALU_result'] = self.alu.giveAddr(src1, imm)
                    result['RD'] = int(inst['rt'], 2)
                elif inst['op'][:3] == "101":  # Store
                    result['ALU_result'] = self.alu.giveAddr(src1, imm)
                    result['RT'] = src2  # Default to 0 if not present
                elif inst['op'][:3] == "000": # beq, bne (Conditional Branch instructions)
                    if (imm & 0x8000): #sign extend
                        imm= imm | 0xFFFF0000
                    a_equal= self.alu.isEqual(src1, src2)
                    b_condition= int(inst["op"][3:],2)==4
                    if (not (a_equal^b_condition)):
                        self.pipeline_registers["IF_ID"] = None
                        self.pipeline_registers["ID_EX"] = None
                        with self.pc_lock:
                            self.PC.value = self.PC.value + (imm<<2) - 4
                    result['ALU_result'] = None
                    result['RD'] = None
                else:  # Arithmetic/logical operations
                    result['ALU_result'] = self.alu.alu_arith_i(inst['op'][3:6], src1, imm)
                    result['RD'] = int(inst['rt'], 2)

            elif type == 2:  # J-type
                addr = int(inst['address'], 2)
                if inst['op'][3:] == '010':
                    with self.pc_lock:
                        self.PC.value = self.PC.value + (addr<<2) - 4
                    self.pipeline_registers["IF_ID"] = None
                    self.pipeline_registers["ID_EX"] = None
                    result['ALU_result'] = None
                    result['RD'] = None
                elif inst['op'][3:] == '011':  # jal (jump and link)
                    result['ALU_result'] = self.PC.value - 4
                    result['RD'] = 31
                    with self.pc_lock:
                        self.PC.value = self.PC.value + (addr<<2) - 4
                    self.pipeline_registers["IF_ID"] = None
                    self.pipeline_registers["ID_EX"] = None
                    
            
            # Put the result in the EX_MEM register
            self.pipeline_registers['EX_MEM'] = result
            print(f"Execute Stage: Executed instruction with result {result}")
            self.curr_state[2]=f"Executed instruction with result: {result}"
            #self.pipeline_registers['ID_EX'] = None
        else:
            self.pipeline_registers['EX_MEM'] = None
            self.curr_state[2]=f"---"

    def memory_access_stage(self, execute_data):
        """Handles memory operations and passes results to write-back stage."""
        if execute_data is not None:
            
            if execute_data is None:  # End signal
                self.pipeline_registers['MEM_WB'] = None
                return
            
            inst = execute_data['instruction']
            type = inst.type  # Save the type of instruction
            inst = inst.get_fields()

            memory_data = {'instruction': execute_data['instruction']}

            if type == 1 and inst['op'][:3] == "100":  # Load instruction
                address = execute_data['ALU_result']
                
                # op[3:6] = 000 | 001 | 011 | 100 | 101
                # load    = lb  | lh  | lw  | lbu | lhu

                match inst['op'][3:6]:
                    case "000": #lb
                        loaded_binary = self.memory.load(address)
                        memory_data['Mem_data'] = signedVal(loaded_binary)
                    case "001": #lh
                        loaded_binary = "".join([self.memory.load(address+i) for i in range(2)])
                        memory_data['Mem_data'] = signedVal(loaded_binary)
                    case "011": #lw
                        loaded_binary = "".join([self.memory.load(address+i) for i in range(4)])
                        memory_data['Mem_data'] = signedVal(loaded_binary)
                    case "100": # lbu
                        loaded_binary = self.memory.load(address)
                        memory_data['Mem_data'] = int(loaded_binary, 2)
                    case "101": #lhu
                        loaded_binary = "".join([self.memory.load(address+i) for i in range(2)])
                        memory_data['Mem_data'] = int(loaded_binary, 2)

                memory_data['RD'] = execute_data['RD']

            elif type == 1 and inst['op'][:3] == "101":  # Store instruction
                mem_addr = execute_data['ALU_result']
                store_data32 = signedBin(execute_data['RT'])
                
                to_output = False
                if (self.io.is_io_address(mem_addr)):
                    to_output = True

                # op[3:6] = 000 | 001 | 011
                # store   = sb  | sh  | sw

                match inst['op'][3:6]:
                    case "000": #sb
                        if (to_output): self.io.io_memory.append(store_data32[24:])
                        self.memory.store(mem_addr, store_data32[24:])
                    case "001": #sh
                        if (to_output): self.io.io_memory.append(store_data32[16:])
                        self.memory.store(mem_addr, store_data32[16:24])
                        self.memory.store(mem_addr + 1, store_data32[24:])
                    case "011": #sw
                        if (to_output): self.io.io_memory.append(store_data32)
                        for i in range(4):
                            self.memory.store(mem_addr + i, store_data32[8*i:8*(i+1)])  
                
                memory_data['RD'] = None
            
            else:  # No memory access, pass ALU result
                memory_data['ALU_result'] = execute_data['ALU_result']
                memory_data['RD'] = execute_data['RD']

            self.pipeline_registers['MEM_WB'] = memory_data
            print(f"Memory Access Stage: Instruction memory access with data {memory_data}")
            self.curr_state[3]=f"Instruction memory access with data {memory_data}"
            #self.pipeline_registers['EX_MEM'] = None
        else:
            self.pipeline_registers['MEM_WB'] = None
            self.curr_state[3]="---"

    def write_back_stage(self, memory_data):
        """Writes data back to registers if necessary."""
        if memory_data is not None:

            inst = memory_data['instruction']
            type = inst.type  # Save the type of instruction
            inst = inst.get_fields()
            reg_dst = memory_data['RD']
            if reg_dst: # if reg_dst is none, branch instruction, no write_back required
                # Perform the write-back operation
                if type == 1 and inst['op'][:3] == "100":  # Load instruction
                    match inst['op'][3:6]:
                        # self.registers.write() method takes register number and 32 bit binary
                        case "000": #lb (signed)
                            self.registers.write(reg_dst, signedBin(memory_data['Mem_data'])) 
                        case "001": #lh (signed)
                            self.registers.write(reg_dst, signedBin(memory_data['Mem_data']))
                        case "011": #lw (full word)
                            self.registers.write(reg_dst, signedBin(memory_data['Mem_data']))
                        case "100": # lbu (unsigned)
                            self.registers.write(reg_dst, format(memory_data['Mem_data'], '032b'))
                        case "101": #lhu (unsigned)
                            self.registers.write(reg_dst, format(memory_data['Mem_data'], '032b'))

                elif (type in [0, 1]) :  # R-type or I-type ALU instruction
                    self.registers.write(reg_dst, signedBin(memory_data['ALU_result']))
                
                elif type == 2 and inst['op'][3:] == '011':
                    self.registers.write(reg_dst, signedBin(memory_data['ALU_result']))

            # Store the register state
            self.register_states.append(self.registers.reg.copy())
            print(f"Write-Back Stage: Write back completed for instruction {memory_data}")
            self.curr_state[4]=f"Write back completed for instruction {memory_data}"
            #self.pipeline_registers['MEM_WB'] = None
        else:
            self.curr_state[4]=f"---"

    def empty_pipeline(self, halt, pipregs):
        if halt.value==0:
            return False
        for val in pipregs.values():
            if val is not None:
                return False
        return True

    def run_pipeline(self):
        """Starts and manages pipeline stages as parallel processes."""
        cycle = 1
        columns = ["fetch", "decode", "execute", "memory_access", "writeBack"]
        cycle_states=pd.DataFrame(columns=columns)
        cycle_states.loc['Initial State']=self.curr_state
        while not self.empty_pipeline(self.halt, self.pipeline_registers):
            print("Cycle ", cycle)
            # Get the data from pipeline registers
            
            fetched_data = self.pipeline_registers["IF_ID"]
            decoded_data = self.pipeline_registers["ID_EX"] 
            execute_data = self.pipeline_registers["EX_MEM"]
            memory_data = self.pipeline_registers["MEM_WB"]
            stall = self.stall
            
            self.curr_state[0]=f"Instruction at PC {self.PC.value} fetched"
            
            # Initialize processes for each stage
            if not stall:
                fetch_process = multiprocessing.Process(target=self.fetch_stage)
                decode_process = multiprocessing.Process(target=self.decode_stage(fetched_data))
                execute_process = multiprocessing.Process(target=self.execute_stage(decoded_data))
            mem_access_process = multiprocessing.Process(target=self.memory_access_stage(execute_data))
            write_back_process = multiprocessing.Process(target=self.write_back_stage(memory_data))
            # Start all processes
            if not stall:
                fetch_process.start()
                decode_process.start()
                execute_process.start()
            mem_access_process.start()
            write_back_process.start()

            # Join all processes
            if not stall:
                fetch_process.join()
                decode_process.join()
                execute_process.join()
            mem_access_process.join()
            write_back_process.join()
            if (self.halt.value==1):
                self.curr_state[0]='---'
            cycle_states.loc[f"Cycle {cycle}"]= self.curr_state
            
            if stall == True:
                self.stall = False
                self.pipeline_registers["EX_MEM"] = None
            cycle += 1

        # Display the final state of registers
        print("Final Register States:")
        # Display the tracked register states after each instruction
        print("-----------------------------")
        print("Tracked Register States After Each Instruction:")
        allRegNames = ["$0", "$at", "$v0", "$v1", "$a0", "$a1", "$a2", "$a3", "$t0", "$t1", "$t2", "$t3", "$t4", "$t5", "$t6", "$t7", "$s0", "$s1", "$s2", "$s3", "$s4", "$s5", "$s6", "$s7", "$t8", "$t9", "$k0", "$k1", "$gp", "$sp", "$fp", "$ra"]
        for i, state in enumerate(self.register_states):
            allRegValues = [signedVal(val) for val in state]
            if i==0:
                print("Initial Values:")
            else: 
                print(f"Instruction {i}:")
            for j in range(32):
                print(f"{allRegNames[j]}: {allRegValues[j]}")
            print() 
        print("-----------------------------")

        return self.register_states, self.io.io_memory,cycle_states

if __name__ == "__main__":
    mips_pipeline = MIPSPipeline(file_path="tests/lh_lbu_test.txt")
    mips_pipeline.run_pipeline()