# from components.alu import ALU
# from components.memory import Memory
# from components.registers import Registers
# from parser import parse_mips_file
# from instructions import Instruction
class Execute:
    def __init__(self, memory, registers, alu,pc):
        self.memory = memory
        self.registers = registers
        self.alu = alu
        self.pc=pc

    # execute the sent instruction (inst object)
    def executeInst(self, inst):
        match inst.type:
            case 0:
                # handle R-type inst
                """
                    jr (jr=001000)
                """
                src_reg = int(inst.rs, 2)
                temp_reg = int(inst.rt, 2)

                if inst.funct=="001000": #handle jr instruction
                    self.pc=src_reg
                elif inst.funct[0:3] == "000":
                    opr1 = self.registers.read(src_reg)
                    ans = self.alu.alu_shift(inst.funct, opr1, inst.shamt)
                else:
                    opr1 = self.registers.read(src_reg)
                    opr2 = self.registers.read(temp_reg)
                    ans = self.alu.alu_arith(inst.funct, opr1, opr2)
                dst_reg = int(inst.rd, 2)
                self.registers.write(dst_reg, ans)
            case 2|3:
                # handle J-type inst 
                """
                    j, jal (pseudodirect addressing, updating PC)
                """
                addr=int(inst.address,2)
                if (int(inst.op[3:],2)==2): #jump code
                    self.pc= (self.pc & 0xF0000000) | (addr<<2)
                else: #jump and link
                    self.registers.write(31,self.pc+4) #write to return address
                    self.pc= (self.pc & 0xF0000000) | (addr<<2)

            case _:
                # handle I-type inst
                """
                    beq, bne,
                """
                match inst.op[0:3]:
                    case "100": # load instructions
                        # op, rs, rt, offset
                        addr = int(self.alu.giveAddr(inst.rs, inst.addrORimm),2)
                        op2ndHalf = int(inst.op[3:6],2)
                        i_range = op2ndHalf % 4
                        loadedStr = ""
                        for i in range(i_range):
                            loadedStr += self.memory.load(addr+i)
                        regNo = int(inst.rt, 2)
                        signExtAmt = (4-(i_range+1)) * 8
                        # 0,1,3 => signed, # 4,5 => unsigned
                        if(op2ndHalf<4):
                            loadedStr = (loadedStr[0]*signExtAmt) + loadedStr
                        else:
                            loadedStr = ("0"*signExtAmt) + loadedStr
                        self.registers.write(regNo, loadedStr)

                    case "101": # store instructions
                        addr = int(self.alu.giveAddr(inst.rs, inst.addrORimm),2)
                        op2ndHalf = int(inst.op[3:6],2)
                        i_range = op2ndHalf
                        regNo = int(inst.rt, 2)
                        storeStr = self.registers.read(regNo)
                        for i in range(24,24-(op2ndHalf*8)-1,-8):
                            self.memory.store(storeStr[i:i+8],addr+(24-i)/8)

                    case "001": # remaining IType
                        src_reg = int(inst.rs, 2)
                        src = self.registers.read(src_reg)
                        ans = self.alu.alu_arith_i(inst.op[3:6], src, inst.addrORimm)
                        dst_reg = int(inst.rt, 2)
                        self.registers.write(dst_reg, ans)
                    case "000": #branching instructions
                        src_reg=int(inst.rs,2)
                        dst_reg=int(inst.rt,2)
                        src_val=self.registers.read(src_reg)
                        dst_val=self.registers.read(dst_reg)
                        imm=int(inst.addrORimm,2)
                        if (imm & 0x8000): #sign extend
                            imm= imm | 0xFFFF0000
                        a_equal= self.alu.isEqual(src_val,dst_val)
                        b_condition= int(inst.op[3:],2)==4
                        if (~(a_equal^b_condition)):
                            self.pc=self.pc+ 4+ imm<<2
                        

