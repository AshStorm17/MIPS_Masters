# --------------------------------------------
class Registers:
    def __init__(self):
        self.reg = [""] * 32 # 32 registers

    def write(self, number, value):
        self.reg[number] = value
    
    def read(self, number):
        return self.reg[number]
# --------------------------------------------
# Memory class
    # byte addressing
    # separate spaces for instructions, data, I/O
class Memory:
    def __init__(self):
        self.data = ["00000000"]*4*1024 # 1024 words

    def store(self, addr, value):
        self.data[addr] = value

    def store32bit_instr(self,instr,curraddr):
        self.data[curraddr]=instr[:8]
        self.data[curraddr+1]=instr[8:16]
        self.data[curraddr+2]=instr[16:24]
        self.data[curraddr+3]=instr[24:32]

    def load(self, addr):
        return self.data[addr]
    
    # function for I/O access
    def fillOutput(self):
        pass

# -------------------------------------------
# ALU class and operations
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
# ---------------------------
class ALU:
    def __init__(self):
        pass

    def alu_arith(self, operation, opr1, opr2):
        """
        COAHP: For the R-type instructions, the ALU needs to perform one of the five actions (AND, OR, subtract, add, or set on less than
        """
        # Note: return binary string as answer
        ans = ""
        match operation:
            case "100000": # add
                ans = signedBin(signedVal(opr1) + signedVal(opr2))
                pass
            case "100010": # sub
                ans = signedBin(signedVal(opr1) - signedVal(opr2))
            case "100100": # and
                ans = signedVal(opr1) & signedVal(opr2)
            case "100101": # or
                ans = signedVal(opr1) | signedVal(opr2)
            case "101010": #slt 
                # compare and return 1 or 0
                return int(signedVal(opr1) < signedVal(opr2))
        
        return ans

    def giveAddr(self, baseAddr, lower16bits):
        """
        COAHP: For load word and store word instructions, 
        we use the ALU to compute the memory address by addition.
        The ALU computes the sum of the value read from the register file and the
        sign-extended, lower 16 bits of the instruction (offset).
        """
        offset = signedVal(lower16bits)
        baseAddrVal = int(baseAddr, 2)
        return format(baseAddrVal+offset, '032b') # assumed final address not -ve
    
    def isEqual(self, bin1, bin2): # comparison for bne, beq
        """
        COAHP: For branch equal, the ALU must perform a subtraction.
        """
        return bin1==bin2 # directly compare the two 32-bit binary strings


# --------------------------------------------
