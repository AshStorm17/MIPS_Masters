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
                # handle R-type inst
                """
                    jr (jr=001000)
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
                    # case 0b001110:
                    #     # xori
                    #     src = self.registers.reg[inst.rs]
                    #     ans = src ^ inst.immediate
                    #     self.registers.reg[inst.rt] = ans
                    case 0b001111:
                        # lui
                        ans = inst.immediate << 16
                        self.registers.reg[inst.rt] = ans
                pass

# -------------------------------------------------------
