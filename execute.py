def signedVal(binStr):
    isSigned = int(binStr[0]=="1")
    return int(binStr, 2) - isSigned*(2**len(binStr))

def signedBin(num):
    # return 2's complement binary string of length len
    ans=""
    if(num<0):
        ans = bin(num % (1<<32))[2:]
    else:
        ans = format(num, '032b')
    return ans

class Execute:
    def __init__(self, memory, registers, alu):
        self.memory = memory
        self.registers = registers
        self.alu = alu

    # execute the sent instruction (inst object)
    def executeInst(self, inst):
        match inst.type:
            case 0:
                # handle R-type inst (e.g. using ALU)
                # op, rs, rt, rd, shamt, funct
                """
                    nor,            (nor=100111) 
                    sll, srl,       (sll=000000, srl=000010)
                    sltu,           (sltu=101011)
                    jr              (jr=001000)
                """
                if inst.rs == 0:
                    opr1 = self.registers.reg[inst.rt]
                    ans = self.alu.alu_shift(inst.funct, opr1, inst.shamt)
                    self.registers.reg[inst.rd] = ans
                else:
                    opr1 = self.registers.reg[inst.rs]
                    opr2 = self.registers.reg[inst.rt]
                    ans = self.alu.alu_arith(inst.funct, opr1, opr2)
            case 2|3:
                # handle J-type inst 
                """
                    j, jal (pseudodirect addressing, updating PC)
                """
                pass
            case _:
                # handle I-type inst
                """
                    addi,
                    beq, bne,
                    slti, sltiu
                    lw, sw,
                    lh, lhu,
                    lb, lbu,
                    sh, sb,
                    lui, 
                    ori, andi,
                """
                match inst.op:
                    case 0b001000:
                        # addi
                        src = self.registers.reg[inst.rs]
                        ans = src + inst.immediate
                        self.registers.reg[inst.rt] = ans
                    case 0b001010:
                        # slti
                        src = self.registers.reg[inst.rs]
                        imm = signedVal(inst.immediate)
                        ans = 1 if src < imm else 0
                        self.registers.reg[inst.rt] = ans
                    case 0b001011:
                        # sltiu
                        src = self.registers.reg[inst.rs]
                        ans = 1 if src < inst.immediate else 0
                        self.registers.reg[inst.rt] = ans
                    case 0b001100:
                        # andi
                        src = self.registers.reg[inst.rs]
                        ans = src & inst.immediate
                        self.registers.reg[inst.rt] = ans
                    case 0b001101:
                        # ori
                        src = self.registers.reg[inst.rs]
                        ans = src | inst.immediate
                        self.registers.reg[inst.rt] = ans
                    case 0b001110:
                        # xori
                        src = self.registers.reg[inst.rs]
                        ans = src ^ inst.immediate
                        self.registers.reg[inst.rt] = ans
                    case 0b001111:
                        # lui
                        ans = inst.immediate << 16
                        self.registers.reg[inst.rt] = ans
                pass

# -------------------------------------------------------
