from components.alu import ALU
from components.memory import Memory
from components.registers import Registers
from instructions import Instruction
from parser_old import parse_mips_file

class MIPSProcessor:
    def __init__(self,mem,alu,reg):
        self.memory = mem
        self.alu = alu
        self.registers = reg
        self.pc=0
        self.IF_ID = {
            'PC': None,
            'instruction': None,
            'valid': False
        }

        self.ID_EX = {
            'instruction': None, #of class type instruction
            # 'valid': False,
            'RD_1':None,
            'RD_2':None,
            'Immediate':None,
            'PC':None,
            'RegWrite':None,
        }
        self.EX_MEM = {
            'ALU_result': None,
            'RD_2': None,
            'PC': None,
            'RegWrite':None
        }

        self.MEM_WB={

        }

    def fetch(self):
        instr = ""
        for i in range(4):
            instr += self.memory.data[self.pc + i]  
        self.IF_ID['instruction'] = instr
        self.IF_ID['PC'] = format(self.pc + 4, '032b')

    def decode (self):
        inst=self.IF_ID['instruction']
        opcode=int (inst[:6],2)
        if opcode==0:
            inst=Instruction(type=0,instruction=inst)
        elif opcode in [2,3]:
            inst=Instruction(type=2,instruction=inst)
        else:
            inst=Instruction(type=1,instruction=inst)
        
        self.ID_EX['instruction']=inst
        self.ID_EX['PC']=self.pc
        self.ID_EX['RD_1']=self.registers.read(int(inst.rs,2))
        self.ID_EX['RD_2']=self.registers.read(int(inst.rt,2))
        imm=int(inst.immediate,2)
        if (imm & 0x8000): #sign extend
            imm= imm | 0xFFFF0000
        self.ID_EX['Immediate']=imm
        self.ID_EX['RegWrite']=inst.rd
        print(self.ID_EX['instruction'])
        print(format(self.ID_EX['Immediate'],'032b'))
    
    def execute(self):
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
        print("Execute Stage:", {key: value for key, value in self.EX_MEM.items()})

    def dmem(self):
        pass
    def write_back(self):
        pass
    def pipelined(self):
        self.fetch()
        self.decode()
        self.execute()
if __name__=="__main__":
    file_path="assets\\binary_2.txt"
    # Step 1 ---------------------------------------
    memory = Memory(initialise=True)
    alu = ALU()
    registers = Registers(initialise=True)
    parse_mips_file(file_path,memory)
    print(memory.data[:20])
    mips = MIPSProcessor(memory, alu, registers)
    mips.pipelined()

