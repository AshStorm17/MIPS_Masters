"""
1. Instantiate memory, ALU, Registers, execute
2. Load/Parse the instruction file into the memory
3. Define & point PC to the 1st instruction; instantiate IR
4. Begin Fetch-Decode-Execute cycle:
    1. Fetch into IR
    2. Decode (get the fields)
    3. Pass to the execution engine
"""

from components import Memory, ALU, Registers
from instructions import RtypeInst, ItypeInst, JtypeInst, giveFields
from execute import Execute
from parser import *

file_path="assets\\binary.txt"
# Step 1 ---------------------------------------
memory = Memory()
alu = ALU()
registers = Registers()
execute = Execute(memory, registers, alu)

# Step 2 ---------------------------------------
# @ BG
parse_mips_file(file_path,memory)

print(memory.data)
# Step 3 ---------------------------------------
PC = memory.data[0] 
IR = ""

# Step 4 ---------------------------------------
while memory.data[PC]!=0:
    # Step 4.1: 
    for i in range(4):
        IR += memory.data[PC+i] 
    
    # Step 4.2 (decode)
    match int(IR[0:7], 2):
        case 0:
            fields = giveFields(IR, 0) # R-type instruction 
            inst = RtypeInst(*fields)
        case 2 | 3:
            fields = giveFields(IR, 2) # J-type instruction
            inst = ItypeInst(*fields)
        case _:
            fields = giveFields(IR, 1) # I-type instruction
            inst = JtypeInst(*fields)
    
    # Step 4.3 (execute)
    execute.executeInst(inst)
    
    
    # Reset IR and move PC to the next instruction
    IR = ""    
    PC += 4 

# ---------------------------------------
