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

        self.IF_ID = {
            'PC': None,
            'instruction': None,
            'valid': False
        }

        self.ID_EX = {
            'instruction': None, #of class type instruction
            'valid': False,
            'RD_1':None,
            'RD_2':None,
            'Immediate':None,
            'PC':None
        }


    def fetch(self):
        pass
    def decode (self):
        pass
    def execute(self):
        pass
    def dmem(self):
        pass
    def write_back(self):
        pass
    def pipelined(self):
        pass

if __name__=="__main__":
    file_path="assets\\binary.txt"
    # Step 1 ---------------------------------------
    memory = Memory()
    alu = ALU()
    registers = Registers()
    parse_mips_file(file_path,memory)
    print(memory.data)
    

    pass
