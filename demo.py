import multiprocessing
from components.registers import Registers
from components.alu import ALU, signedVal, signedBin
from components.memory import Memory
from instructions import Instruction
from parser import MIPSParser
from hazard import HazardManager

from pipeline import MIPSPipeline

from utils.assembler import MIPSAssembler

if __name__=="__main__":
    assembler = MIPSAssembler()
    test_instructions = assembler.parse_asm("assets\mipsasm_1.asm")
    machine_codes = assembler.assemble_binary(test_instructions)
    save=True
    file_path="assets\\binary_2.txt"
    if (save):
        #write machine code to text file   
        with open(file_path, 'w') as file:
                for code in machine_codes:
                    file.write(f"{code}\n")
        print(f"\nMachine code successfully written to {file_path}")
    mips_pipeline=MIPSPipeline(file_path)
    mips_pipeline.run_pipeline()
