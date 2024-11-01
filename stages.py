from components.alu import ALU
from components.memory import Memory
from components.registers import Registers
from instructions import Instruction
from parser import parse_mips_file
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
            # 'RD_1':None,
            # 'RD_2':None,
            # 'Immediate':None,
            'PC':None
        }


    def fetch(self):
        pass
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
        print(self.ID_EX)
    
    def execute(self):
        pass
    def dmem(self):
        pass
    def write_back(self):
        pass
    def pipelined(self):
        pass

if __name__=="__main__":
    file_path="assets\\binary_2.txt"
    # Step 1 ---------------------------------------
    memory = Memory(initialise=True)
    alu = ALU()
    registers = Registers(initialise=True)
    parse_mips_file(file_path,memory)
    print(memory.data[:20])
    mips=MIPSProcessor(mem=memory,alu=ALU,reg=registers)


    pass
