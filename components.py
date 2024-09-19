# --------------------------------------------
class Registers:
    def __init__(self):
        self.reg = [""] * 32 # 32 registers

    def write(self, number, value):
        self.reg[number] = value
    
    def read(self, number):
        return self.reg[number]
# --------------------------------------------
# memory class
    # byte addressing
    # separate spaces for instructions, data, I/O
class Memory:
    def __init__(self):
        self.data = [""]*4*1024 # 1024 words

    def store(self, addr, value):
        self.data[addr] = value

    def load(self, addr):
        return self.data[addr]
    
    # function for I/O access

# -------------------------------------------
# ALU class and operations
def signedVal(binStr):
    isSigned = int(binStr[0]=="1")
    return int(binStr, 2) - isSigned*(2**len(binStr))

def signedBin(num, len):
    # return 2's complement binary string of length len
    ans=""
    if(num<0):
        pass
    else:
        pass
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
                # signed or unsigned?
                num1 = signedVal(opr1)
                num2 = signedVal(opr2)
                ans = signedBin(num1 + num2, 32)
                pass
            case "100010": # sub
                pass
            case "100100": # and
                pass
            case "100101": # or
                pass
            case "101010": #slt
                pass
        
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
