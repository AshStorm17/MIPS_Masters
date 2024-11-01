from components.alu import ALU
from components.memory import Memory
from components.registers import Registers
from instructions import Instruction
from parser import parse_mips_file
from execute import execute_instruction
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
        # print(self.ID_EX['instruction'])
        # print(format(self.ID_EX['Immediate'],'032b'))
    
    def execute(self):
        inst = self.ID_EX['instruction']
        match inst.type:
            case 0:
                
                pass
            case 2 | 3:
                pass
            case _:
                pass
    
    def mem(self):
        pass
    def write_back(self):
        pass
    def pipelined(self):
        self.fetch()
        self.decode()
        # self.execute()
        

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


    pass