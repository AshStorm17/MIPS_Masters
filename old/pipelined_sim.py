from components.registers import Registers
from components.alu import ALU
from components.memory import Memory
from instructions import RtypeInst, ItypeInst, JtypeInst, giveFields
from execute import Execute
from parser import *

file_path = "assets\\binary.txt"

# Step 1: Instantiate components
memory = Memory()
alu = ALU()
registers = Registers()
PC = 0 

# Intermediate pipeline registers (one for each pipeline stage)
IF_ID = {'PC': 0, 'IR': ''}
ID_EX = {'fields': None, 'inst_type': None}
EX_MEM = {'ALU_result': 0, 'dest_reg': None}
MEM_WB = {'mem_data': 0, 'ALU_result': 0, 'dest_reg': None}

# Initialize execute handler
execute = Execute(memory, registers, alu, PC)

# Step 2: Parse and load instructions into memory
parse_mips_file(file_path, memory)

# Step 3: Begin reverse loop pipeline processing
while PC < len(memory.data):
    # Reverse order processing: WB -> MEM -> EX -> ID -> IF

    # Stage 5: Write Back (WB)
    if MEM_WB['dest_reg'] is not None:
        registers.write(MEM_WB['dest_reg'], MEM_WB['mem_data'] if MEM_WB['mem_data'] else MEM_WB['ALU_result'])
    
    # Stage 4: Memory Access (MEM)
    if EX_MEM['dest_reg'] is not None:
        if EX_MEM['inst_type'] == "load":
            MEM_WB['mem_data'] = memory.load(EX_MEM['ALU_result'])
        elif EX_MEM['inst_type'] == "store":
            memory.store(EX_MEM['ALU_result'], registers.read(EX_MEM['dest_reg']))
        else:
            MEM_WB['ALU_result'] = EX_MEM['ALU_result']
        MEM_WB['dest_reg'] = EX_MEM['dest_reg']
    
    # Stage 3: Execute (EX)
    if ID_EX['fields'] is not None:
        result, dest_reg, inst_type = execute.executeInst(ID_EX['inst_type'], *ID_EX['fields'])
        EX_MEM['ALU_result'] = result
        EX_MEM['dest_reg'] = dest_reg
        EX_MEM['inst_type'] = inst_type
    
    # Stage 2: Decode (ID)
    if IF_ID['IR']:
        opcode = int(IF_ID['IR'][0:7], 2)
        if opcode == 0:
            fields = giveFields(IF_ID['IR'], 0)  # R-type instruction
            ID_EX['inst_type'] = RtypeInst
        elif opcode in [2, 3]:
            fields = giveFields(IF_ID['IR'], 2)  # J-type instruction
            ID_EX['inst_type'] = JtypeInst
        else:
            fields = giveFields(IF_ID['IR'], 1)  # I-type instruction
            ID_EX['inst_type'] = ItypeInst
        ID_EX['fields'] = fields
    
    # Stage 1: Fetch (IF)
    if PC < len(memory.data) - 4:
        IF_ID['IR'] = ''.join(memory.data[PC:PC + 4])  # Fetch 32-bit instruction
        IF_ID['PC'] = PC
        PC += 4
    
    # Reset intermediate registers if no new instruction was loaded (pipeline flush scenario)
    if PC >= len(memory.data):
        IF_ID = {'PC': 0, 'IR': ''}
    