def execute_instruction(memory, registers, alu, pc, inst):
    # Execute the sent instruction (inst object)

    match inst.type:
        case 0:
            # Handle R-type instruction
            src_reg = int(inst.rs, 2)
            temp_reg = int(inst.rt, 2)

            if inst.funct == "001000":  # Handle jr instruction
                pc = registers.read(src_reg)  # Update PC to the source register value
            elif inst.funct[0:3] == "000":  # Shift instructions
                opr1 = registers.read(src_reg)
                ans = alu.alu_shift(inst.funct, opr1, inst.shamt)
            else:
                opr1 = registers.read(src_reg)
                opr2 = registers.read(temp_reg)
                ans = alu.alu_arith(inst.funct, opr1, opr2)

            dst_reg = int(inst.rd, 2)
            registers.write(dst_reg, ans)

        case 2 | 3:
            # Handle J-type instruction
            addr = int(inst.address, 2)

            if int(inst.op[3:], 2) == 2:  # Jump (j)
                pc = (pc & 0xF0000000) | (addr << 2)
            else:  # Jump and link (jal)
                registers.write(31, pc + 4)  # Write return address
                pc = (pc & 0xF0000000) | (addr << 2)

        case _:
            # Handle I-type instruction
            match inst.op[0:3]:
                case "100":  # Load instructions
                    addr = int(alu.giveAddr(inst.rs, inst.addrORimm), 2)
                    op2ndHalf = int(inst.op[3:6], 2)
                    i_range = op2ndHalf % 4
                    loadedStr = ""

                    for i in range(i_range):
                        loadedStr += memory.load(addr + i)

                    regNo = int(inst.rt, 2)
                    signExtAmt = (4 - (i_range + 1)) * 8

                    # 0,1,3 => signed, 4,5 => unsigned
                    if op2ndHalf < 4:
                        loadedStr = (loadedStr[0] * signExtAmt) + loadedStr
                    else:
                        loadedStr = ("0" * signExtAmt) + loadedStr

                    registers.write(regNo, loadedStr)

                case "101":  # Store instructions
                    addr = int(alu.giveAddr(inst.rs, inst.addrORimm), 2)
                    op2ndHalf = int(inst.op[3:6], 2)
                    i_range = op2ndHalf
                    regNo = int(inst.rt, 2)
                    storeStr = registers.read(regNo)

                    for i in range(24, 24 - (op2ndHalf * 8) - 1, -8):
                        memory.store(storeStr[i:i + 8], addr + (24 - i) // 8)

                case "001":  # Remaining I-type
                    src_reg = int(inst.rs, 2)
                    src = registers.read(src_reg)
                    ans = alu.alu_arith_i(inst.op[3:6], src, inst.addrORimm)
                    dst_reg = int(inst.rt, 2)
                    registers.write(dst_reg, ans)

                case "000":  # Branching instructions
                    src_reg = int(inst.rs, 2)
                    dst_reg = int(inst.rt, 2)
                    src_val = registers.read(src_reg)
                    dst_val = registers.read(dst_reg)
                    imm = int(inst.addrORimm, 2)

                    if imm & 0x8000:  # Sign extend
                        imm = imm | 0xFFFF0000

                    a_equal = alu.isEqual(src_val, dst_val)
                    b_condition = int(inst.op[3:], 2) == 4

                    if ~(a_equal ^ b_condition):
                        pc += 4 + (imm << 2)

    return pc  # Return updated PC after instruction execution

# -------------------------------------------------------
# if __name__=='__main__':
#     memory = Memory()
#     registers = Registers()
#     alu = ALU()
#     pc = 0
#     execute = Execute(memory, registers, alu, pc)
#     parse_mips_file('assets\\binary.txt',memory)
#      # Test R-type instruction (add)
#     r_inst = Instruction(
#         type=0,
#         instruction='00000010001100100100100000100000'
#     )
    
#     # # Test I-type instruction (addi)
#     # i_inst = Instruction(
#     #     type=1,
#     #     op="001000",  # addi
#     #     rs="00001",  # r1
#     #     rt="00100",  # r4
#     #     addrORimm="0000000000000001"  # immediate value 1
#     # )
    
#     # # Test J-type instruction (jump)
#     # j_inst = Instruction(
#     #     type=2,
#     #     op="000010",  # j
#     #     address="00000000000000000000000001"  # jump target
#     # )
    
#     # Execute instructions
#     print("Testing R-type instruction...")
#     execute.executeInst(r_inst)
#     print(f"Register 3 value after add: {registers.read(3)}")
    
#     # print("\nTesting I-type instruction...")
#     # execute.executeInst(i_inst)
#     # print(f"Register 4 value after addi: {registers.read(4)}")
    
#     # print("\nTesting J-type instruction...")
#     # old_pc = execute.pc
#     # execute.executeInst(j_inst)
#     # print(f"PC changed from {old_pc} to {execute.pc}")