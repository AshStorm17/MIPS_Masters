from components.alu import ALU
from components.memory import Memory
from components.registers import Registers
from instructions import Instruction
from parser_old import parse_mips_file

class MIPSProcessor:
    def __init__(self, mem, alu, reg):
        self.memory = mem
        self.alu = alu
        self.registers = reg
        self.pc = 0
        
        # Pipeline registers
        self.IF_ID = {'PC': None, 'instruction': None, 'valid': False}
        self.ID_EX = {'instruction': None, 'RD_1': None, 'RD_2': None, 'Immediate': None, 'PC': None}
        self.EX_MEM = {'ALU_result': None, 'RD_2': None, 'RegDst': None, 'instruction': None}
        self.MEM_WB = {'ALU_result': None, 'Mem_data': None, 'RegDst': None, 'instruction': None}
    def fetch(self):
        # Fetches an instruction from memory at PC
        instr = ""
        for i in range(4):
            instr += self.memory.data[self.pc + i]  
        self.IF_ID['instruction'] = instr
        self.IF_ID['PC'] = format(self.pc + 4, '032b')
        self.pc += 4

    def decode(self):
        # Decodes instruction in IF/ID and sets up ID/EX pipeline register
        inst = self.IF_ID['instruction']
        opcode = int(inst[:6], 2)
        
        if opcode == 0:
            inst = Instruction(type=0, instruction=inst)
        elif opcode in [2, 3]:
            inst = Instruction(type=2, instruction=inst)
        else:
            inst = Instruction(type=1, instruction=inst)
        
        self.ID_EX['instruction'] = inst
        self.ID_EX['PC'] = self.pc
        self.ID_EX['RD_1'] = self.registers.read(int(inst.rs, 2))
        self.ID_EX['RD_2'] = self.registers.read(int(inst.rt, 2))
        if inst.type == 1:
            immediate = int(inst.immediate, 2)
            if (immediate & 0x8000):  # Sign extend if negative
                immediate = immediate | 0xFFFF0000
            self.ID_EX['Immediate'] = immediate
        print("Decode Stage:", self.ID_EX)

    def execute(self):
        # Executes the instruction in ID/EX and updates EX/MEM pipeline register
        inst = self.ID_EX['instruction']
        
        if inst.type == 0:  # R-type
            src1 = self.ID_EX['RD_1']
            src2 = self.ID_EX['RD_2']
            if inst.funct == '001000':  # jr
                self.pc = src1
            elif inst.funct[:3] == "000":  # shift operations
                result = self.alu.alu_shift(inst.funct, src1, int(inst.shamt, 2))
            else:  # arithmetic/logical operations
                result = self.alu.alu_arith(inst.funct, src1, src2)
            dst_reg = int(inst.rd, 2)
            self.EX_MEM['ALU_result'] = result
            self.EX_MEM['RegDst'] = dst_reg
        
        elif inst.type == 1:  # I-type
            src1 = self.ID_EX['RD_1']
            imm = self.ID_EX['Immediate']
            if inst.op[:3] == "100":  # load
                address = self.alu.giveAddr(src1, imm)
                self.EX_MEM['ALU_result'] = address
                self.EX_MEM['RegDst'] = int(inst.rt, 2)
            elif inst.op[:3] == "101":  # store
                address = self.alu.giveAddr(src1, imm)
                self.EX_MEM['ALU_result'] = address
                self.EX_MEM['RD_2'] = self.ID_EX['RD_2']
            else:
                result = self.alu.alu_arith_i(inst.op[3:6], src1, imm)
                self.EX_MEM['ALU_result'] = result
                self.EX_MEM['RegDst'] = int(inst.rt, 2)
        
        elif inst.type == 2:  # J-type
            addr = int(inst.address, 2)
            if inst.op[3:] == '000010':  # j instruction
                self.pc = (self.pc & 0xF0000000) | (addr << 2)
            elif inst.op[3:] == '000011':  # jal instruction
                self.registers.write(31, self.pc + 4)  # Write to return address
                self.pc = (self.pc & 0xF0000000) | (addr << 2)
        
        self.EX_MEM['instruction'] = inst
        print("Execute Stage:", self.EX_MEM)

    def mem(self):
        # Memory stage for EX/MEM pipeline register, updating MEM/WB
        inst = self.EX_MEM['instruction']
        
        if inst.type == 1 and inst.op[:3] == "100":  # load instruction
            address = self.EX_MEM['ALU_result']
            mem_data = "".join(self.memory.load(address + i) for i in range(4))
            self.MEM_WB['Mem_data'] = mem_data
            self.MEM_WB['RegDst'] = self.EX_MEM['RegDst']
        
        elif inst.type == 1 and inst.op[:3] == "101":  # store instruction
            address = self.EX_MEM['ALU_result']
            store_data = self.EX_MEM['RD_2']
            for i in range(4):
                self.memory.store(store_data[i*8:(i+1)*8], address + i)
        
        else:  # No memory access
            self.MEM_WB['ALU_result'] = self.EX_MEM['ALU_result']
            self.MEM_WB['RegDst'] = self.EX_MEM['RegDst']
        
        self.MEM_WB['instruction'] = inst
        print("Memory Stage:", self.MEM_WB)

    def write_back(self):
        # Write-back stage for MEM/WB pipeline register
        inst = self.MEM_WB['instruction']
        reg_dst = self.MEM_WB['RegDst']
        
        if inst.type == 1 and inst.op[:3] == "100":  # load instruction
            self.registers.write(reg_dst, self.MEM_WB['Mem_data'])
        elif inst.type in [0, 1]:  # R-type or I-type ALU instruction
            self.registers.write(reg_dst, self.MEM_WB['ALU_result'])
        
        print("Write-back Stage:", {'RegDst': reg_dst, 'Value': self.registers.read(reg_dst)})

    def pipelined(self):
        # Simulates one clock cycle of the pipeline
        
        self.fetch()
        self.decode()
        self.execute()
        self.mem()

        self.write_back()

# Example usage
if __name__ == "__main__":
    file_path = "assets\\binary.txt"
    memory = Memory(initialise=True)
    alu = ALU()
    registers = Registers(initialise=True)
    parse_mips_file(file_path, memory)
    print(memory.data[:20])
    mips = MIPSProcessor(memory, alu, registers)
    mips.pipelined()
